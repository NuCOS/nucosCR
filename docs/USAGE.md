# Usage Documentation — nucosCR 0.3.x

Full API reference and recipes for the nucosCR cryptography toolbox.

---

## Table of Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [AES authenticated encryption](#aes-authenticated-encryption)
  - [Basic encrypt/decrypt](#basic-encrypt--decrypt)
  - [File-based encryption](#file-based-encryption)
  - [Detecting tampering](#detecting-tampering)
  - [Legacy EAX decryption](#legacy-eax-decryption)
  - [Internal format (advanced)](#internal-format-advanced)
- [Password hashing & migration](#password-hashing--migration)
  - [`hexdigest` — salted KDF](#hexdigest--salted-kdf)
  - [`hexdigest_n` — iterated digest](#hexdigest_n--iterated-digest)
  - [`verify_hexdigest` — credential verification & migration](#verify_hexdigest--credential-verification--migration)
  - [Migration recipe](#migration-recipe)
- [RSA public-key crypto](#rsa-public-key-crypto)
  - [Key management](#key-management)
  - [Encrypt & decrypt](#encrypt--decrypt)
- [File utilities](#file-utilities)
- [Random bytes](#random-bytes)
- [CLI tool: `aes-cp`](#cli-tool--aes-cp)
- [Module version](#module-version)
- [Complete export list](#complete-export-list)

---

## Installation

```bash
pip install nucosCR
```

or from source:

```bash
git clone https://github.com/NuCOS/nucosCR.git
cd nucosCR
pip install -e .
```

Requires **Python 3.10+** (backend: `pycryptodomex`).

---

## Quick start

```python
from nucosCR import CryptoAESBase, hexdigest, verify_hexdigest

# AES encrypt
c = CryptoAESBase("my-secret")
blob, _ = c.encryption(b"payload")
plain, ok = c.decryption(blob)
assert ok and plain == b"payload"

# hash a password
stored = hexdigest("hunter2")

# verify (and migrate if needed)
is_valid, needs_rehash = verify_hexdigest("hunter2", stored)
```

---

## AES authenticated encryption

### Basic encrypt / decrypt

`CryptoAESBase` uses **AES-256-GCM** with a salted PBKDF2 key derivation
(100 000 iterations). Encryption returns a self-describing base64 blob that
embeds salt, nonce and authentication tag — you only need to store or transmit
a single value.

```python
from nucosCR import CryptoAESBase

c = CryptoAESBase("strong passphrase")

# Encryption — returns (blob, nonce). The nonce is informational; it is
# already embedded inside `blob`.
blob, _ = c.encryption(b"confidential data")
# blob is a base64-encoded string that can be saved to disk or sent over
# the wire.  Example content: b"TkMx..."  (starts with the NC1 magic)

# Decryption — just pass the blob.  Returns (plaintext, success).
plain, ok = c.decryption(blob)
assert ok                     # True = authenticated + decrypted
assert plain == b"confidential data"
```

**Signature:**

| Method | Parameters | Returns |
|---|---|---|
| `__init__(passwd)` | `passwd` — `str` or `bytes` | — |
| `encryption(plain)` | `plain` — `str` or `bytes` | `(blob: bytes, nonce: bytes)` |
| `decryption(blob, nonce=None)` | `blob: bytes`, `nonce=None` for new format | `(plain: bytes, success: bool)` |

**Notes:**
- Plaintext can be `str` (UTF-8 encoded) or `bytes`.
- `success == False` means either the blob was tampered with or the wrong
  password was used.
- Encryption produces a unique blob every time, even for identical input
  (fresh random salt + nonce).

### File-based encryption

Use the built-in file helpers together with `CryptoAESBase`:

```python
from nucosCR import CryptoAESBase, read_from_file, write_to_file

c = CryptoAESBase("file-password")
blob, _ = c.encryption(read_from_file("secret.txt"))
write_to_file("secret.enc", blob)

# later…
data = read_from_file("secret.enc")
plain, ok = CryptoAESBase("file-password").decryption(data)
if ok:
    write_to_file("secret.txt", plain)
```

### Detecting tampering

GCM authentication detects any modification of the ciphertext:

```python
c = CryptoAESBase("secret")
blob, _ = c.encryption(b"integrity check")

# Tamper with the blob
corrupted = bytearray(blob)
corrupted[-1] ^= 0x01

plain, ok = c.decryption(bytes(corrupted))
if not ok:
    print("Integrity check failed — data was altered!")
```

### Legacy EAX decryption

Files encrypted with nucosCR **before version 0.3** used an unauthenticated
EAX mode. You can still decrypt them by passing the `nonce` that was returned
by the legacy `encryption()` call:

```python
c = CryptoAESBase("old-password")
encrypted_data = read_from_file("legacy.enc")
# nonce must be read from wherever it was stored (sidecar file, etc.)
plain, ok = c.decryption(encrypted_data, nonce=known_nonce)
```

If the `nonce` parameter is provided and the blob does not start with the
`NC1` magic, the legacy EAX path is automatically selected.

### Internal format (advanced)

The new self-describing blob (v0.3+) is structured as:

```
base64(  "NC1"         — 3-byte magic
       + salt          — 16 bytes (PBKDF2 salt)
       + nonce         — 16 bytes (GCM nonce)
       + tag           — 16 bytes (GCM authentication tag)
       + ciphertext    — variable length (AES-GCM encrypted, PKCS7 padded)
      )
```

Key derivation uses `PBKDF2-HMAC-SHA256` with the embedded salt and
100 000 iterations.

---

## Password hashing & migration

The module provides three functions for hashing secrets and migrating from the
old unsalted SHA-256 scheme to a modern salted KDF.

### `hexdigest` — salted KDF

```python
from nucosCR import hexdigest

# Default (v0.3+): salted, self-describing PBKDF2 hash.
h = hexdigest("super-secret")
print(h)
# Example: pbkdf2-sha256$100000$ab12cd...$ef34ab...

# Legacy (pre-0.3): unsalted single-round SHA-256 hex.
legacy = hexdigest("super-secret", legacy=True)
print(legacy)
# Always the same: a 64-character hex string
```

**Signature:** `hexdigest(s, legacy=False) -> str`

| Parameter | Default | Description |
|---|---|---|
| `s` | (required) | Secret to hash (`str` or `bytes`) |
| `legacy` | `False` | `True` = reproduce old SHA-256 behaviour |

The new default format is: `pbkdf2-sha256$<iterations>$<salt_hex>$<digest_hex>`.

### `hexdigest_n` — iterated digest

```python
from nucosCR import hexdigest_n

# Legacy: apply SHA-256 n times (as old CLI did).
h = hexdigest_n("pass", 100, legacy=True)

# New mode: single salted KDF (the iteration concept is subsumed by the
# KDF's own iteration count; ``n_max`` is retained for API compatibility).
h = hexdigest_n("pass", 100)          # equivalent to hexdigest("pass")
h = hexdigest_n("pass", any_number)   # all produce the same KDF hash
```

**Signature:** `hexdigest_n(s, n_max, legacy=False) -> str`

### `verify_hexdigest` — credential verification & migration

This single function verifies a candidate secret against *any* stored hash
(old legacy or new KDF) and tells you if the stored hash should be upgraded:

```python
from nucosCR import verify_hexdigest

stored = get_stored_hash_from_database()   # could be old or new format

valid, needs_rehash = verify_hexdigest("candidate-password", stored)

if not valid:
    print("Wrong password")
elif needs_rehash:
    # It matched, but the hash is still in the old (unsalted) format.
    # Re-hash it to the new salted format immediately.
    new_hash = hexdigest("candidate-password")
    update_stored_hash_in_database(new_hash)
    print("Password valid — upgraded to new hash format")
else:
    print("Password valid (already in new format)")
```

**Signature:** `verify_hexdigest(secret, stored) -> (valid: bool, needs_rehash: bool)`

| Return value | Meaning |
|---|---|
| `(False, *)` | Secret does **not** match |
| `(True, False)` | Secret matches **new salted** format — no action needed |
| `(True, True)` | Secret matches **old legacy** format — re-hash now |

### Migration recipe

Use this pattern in your login / authentication handler:

```python
from nucosCR import hexdigest, verify_hexdigest

def authenticate(username, password, db):
    stored_hash = db.get_hash(username)
    if not stored_hash:
        return False
    valid, needs_rehash = verify_hexdigest(password, stored_hash)
    if not valid:
        return False
    if needs_rehash:
        db.set_hash(username, hexdigest(password))
    return True
```

---

## RSA public-key crypto

`CryptoRSABase` provides 2048-bit RSA with SHA-256 message integrity. Keys
are stored as PEM files in a configurable directory (default: `./PEM/`).

### Key management

```python
from nucosCR import CryptoRSABase

# Optionally choose a key storage directory.
rsa = CryptoRSABase(path="/home/user/.nucos_keys")

# Generate a new key pair or load it if it already exists.
# Keys are stored as  <path>/<name>_localkey.pem  with mode 0600.
key = rsa.create_rsa_key("alice")
# key = rsa.get_key_by_file("alice")             # load existing key

# Get the public key in hex (used for encryption).
public_hex = rsa.get_hex_key("alice")
print(public_hex)   # long hex string — give this to whoever sends you data
```

**Key lifecycle:**
1. `create_rsa_key(name)` — generates a 2048-bit RSA key and saves it to disk.
2. `get_key_by_file(name)` — loads the key from disk (creates it if absent).
3. `get_hex_key(name)` — returns the public key as a hex string (DER export).
4. Keys are stored with restrictive permissions (`0600`).

### Encrypt & decrypt

```python
rsa = CryptoRSABase(path="./keys")

# --- Sender side (only needs hex public key) ---
sender = CryptoRSABase()           # no path needed for sender
hexkey = "..."                     # obtained from receiver's get_hex_key()
ciphertext = sender.encrypt(b"short secret message", hexkey)
# RSA can only encrypt data up to ~190 bytes (2048-bit key minus padding + digest).

# --- Receiver side ---
receiver = CryptoRSABase(path="./keys")
plaintext = receiver.decrypt("alice", ciphertext)
assert plaintext == b"short secret message"
```

**Signature:**

| Method | Parameters | Returns |
|---|---|---|
| `__init__(path=None)` | `path` — key storage directory | — |
| `create_rsa_key(name)` | `name` — identity string | RSA key object |
| `get_key_by_file(name)` | `name` — identity string | RSA key object |
| `get_hex_key(name)` | `name` — identity string | hex string (public key) |
| `encrypt(message, hexkey)` | `message: bytes`, `hexkey: str` | ciphertext `bytes` |
| `decrypt(name, ciphertext)` | `name: str`, `ciphertext: bytes` | plaintext `bytes` |

**Security note:** the message is appended with a SHA-256 digest (RSA
sign-and-encrypt pattern). The decrypt method verifies the digest
internally; if the digest does not match, the decrypted bytes are returned
anyway but should be discarded by the caller. Future versions will throw an
exception on digest mismatch.

---

## File utilities

Convenience helpers for binary file I/O and integrity checks:

```python
from nucosCR import read_from_file, write_to_file, get_crc_from_file

# Write bytes with configurable chunk size.
write_to_file("data.bin", b"hello world", chunksize=4096)

# Read as bytes.
raw = read_from_file("data.bin")          # b"hello world"

# CRC-32 (e.g. to detect accidental corruption).
crc = get_crc_from_file("data.bin")      # int or None if the file is missing
```

**Signatures:**

| Function | Signature |
|---|---|
| `read_from_file(filename)` | `-> bytes` |
| `write_to_file(filename, data, chunksize=8192)` | `-> None` |
| `get_crc_from_file(filename)` | `-> int` or `None` |

---

## Random bytes

Generate cryptographically random hex bytes:

```python
from nucosCR import random

hex_bytes = random(32)   # returns a 64-char hex string (32 raw bytes)
```

**Signature:** `random(n) -> str` — returns `binascii.hexlify(n random bytes)`.
Note that the returned string length is `2 × n`.

---

## CLI tool: `aes-cp`

The `aes-cp` command-line utility encrypts or decrypts files and directories
using the same `CryptoAESBase` class.

```bash
# Encrypt a file
aes-cp -e -p mypassword source.txt enc.bin

# Decrypt a file
aes-cp -d -p mypassword enc.bin decrypted.txt

# Encrypt an entire folder (recursive copy)
aes-cp -e -p mypassword source_folder/ dest_folder/

# Overwrite existing files (no -o = skip existing)
aes-cp -e -o -p mypassword source.txt enc.bin

# Compare two files with CRC-32
aes-cp -c file1.txt file2.txt
```

**Arguments:**

| Flag | Meaning |
|---|---|
| `-e <src> <dest>` | Encrypt copy |
| `-d <src> <dest>` | Decrypt copy |
| `-c <file1> <file2>` | CRC check (prints `True`/`False`) |
| `-o` | Overwrite existing destination files |
| `-p <password>` | Password (if omitted, prompts via `getpass`) |

The CLI writes the same self-describing `NC1` base64 blobs as the Python API,
so you can mix API and CLI operations freely.

---

## Module version

```python
import nucosCR

print(nucosCR.version)   # e.g. "0.3.0"
```

The version string is sourced from `nucosCR/version.py` and follows PEP 440.

---

## Complete export list

Everything available from `nucosCR`:

```python
from nucosCR import (
    # AES
    CryptoAESBase,

    # RSA
    CryptoRSABase,

    # Password hashing & migration
    hexdigest,
    hexdigest_n,
    verify_hexdigest,

    # File I/O
    read_from_file,
    write_to_file,
    get_crc_from_file,

    # Utilities
    random,
    version,
)
```