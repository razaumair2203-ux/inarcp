"""Extract ONE member from the 132 GB NetRAD.zip on Figshare using HTTP range requests.
Usage: python netrad_extract_member.py "<member path inside zip>" <output file>
Example member: "NetRAD/N3/e11_06_09_1113_58_P1_1_130000_S0_1_2047_node3_MF_refsig.mat"
Requires only Python stdlib + curl on PATH. Streams and inflates (deflate) to disk.
"""
import struct, zlib, subprocess, sys
URL = 'https://ndownloader.figshare.com/files/65710497'
TOTAL = 131781942836
def rng(s, l):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', '120', '-r', f'{s}-{s+l-1}', URL], capture_output=True, check=True)
    return r.stdout
def central_directory():
    tail = rng(TOTAL - 65536, 65536)
    j = tail.rfind(b'PK\x06\x06')
    (_, _, _, _, _, _, ntot, cdsize, cdoff) = struct.unpack_from('<QHHIIQQQQ', tail, j + 4)
    cd = rng(cdoff, cdsize)
    i = 0; ents = {}
    while cd[i:i+4] == b'PK\x01\x02':
        (_, _, flag, meth, _, _, crc, csz, usz, nl, el, cl, _, _, _, lho) = struct.unpack_from('<HHHHHHIIIHHHHHII', cd, i + 4)
        name = cd[i+46:i+46+nl].decode('utf-8', 'replace'); extra = cd[i+46+nl:i+46+nl+el]
        k = 0
        while k + 4 <= len(extra):
            hid, hsz = struct.unpack_from('<HH', extra, k)
            if hid == 1:
                p = k + 4
                if usz == 0xFFFFFFFF: usz = struct.unpack_from('<Q', extra, p)[0]; p += 8
                if csz == 0xFFFFFFFF: csz = struct.unpack_from('<Q', extra, p)[0]; p += 8
                if lho == 0xFFFFFFFF: lho = struct.unpack_from('<Q', extra, p)[0]; p += 8
            k += 4 + hsz
        ents[name] = (lho, csz, usz, meth, crc); i += 46 + nl + el + cl
    return ents
def extract(member, out):
    ents = central_directory()
    if member == 'LIST':
        for n, (lho, csz, usz, m, c) in ents.items(): print(f'{usz:>14d}  {n}')
        return
    lho, csz, usz, meth, crc = ents[member]
    h = rng(lho, 30 + 1024); nl, el = struct.unpack_from('<HH', h, 26)
    start = lho + 30 + nl + el
    d = zlib.decompressobj(-15) if meth == 8 else None
    CH = 256 * 1024 * 1024; pos = 0; c = 0
    with open(out, 'wb') as fh:
        while pos < csz:
            n = min(CH, csz - pos)
            blk = rng(start + pos, n); pos += n
            data = d.decompress(blk) if d else blk
            c = zlib.crc32(data, c); fh.write(data)
            print(f'{pos/1e9:.2f}/{csz/1e9:.2f} GB', end='\r', flush=True)
        if d: tail = d.flush(); c = zlib.crc32(tail, c); fh.write(tail)
    print('\nCRC ok' if (c & 0xFFFFFFFF) == crc else '\nCRC MISMATCH')
if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
