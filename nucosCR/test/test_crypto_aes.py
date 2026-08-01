import base64
import hashlib

from nucosCR import (
    CryptoAESBase,
    random,
    hexdigest,
    hexdigest_n,
    verify_hexdigest,
)


class TestCryptoAESBase:
    def test_encrypt_roundtrip(self):
        text = random(80000)
        en, nonce = CryptoAESBase("test").encryption(text)
        de, success = CryptoAESBase("test").decryption(en)
        assert success
        assert text == de

    def test_encrypt_returns_self_describing_blob(self):
        en, nonce = CryptoAESBase("test").encryption(b"hello")
        raw = base64.b64decode(en)
        assert raw[:3] == b"NC1"
        assert nonce == raw[3 + 16:3 + 16 + 16]

    def test_unicode_and_string_roundtrip(self):
        c = CryptoAESBase("pw")
        for payload in ("héllo wörld", "проверка", b"\x00\xffraw"):
            en, _ = c.encryption(payload)
            de, success = c.decryption(en)
            assert success
            expected = payload.encode() if isinstance(payload, str) else payload
            assert de == expected

    def test_plaintext_ending_in_padding_byte(self):
        en, _ = CryptoAESBase("test").encryption(b"secret{")
        de, success = CryptoAESBase("test").decryption(en)
        assert success
        assert de == b"secret{"

    def test_tampered_ciphertext_is_detected(self):
        en, _ = CryptoAESBase("test").encryption(random(100))
        data = bytearray(en)
        data[-1] ^= 0x01
        de, success = CryptoAESBase("test").decryption(bytes(data))
        assert not success

    def test_wrong_password_is_detected(self):
        en, _ = CryptoAESBase("right").encryption(b"secret data")
        de, success = CryptoAESBase("wrong").decryption(en)
        assert not success


class TestHexdigest:
    def test_legacy_flag_matches_standard_sha256(self):
        h = hexdigest("secret", legacy=True)
        assert len(h) == 64
        assert h == hashlib.sha256(b"secret").hexdigest()

    def test_hexdigest_n_legacy_repeats(self):
        assert hexdigest_n("x", 3, legacy=True) == hexdigest(
            hexdigest(hexdigest("x", legacy=True), legacy=True), legacy=True
        )

    def test_salted_output_differs_and_verifies(self):
        h1 = hexdigest("secret")
        h2 = hexdigest("secret")
        assert h1 != h2  # random salt
        assert h1.startswith("pbkdf2-sha256$")
        ok, needs = verify_hexdigest("secret", h1)
        assert ok and not needs

    def test_verify_legacy_reports_rehash(self):
        legacy = hexdigest("secret", legacy=True)
        ok, needs = verify_hexdigest("secret", legacy)
        assert ok and needs
        ok_bad, _ = verify_hexdigest("wrong", legacy)
        assert not ok_bad

    def test_verify_rejects_wrong_secret(self):
        h = hexdigest("secret")
        assert verify_hexdigest("nope", h)[0] is False

    def test_bytes_and_unicode_inputs_are_interoperable(self):
        # legacy is deterministic so str/bytes must match exactly
        assert hexdigest("secret", legacy=True) == hexdigest(b"secret", legacy=True)
        # salted hashes are random-per-call; validate cross-type via the verifier
        h = hexdigest(b"secret")
        assert verify_hexdigest("secret", h)[0] is True
