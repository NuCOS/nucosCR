# nucosCR
*nucosCR* is a convenient cryptography module in python, a working toolbox on
top of the *pycryptodomex* backend. It provides AES (GCM, authenticated) and
RSA helpers plus a small CLI file-encryption tool.

This module is in **alpha** stage, any usage is on your own risk and
responsibility.

## Install
```
pip install nucosCR
```
or download the tarball at [https://github.com/NuCOS/nucosCR](https://github.com/NuCOS/nucosCR), unzip and type
```
pip install -e .
```

## Quick usage
```python
from nucosCR import CryptoAESBase, hexdigest

# Authenticated AES: encryption() returns a single self-describing blob
# (salt + nonce + tag + ciphertext), decryption() verifies integrity.
c = CryptoAESBase("a strong password")
blob, _ = c.encryption(b"hello world")
plain, ok = c.decryption(blob)   # ok is False if tampered or wrong password

# Password hashing with a salted KDF. legacy=True reproduces the old
# unsalted SHA-256 digest so existing hashes keep validating:
h = hexdigest("pw")                       # salted, self-describing
from nucosCR import verify_hexdigest
valid, needs_rehash = verify_hexdigest("pw", h)
```

## Backward compatibility & migration (0.3.x)
- `hexdigest` / `hexdigest_n` now default to a salted PBKDF2-HMAC-SHA256 hash.
  Pass `legacy=True` to reproduce the previous unsalted SHA-256 digest.
  `verify_hexdigest(secret, stored)` returns `(valid, needs_rehash)` so storing
  systems can transparently re-hash legacy credentials on next successful login.
- AES output is now authenticated (GCM) with PKCS7 padding. Legacy pre-0.3
  EAX-encoded blobs can still be decrypted by passing the stored `nonce` to
  `decryption`.

## Development, build & test

Requires Python 3.10+.

```
./genie.sh all     # clean, build sdist+wheel, install into a venv, run pytest
./genie.sh build   # build only (dist/)
./genie.sh test    # pip install -e . && pytest
```

Tests are **pytest-only** and live in `nucosCR/test/`:

```
pip install -e . pytest
pytest
```

## Documentation
[http://nucoscr.readthedocs.io/](http://nucoscr.readthedocs.io/)

## Licence
MIT License

## Platforms
No specific platform dependency. Python 3.10+. Up to now only Linux OS is
tested.
