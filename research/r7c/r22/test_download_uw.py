"""Fabricated-only public acquisition tests; no provider/raw data are fetched."""
import hashlib,io,json,pathlib,tempfile,unittest,unittest.mock,zipfile
import download_uw as D

class Response:
    def __init__(self,body,start,end,total,status=206):
        self.status=status; self.headers={'Content-Range':f'bytes {start}-{end-1}/{total}'}
        self.stream=io.BytesIO(body)
    def __enter__(self): return self
    def __exit__(self,*args): return None
    def read(self,n): return self.stream.read(n)

def fabricated():
    memory=io.BytesIO()
    payloads={
      'Automotive/2019_04_09_pms1000/radar_raw_frame/000003.mat':b'fabricated raw mat bytes only',
      'Automotive/2019_04_09_pms1000/text_labels/0000000003.csv':b'26,0,0,7,0.7,0.7\n',
    }
    with zipfile.ZipFile(memory,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,payload in payloads.items(): archive.writestr(name,payload)
    body=memory.getvalue(); entries=[]
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for info in archive.infolist():
            entries.append(dict(name=info.filename,compression=info.compress_type,crc32=info.CRC,
              compressed_bytes=info.compress_size,uncompressed_bytes=info.file_size,local_header_offset=info.header_offset,
              local_file=info.filename.removeprefix('Automotive/'),sha256=hashlib.sha256(payloads[info.filename]).hexdigest()))
    return body,entries

class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=pathlib.Path(self.temp.name)
        self.data_patch=unittest.mock.patch.object(D,'DATA',self.root/'data');self.data_patch.start()
    def tearDown(self): self.data_patch.stop();self.temp.cleanup()

    def test_bounded_range_roundtrip_crc_sha_and_resume(self):
        body,entries=fabricated(); calls=[]
        def opener(request,timeout):
            requested=request.headers['Range'];lo,hi=map(int,requested.removeprefix('bytes=').split('-'))
            calls.append((lo,hi));return Response(body[lo:hi+1],lo,hi+1,len(body))
        chunks=D.ranges(entries)
        self.assertTrue(all(end-start<=D.MAX_REQUEST for start,end,_ in chunks))
        for chunk in chunks: D.fetch_chunk('https://example.invalid/archive.zip',chunk,opener=opener,attempts=1)
        self.assertTrue(calls)
        self.assertTrue(all(D.complete(e) for e in entries))
        D.local_path(entries[0]).write_bytes(b'corrupt existing member')
        self.assertFalse(D.complete(entries[0]))

    def test_sha_and_crc_corruption_refused(self):
        body,entries=fabricated();entry=entries[0]
        with zipfile.ZipFile(io.BytesIO(body)) as archive: payload=archive.read(entry['name'])
        with self.assertRaisesRegex(ValueError,'CRC'): D.verify_payload(dict(entry,crc32=0),payload)
        with self.assertRaisesRegex(ValueError,'SHA256'): D.verify_payload(dict(entry,sha256='0'*64),payload)

    def test_path_escape_and_noncanonical_local_path_refused(self):
        _,entries=fabricated();entry=entries[0]
        for changed in (dict(entry,name='Automotive/../radar_raw_frame/000003.mat'),
                        dict(entry,local_file='../outside.mat'),
                        dict(entry,local_file=entry['local_file'].replace('/','\\'))):
            with self.assertRaises(ValueError): D.local_path(changed)

    def test_ignored_range_refused_without_output(self):
        body,entries=fabricated();chunk=D.ranges(entries)[0]
        def opener(request,timeout): return Response(body,chunk[0],chunk[1],len(body),status=200)
        with self.assertRaisesRegex(RuntimeError,'ignored'): D.fetch_chunk('https://example.invalid/archive.zip',chunk,opener=opener,attempts=1)
        self.assertFalse(D.local_path(entries[0]).exists())

    def test_receipt_cannot_overwrite_source_registry_or_another_receipt(self):
        registry=self.root/'source_registry.json';registry.write_bytes(b'immutable fake registry')
        with unittest.mock.patch.object(D,'MANIFEST',registry):
            with self.assertRaisesRegex(ValueError,'overwrite'): D.write_receipt(registry,{'changed':True})
        self.assertEqual(registry.read_bytes(),b'immutable fake registry')
        receipt=D.DATA/'download_receipts/one.json';D.write_receipt(receipt,{'verified':True})
        with self.assertRaises(FileExistsError): D.write_receipt(receipt,{'changed':True})
        self.assertEqual(json.loads(receipt.read_text()),{'verified':True})

if __name__=='__main__': unittest.main()
