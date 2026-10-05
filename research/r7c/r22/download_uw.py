"""Selectively download the three metadata-fixed UW records; never process signals.

Uses only the public frozen UW_SOURCE_MANIFEST.json and bounded HTTP ranges;
the original full ZIP catalog or private review folder is not required. Resuming
and extraction verify source CRC and SHA256. The frozen registry is never written.
"""
from __future__ import annotations
import argparse, concurrent.futures, datetime, hashlib, json, pathlib, struct, time
import urllib.request, zlib

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / 'UW_SOURCE_MANIFEST.json'
FREEZE = HERE / 'UW_FREEZE.json'
DATA = HERE.parent / 'data/UW_R22'
RECORDS = tuple(f'2019_04_09_pms{x}000' for x in (1, 2, 3))
MAX_REQUEST = 8_000_000

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local_path(entry):
    parts = pathlib.PurePosixPath(entry['name']).parts
    if len(parts) != 4 or parts[0] != 'Automotive' or parts[1] not in RECORDS:
        raise ValueError('Unexpected archive member path')
    suffix = pathlib.PurePosixPath(entry['name']).suffix
    folder = {'.mat': 'radar_raw_frame', '.csv': 'text_labels'}.get(suffix)
    if folder != parts[2] or any(p in ('.', '..') or '\\' in p for p in parts):
        raise ValueError('Unexpected modality or unsafe member path')
    if entry['local_file'] != pathlib.PurePosixPath(*parts[1:]).as_posix():
        raise ValueError('Frozen local path differs from archive member path')
    return DATA.joinpath(*parts[1:])

def source_registry():
    """Read the exact frozen registry; no reconstruction or metadata rewrite."""
    expected = json.loads(FREEZE.read_text(encoding='utf8'))['sha256']['source_manifest']
    if sha(MANIFEST) != expected: raise ValueError('Frozen source registry hash mismatch')
    record = json.loads(MANIFEST.read_text(encoding='utf8'))
    if tuple(record['records']) != RECORDS or len(record['members']) != 5379:
        raise ValueError('Fixed record membership changed')
    entries = sorted(record['members'], key=lambda e: e['local_header_offset'])
    for entry in entries: local_path(entry)
    return record, entries, expected

def verify_payload(entry, data):
    if len(data) != entry['uncompressed_bytes'] or zlib.crc32(data) != entry['crc32']:
        raise ValueError('Provider CRC or uncompressed size mismatch')
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise ValueError('Frozen source member SHA256 mismatch')

def complete(entry):
    path = local_path(entry)
    if not path.exists() or path.stat().st_size != entry['uncompressed_bytes']:
        return False
    try: verify_payload(entry, path.read_bytes())
    except ValueError: return False
    return True

def ranges(entries):
    """Coalesce only adjacent selected members; skip intervening image payloads."""
    chunks, current, start, end = [], [], 0, 0
    for e in entries:
        off = e['local_header_offset']
        # Provider ZIP local headers have a short extended timestamp extra field.
        bound = off + 30 + len(e['name'].encode()) + 128 + e['compressed_bytes']
        if current and (off > end + 256 or bound - start > MAX_REQUEST):
            chunks.append((start, end, current)); current = []
        if not current: start = off
        current.append(e); end = max(end if len(current) > 1 else 0, bound)
    if current: chunks.append((start, end, current))
    return chunks

def fetch_chunk(url, item, *, opener=urllib.request.urlopen, attempts=4):
    start, end, entries = item
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={start}-{end-1}'})
    last = None
    for attempt in range(attempts):
        try:
            with opener(request, timeout=45) as response:
                if response.status != 206 or not response.headers.get('Content-Range', '').startswith(f'bytes {start}-{end-1}/'):
                    raise ValueError('Server ignored or altered bounded Range')
                body = response.read(end-start+1)
            if len(body) != end-start: raise ValueError('Range byte count mismatch')
            saved = []
            for e in entries:
                off = e['local_header_offset'] - start
                if body[off:off+4] != b'PK\x03\x04': raise ValueError('Bad local ZIP header')
                nlen, elen = struct.unpack_from('<HH', body, off+26)
                if body[off+30:off+30+nlen].decode('utf8') != e['name']:
                    raise ValueError('Local ZIP header name differs from frozen member')
                begin = off + 30 + nlen + elen
                data = body[begin:begin+e['compressed_bytes']]
                if e['compression'] == 8: data = zlib.decompress(data, -15)
                elif e['compression'] != 0: raise ValueError('Unsupported ZIP compression')
                verify_payload(e, data)
                path = local_path(e); path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_suffix(path.suffix+'.part'); tmp.write_bytes(data); tmp.replace(path)
                saved.append(e['name'])
            return len(saved), end-start
        except Exception as exc:
            last = exc
            if attempt < attempts-1: time.sleep(2*(attempt+1))
    raise RuntimeError(f'Range {start}:{end} failed: {last}')

def write_receipt(path, record):
    """Receipts must stay in the ignored data folder and never replace a file."""
    path = pathlib.Path(path)
    resolved = path.resolve()
    if resolved in (MANIFEST.resolve(), FREEZE.resolve()) or not resolved.is_relative_to(DATA.resolve()):
        raise ValueError('Refusing source-registry overwrite or receipt outside ignored data folder')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(record, stream, indent=2); stream.write('\n')

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    registry, entries, registry_sha = source_registry()
    plan = {'source_url': registry['source_url'], 'archive_bytes': registry['archive_bytes'],
            'frozen_source_manifest_sha256': registry_sha, 'records': RECORDS, 'members': len(entries),
            'compressed_bytes': sum(e['compressed_bytes'] for e in entries),
            'uncompressed_bytes': sum(e['uncompressed_bytes'] for e in entries),
            'selection': 'all .mat and .csv members of three fixed pms records; metadata only',
            'data_license': 'CC BY 4.0; primary IEEE DataPort dataset JSON-LD and DataCite DOI rightsList verified 2026-10-05. MIT is the author tool license.',
            'provider_repository': 'https://github.com/Xiangyu-Gao/Raw_ADC_radar_dataset_for_automotive_object_detection',
            'dataset_doi': 'https://doi.org/10.21227/xm40-jx59'}
    print(json.dumps(plan, indent=2), flush=True)
    if args.plan: return
    DATA.mkdir(parents=True, exist_ok=True)
    if not DATA.joinpath('.gitignore').exists(): DATA.joinpath('.gitignore').write_text('*\n!.gitignore\n')
    pending = [e for e in entries if not complete(e)]; chunks = ranges(pending)
    done, received, started = len(entries)-len(pending), 0, time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_chunk, registry['source_url'], item) for item in chunks]
        for future in concurrent.futures.as_completed(futures):
            count, nbytes = future.result(); done += count; received += nbytes
            print(json.dumps({'members_verified': done, 'total': len(entries), 'downloaded_bytes': received,
                              'elapsed_s': round(time.monotonic()-started, 1)}), flush=True)
    for e in entries:
        if not complete(e): raise ValueError(f'Missing or corrupt final member: {e["name"]}')
    if sha(MANIFEST) != registry_sha: raise ValueError('Frozen registry changed during acquisition')
    receipt = dict(plan, downloaded_bytes_this_run=received, members_reused=len(entries)-len(pending),
                   members_crc_sha_verified=len(entries), elapsed_seconds=time.monotonic()-started,
                   completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), frozen_registry_rewritten=False)
    write_receipt(DATA/'download_receipts'/f'{time.time_ns()}.json',receipt)
    print('All fixed members CRC/SHA verified; no signal outcomes computed.', flush=True)

if __name__ == '__main__': main()
