# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 11:19:37 2014

@author: BRAUOLI

Cryptographic primitives built on top of pycryptodomex.

Note on a major change in the 0.3.x line:
- AES now uses authenticated GCM (integrity + confidentiality) instead of an
  unauthenticated EAX misuse, and PKCS7 padding instead of a fixed byte.
- A single self-describing ciphertext blob embeds salt + nonce + tag, so no
  separate nonce/tag bookkeeping is needed.
- ``hexdigest`` / ``hexdigest_n`` now default to a salted KDF. Pass
  ``legacy=True`` to reproduce the old unsalted SHA-256 behaviour so that
  previously stored hashes keep validating and can be migrated (see
  ``verify_hexdigest``).
"""
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome import Random
from Cryptodome.Util.Padding import pad, unpad
import base64, os, binascii

# AES blob magic to tag the new self-describing format.
_AES_MAGIC = b"NC1"

# Salt length and tag length used by the AES GCM format.
_AES_SALT_LEN = 16
_AES_NONCE_LEN = 16
_AES_TAG_LEN = 16

# Key derivation defaults (password hashing / key derivation).
_PBKDF2_ITERATIONS = 100000
_HEXDIGEST_PREFIX = "pbkdf2-sha256"


def _to_bytes(s):
    if type(s) is bytes:
        return s
    return s.encode("utf8")


def _hexdigest_legacy(s):
    """Legacy unsalted single-round SHA-256 hex digest (pre-0.3 behaviour)."""
    h = SHA256.new()
    h.update(_to_bytes(s))
    return h.hexdigest()


def hexdigest(s, legacy=False):
    """
    Return a digest of ``s``.

    By default (``legacy=False``) a salted, self-describing PBKDF2-HMAC-SHA256
    hash is returned. Pass ``legacy=True`` to obtain the previous unsalted
    single-round SHA-256 hex digest, so existing stored hashes keep working and
    can be migrated with :func:`verify_hexdigest`.

    :param s: secret to hash (str or bytes)
    :param legacy: if True, reproduce the old unsalted SHA-256 digest
    :return: hex/self-describing string
    """
    if legacy:
        return _hexdigest_legacy(s)
    salt = Random.get_random_bytes(16)
    dk = PBKDF2(_to_bytes(s), salt, dkLen=32, count=_PBKDF2_ITERATIONS,
                hmac_hash_module=SHA256)
    return "{0}${1}${2}${3}".format(_HEXDIGEST_PREFIX, _PBKDF2_ITERATIONS,
                                    salt.hex(), dk.hex())


def hexdigest_n(s, n_max, legacy=False):
    """
    Iterated digest (kept for backward compatibility).

    In legacy mode this reproduces the old behaviour of applying SHA-256
    ``n_max`` times. In the new mode the iteration count is handled inside the
    KDF, so a single salted PBKDF2 hash is returned regardless of ``n_max``.
    """
    if legacy:
        for _ in range(n_max):
            s = _hexdigest_legacy(s)
        return s
    return hexdigest(s, legacy=False)


def verify_hexdigest(secret, stored):
    """
    Validate ``secret`` against a stored hash and report whether it should be
    re-hashed (i.e. still stored in the old legacy format) so callers can
    transparently migrate credentials on the next successful login.

    :param secret: candidate secret (str or bytes)
    :param stored: previously stored hash string
    :return: (valid, needs_rehash)
    """
    if stored.startswith(_HEXDIGEST_PREFIX + "$"):
        try:
            _, iters_s, salt_hex, dgst_hex = stored.split("$")
        except ValueError:
            return False, False
        try:
            dk = PBKDF2(_to_bytes(secret), bytes.fromhex(salt_hex), dkLen=32,
                        count=int(iters_s), hmac_hash_module=SHA256)
        except (ValueError, TypeError):
            return False, False
        return dk.hex() == dgst_hex, False
    # Legacy (unsalted single-round SHA-256) hash -> needs re-hashing.
    return _hexdigest_legacy(secret) == stored, True


def read_from_file(filename):
    with open(filename, "rb") as in_file:
        data = in_file.read()
    return data


def write_to_file(filename, data, chunksize=8192):
    """
    Write bytes from data into file

    :param filename: name of file
    :param data: list with data (turned into bytearrays)
    :param chunksize: the bit-size which is transmitted at once
    """
    with open(filename, "wb") as f:
        loc = 0
        length = len(data)
        while True:
            if loc + chunksize < length:
                chunk = data[loc:loc + chunksize]
                f.write(chunk)
                loc += chunksize
            else:
                chunk = data[loc:length]
                f.write(chunk)
                break


def get_crc_from_file(filename):
    if os.path.exists(filename):
        data = read_from_file(filename)
        return binascii.crc32(data)


def random(n):
    out = Random.new()
    number = out.read(n)
    hexnumber = binascii.hexlify(number)
    return hexnumber


class CryptoAESBase():
    """
    class is based on bytes as input and output. Nevertheless tolerant against
    unicode and string input.
    """
    def __init__(self, passwd):
        self.passwd = _to_bytes(passwd)

    def _derive_key(self, salt):
        return PBKDF2(self.passwd, salt, dkLen=32, count=_PBKDF2_ITERATIONS,
                      hmac_hash_module=SHA256)

    def _derive_key_legacy(self):
        h = SHA256.new()
        h.update(self.passwd)
        return h.digest()

    def encryption(self, pI):
        """
        Encrypt plaintext with AES-GCM using a fresh salt and nonce.

        Returns a single self-describing base64 blob
        ``b64("NC1" + salt + nonce + tag + ciphertext)`` together with the
        nonce (embedded in the blob, kept for API compatibility).
        """
        salt = Random.get_random_bytes(_AES_SALT_LEN)
        key = self._derive_key(salt)
        nonce = Random.get_random_bytes(_AES_NONCE_LEN)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        pt = _to_bytes(pI)
        ct, tag = cipher.encrypt_and_digest(pad(pt, AES.block_size))
        blob = base64.b64encode(_AES_MAGIC + salt + nonce + tag + ct)
        return blob, nonce

    def decryption(self, encryptedBytes, nonce=None):
        """
        Decrypt a previously encrypted payload.

        New self-describing blobs (``NC1`` prefix) carry their own salt and
        nonce, so passing ``nonce=None`` ``decrypt_and_verify``s that format.
        The legacy pre-0.3 EAX format is still supported when an explicit
        ``nonce`` is supplied.
        """
        try:
            data = base64.b64decode(encryptedBytes)
            if data[:3] == _AES_MAGIC:
                salt = data[3:3 + _AES_SALT_LEN]
                nonce = data[3 + _AES_SALT_LEN:3 + _AES_SALT_LEN + _AES_NONCE_LEN]
                tag = data[3 + _AES_SALT_LEN + _AES_NONCE_LEN:
                            3 + _AES_SALT_LEN + _AES_NONCE_LEN + _AES_TAG_LEN]
                ct = data[3 + _AES_SALT_LEN + _AES_NONCE_LEN + _AES_TAG_LEN:]
                key = self._derive_key(salt)
                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                plain = cipher.decrypt_and_verify(ct, tag)
                return unpad(plain, AES.block_size), True
            # Legacy: unauthenticated EAX, fixed '}' padding, unsalted key.
            if nonce is None:
                return b"", False
            key = self._derive_key_legacy()
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            pt = cipher.decrypt(data).rstrip(b"{")
            return pt, True
        except (ValueError, KeyError, TypeError):
            return b"", False
