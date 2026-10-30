import socket
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from lynowcatch import engine

class EngineTests(unittest.TestCase):
    def address(self, address):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (address,443))]

    def test_reject_local_private_and_mixed_addresses(self):
        for address in ('127.0.0.1','10.0.0.1','169.254.169.254','192.168.1.1','::1'):
            with self.subTest(address=address), patch.object(engine.socket,'getaddrinfo',return_value=self.address(address)):
                with self.assertRaises(ValueError): engine.validate_url('https://example.com')
        with patch.object(engine.socket,'getaddrinfo',return_value=self.address('1.1.1.1')+self.address('127.0.0.1')):
            with self.assertRaises(ValueError): engine.validate_url('https://example.com')

    def test_reject_invalid_schemes_credentials_and_types(self):
        for url in ('file:///x','ftp://example.com','https://user:pass@example.com','bad',None,42):
            with self.subTest(url=url), self.assertRaises(ValueError): engine.validate_url(url)

    def test_public_url(self):
        with patch.object(engine.socket,'getaddrinfo',return_value=self.address('1.1.1.1')):
            self.assertEqual(engine.validate_url('https://example.com/video'), 'https://example.com/video')

    def test_options_and_trim_validation(self):
        self.assertEqual(engine.options({'format':'gif','start':2,'duration':5}),('gif','1080',2,5))
        for data in ({'format':'exe'},{'quality':'999'},{'start':-1},{'duration':3601},{'start':'nan'},{'start':'inf'},{'format':'original','start':1}):
            with self.subTest(data=data), self.assertRaises(ValueError): engine.options(data)

    def test_download_failure_removes_partial_output(self):
        def fail(cmd, **kwargs):
            target = Path(cmd[cmd.index('-o')+1]).parent
            (target/'media.mp4.part').write_bytes(b'partial')
            return subprocess.CompletedProcess(cmd,1)
        with tempfile.TemporaryDirectory() as temp, patch.object(engine,'validate_url',return_value='https://example.com'), patch.object(engine,'health',return_value={'ffmpeg':True,'ffprobe':True}), patch.object(engine.subprocess,'run',side_effect=fail):
            with self.assertRaises(ValueError): engine.download({'url':'https://example.com'},temp)
            self.assertEqual(list(Path(temp).iterdir()),[])

    def test_trim_gif_uses_offset_and_caps_duration(self):
        calls=[]
        def run(cmd, **kwargs):
            calls.append(cmd)
            if '-o' in cmd: Path(cmd[cmd.index('-o')+1].replace('%(ext)s','mp4')).write_bytes(b'video')
            else: Path(cmd[-1]).write_bytes(b'gif')
            return subprocess.CompletedProcess(cmd,0)
        with tempfile.TemporaryDirectory() as temp, patch.object(engine,'validate_url',return_value='https://example.com'), patch.object(engine,'health',return_value={'ffmpeg':True,'ffprobe':True}), patch.object(engine.subprocess,'run',side_effect=run):
            result=engine.download({'url':'https://example.com','format':'gif','start':4,'duration':20},temp)
            self.assertEqual(calls[1][calls[1].index('-ss')+1],'4.0')
            self.assertEqual(calls[1][calls[1].index('-t')+1],'15')
            self.assertEqual(result['size'],3)
            self.assertTrue(result['file'].endswith('.gif'))

if __name__ == '__main__': unittest.main()
