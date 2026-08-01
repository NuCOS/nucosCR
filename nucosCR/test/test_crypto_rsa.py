import os

from nucosCR import CryptoRSABase, random


class TestCryptoRSABase:
    def test_key_create_and_reload(self, tmp_path):
        c = CryptoRSABase(path=str(tmp_path))
        name = "test_admin"
        k1 = c.create_rsa_key(name)
        k2 = c.get_key_by_file(name)
        assert k1 == k2
        mode = oct(os.stat(c.filename).st_mode & 0o777)
        assert mode == "0o600"

    def test_encrypt_decrypt_roundtrip(self, tmp_path):
        c = CryptoRSABase(path=str(tmp_path))
        name = "test_admin"
        hexkey = c.get_hex_key(name)
        txt = random(100)
        assert c.decrypt(name, c.encrypt(txt, hexkey)) == txt

    def test_decrypt_rejects_tampered(self, tmp_path):
        c = CryptoRSABase(path=str(tmp_path))
        name = "test_admin"
        hexkey = c.get_hex_key(name)
        txt = random(100)
        en = bytearray(c.encrypt(txt, hexkey))
        en[-1] ^= 0x01
        out = c.decrypt(name, bytes(en))
        assert out != txt
