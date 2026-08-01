# CHANGELOG

All notable changes to this project are documented in this file,
newest first.

---

## Documentation overhaul — 2026-08-01

### 🚀 COMPLETED: comprehensive usage documentation
- Created `docs/USAGE.md` — a full API reference and recipe guide covering
  every public export: AES-GCM encrypt/decrypt (including tamper detection,
  file I/O, legacy EAX compat, and the internal blob format), salted password
  hashing with `hexdigest`/`hexdigest_n`/`verify_hexdigest` and a complete
  credential-migration recipe, RSA key management and encrypt/decrypt, file
  utilities (`read_from_file`/`write_from_file`/`get_crc_from_file`/`random`),
  the `aes-cp` CLI tool, and the module `version` export.
- Rewrote `README.md` with a concise install/quick-start section and a
  prominent table-of-contents linking into `docs/USAGE.md`.

---

## Repository hygiene — 2026-08-01

### 🚀 COMPLETED: GitHub-ready repository
- Updated `LICENSE.txt` copyright year to **2016–2026**.
- Added GitHub Actions CI (`.github/workflows/ci.yml`): pytest matrix on Python
  3.10–3.13 plus a build job producing sdist + wheel and running `twine check`.
- Added standard project files: `CONTRIBUTING.md`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`, `.editorconfig`, and `.gitattributes`.
- Removed the dead `info.py` diagnostic (only used by the deleted legacy
  `genie.sh`).
- Cleaned regenerable build/test artifacts (venv, `dist`, egg-info, caches,
  test `PEM` key) from the working tree.

---

## Deployment & testing overhaul — 2026-08-01

### 🚀 COMPLETED: pytest-only testing system
- Replaced the legacy `nose2` / junitxml pipeline. Removed `aftermath.py` and
  the committed `nose2-junit_py2.xml` / `nose2-junit_py3.xml` artifacts.
- Tests migrated to pytest-native modules under `nucosCR/test/`
  (`test_crypto_aes.py`, `test_crypto_rsa.py`, `test_cli.py`), discovered via
  `pyproject.toml` (`[tool.pytest.ini_options]` with `testpaths` +
  `pythonpath`).
- Coverage extended from 8 → **21 tests**: AES round-trip + `{`-suffix
  plaintext + self-describing blob shape, tamper and wrong-password detection,
  salted-hash verify, legacy-hash migration, RSA key permissions + round-trip +
  tamper rejection, file-I/O helpers, CLI encrypt/decrypt round-trip, and CLI
  tamper rejection. All passing.

### 🚀 COMPLETED: modern deployment
- Target platform raised to **Python 3.10+** (`python_requires=">=3.10"`,
  classifiers updated to 3.10–3.13; py2/py3.5 references dropped).
- `genie.sh` rewritten for modern tooling: creates a `venv`, builds sdist +
  wheel with `python -m build`, installs, and runs `pytest` (`clean`/`build`/
  `test`/`all` subcommands). The old conda multi-Python + Jenkins-junit driver
  was removed.
- Added `pyproject.toml` (PEP 517 build backend + pytest config); removed the
  deprecated `setup.cfg` `description-file`; `setup.py` now reads the README for
  `long_description`.
- `scripts/aes-cp` shebang changed to `#!/usr/bin/env python3`.
- `MANIFEST.in` updated to ship docs and tests in the sdist.

---

## [0.3.0] — 2026-08-01

### 🚀 COMPLETED: Authenticated AES (GCM) with self-describing format
- `CryptoAESBase.encryption()` now uses **AES-GCM** (`encrypt_and_digest` /
  `decrypt_and_verify`) so ciphertext is authenticated and tampering is
  detected, replacing the previous unauthenticated EAX misuse.
- Introduced a single self-describing blob
  `base64("NC1" + salt + nonce + tag + ciphertext)`; the separate nonce/tag
  bookkeeping is no longer required.
- Replaced fixed-`{}` padding with **PKCS7** padding, fixing corruption of any
  plaintext ending in `{`.
- AES keys are now derived with **salted PBKDF2-HMAC-SHA256** instead of a bare
  unsalted SHA-256.
- **Backward compatibility**: legacy pre-0.3 EAX-encoded blobs still decrypt by
  passing the stored `nonce` to `decryption()`.

### 🚀 COMPLETED: Salted password hashing with legacy/migration support
- `hexdigest(s)` and `hexdigest_n(s, n)` now accept a `legacy=True/False` flag
  (default `False`). The new default returns a salted, self-describing
  `pbkdf2-sha256$<iter>$<salt>$<digest>` hash; `legacy=True` reproduces the old
  unsalted single-round SHA-256 digest so existing stored hashes keep
  validating and login does not break.
- Added `verify_hexdigest(secret, stored) -> (valid, needs_rehash)` so callers
  can transparently migrate legacy credentials to the new format on the next
  successful login.

### 🚀 COMPLETED: RSA hardening
- `CryptoRSABase` upgraded the digest from deprecated SHA-1 to **SHA-256**.
- Private keys are written with mode `0600` instead of the default permissive
  permissions.
- Removed class-level mutable state (`fullkey`/`filename`) so instances are
  constructed per-use and are no longer shared/racy; `path` is configurable.

### 🚀 COMPLETED: CLI & packaging fixes
- `scripts/aes-cp` fixed a latent bug that attempted to write the
  `(blob, nonce)` tuple to disk; it now writes the single self-describing blob
  and checks decryption success before writing output.
- The CLI passes the raw password to `CryptoAESBase` (the class performs its
  own salted KDF), keeping it deterministic across encrypt/decrypt runs.
- `setup.py`: corrected `url`/`download_url` to `NuCOS/nucosCR`, raised the
  `Development Status` classifier to `3 - Alpha`, expanded Python classifiers
  to 3.5–3.12 with `python_requires`, removed the dead `doc` `data_files` walk,
  and the package now requires `pycryptodomex`.
- Version bumped 0.2.8 → **0.3.0**.

### 🚀 COMPLETED: Docs & tests
- Rewrote `README.md` around the pycryptodomex backend, the new AWS AES
  format, and the `legacy`/`verify_hexdigest` migration story.
- Expanded unit tests: tampering is now detected, `{`-suffix plaintext
  round-trips, salted hashes verify, and legacy hashes report `needs_rehash`.
- Added this `CHANGELOG.md` and refreshed `docs/STATUS_REPORT.md`.

---

## [0.2.8] — previous release
- Legacy release on the pycrypto/pycryptodomex boundary.
- Unauthenticated EAX AES, fixed-character padding, unsalted SHA-256 hashing,
  SHA-1 in RSA. See `docs/STATUS_REPORT.md` (historical sections) for the
  assessment that motivated the 0.3.0 changes.
