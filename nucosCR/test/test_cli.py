import os
import subprocess
import sys

import nucosCR
from nucosCR import random, read_from_file, write_to_file, get_crc_from_file

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AES_CP = os.path.join(ROOT, "scripts", "aes-cp")


class TestFileHelpers:
    def test_write_read_roundtrip(self, tmp_path):
        fn = str(tmp_path / "data.bin")
        data = random(50000)
        write_to_file(fn, data)
        assert read_from_file(fn) == data

    def test_chunked_write_matches(self, tmp_path):
        fn = str(tmp_path / "big.bin")
        data = random(200000)
        write_to_file(fn, data, chunksize=4096)
        assert read_from_file(fn) == data

    def test_crc(self, tmp_path):
        fn = str(tmp_path / "crc.bin")
        write_to_file(fn, b"fixed content")
        assert get_crc_from_file(fn) == get_crc_from_file(fn)
        assert get_crc_from_file(str(tmp_path / "missing.bin")) is None


class TestCLI:
    def _run(self, *args):
        env = dict(os.environ)
        env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, AES_CP, *args], capture_output=True, text=True, env=env
        )

    def test_cli_roundtrip_and_tamper(self, tmp_path):
        plain = tmp_path / "plain.txt"
        enc = tmp_path / "enc.bin"
        dec = tmp_path / "dec.txt"
        bad = tmp_path / "bad.bin"
        plain.write_bytes(b"top secret file content")
        pw = "letmein"

        r = self._run("-e", "-o", "-p", pw, str(plain), str(enc))
        assert r.returncode == 0, r.stderr
        assert enc.exists()

        r = self._run("-d", "-o", "-p", pw, str(enc), str(dec))
        assert r.returncode == 0, r.stderr
        assert dec.read_bytes() == plain.read_bytes()

        tampered = bytearray(enc.read_bytes())
        tampered[-1] ^= 0x40
        bad.write_bytes(bytes(tampered))
        r = self._run("-d", "-p", pw, str(bad), str(tmp_path / "bad.txt"))
        assert "failed" in r.stdout.lower()

    def test_cli_requires_source_and_dest(self, tmp_path):
        r = self._run("-e", "-p", "pw")
        assert r.returncode != 0


def test_version_reported():
    assert nucosCR.version.count(".") >= 2
