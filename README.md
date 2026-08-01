# nucosCR
*nucosCR* is a convenient cryptography module in Python, a working toolbox on
top of the *pycryptodomex* backend. It provides **AES-GCM** authenticated
encryption, **RSA** public-key cryptography, **salted password hashing** with
credential migration, and a **CLI file-encryption** tool.

This module is in **alpha** stage — any usage is on your own risk and
responsibility.

## Install
```bash
pip install nucosCR
```
or from source:
```bash
git clone https://github.com/NuCOS/nucosCR.git
cd nucosCR
pip install -e .
```
Requires **Python 3.10+**.

## Quick usage

```python
from nucosCR import CryptoAESBase, hexdigest, verify_hexdigest

# Authenticated AES-GCM encryption — a single self-describing blob.
enc = CryptoAESBase("my secret")
blob, _ = enc.encryption(b"confidential data")
plain, ok  = enc.decryption(blob)       # ok == False if tampered

# Salted PBKDF2 password hashing with transparent credential migration.
stored = hexdigest("hunter2")            # self-describing format
valid, needs_rehash = verify_hexdigest("hunter2", stored)
if valid and needs_rehash:
    save(hexdigest("hunter2"))           # upgraded !
```

## Documentation

**Full usage guide with every feature and recipe → [docs/USAGE.md](docs/USAGE.md)**

| Topic | What you get |
|---|---|
| [AES-GCM encryption](docs/USAGE.md#aes-authenticated-encryption) | Encrypt/decrypt, file I/O, tamper detection, legacy EAX compat, internal blob format |
| [Password hashing](docs/USAGE.md#password-hashing--migration) | Salted KDF, legacy SHA-256 compat, `verify_hexdigest` migration recipe |
| [RSA public-key crypto](docs/USAGE.md#rsa-public-key-crypto) | Key generation (PEM, `0600`), encrypt/decrypt, hex public key |
| [CLI tool `aes-cp`](docs/USAGE.md#cli-tool--aes-cp) | Encrypt/decrypt files & folders, CRC check |
| [File utilities](docs/USAGE.md#file-utilities) | `read_from_file`, `write_to_file`, `get_crc_from_file`, `random` |

Built docs: [nucoscr.readthedocs.io](http://nucoscr.readthedocs.io/)

## Backward compatibility (0.3.x)
- **`hexdigest` / `hexdigest_n`** default to salted PBKDF2. Pass `legacy=True`
  to reproduce the old SHA-256 digest. `verify_hexdigest` returns `needs_rehash`
  so credentials can be transparently migrated on next login.
- **AES** is now authenticated GCM with PKCS7 padding. Pre-0.3 EAX blobs can
  still be decrypted by passing the stored `nonce` to `decryption()`.

## Development

```bash
./genie.sh all      # clean → build → venv-install → pytest
./genie.sh test     # pip install -e . && pytest
pytest              # run the test suite directly
```

Requires **Python 3.10+**. CI matrix: 3.10, 3.11, 3.12, 3.13.

## Licence
MIT — see [`LICENSE.txt`](LICENSE.txt).

## Platforms
No specific OS dependency. Tested on Linux only.