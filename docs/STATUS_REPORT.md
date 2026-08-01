# STATUS_REPORT — nucosCR

**Last updated**: 2026-08-01
**Branch**: master (clean working tree, in sync with origin/master)
**Version**: 0.3.0 (`nucosCR/version.py`)
**Stage**: Alpha (`Development Status :: 3 - Alpha`)

> **Update 0.3.0**: The weaknesses and urgent fixes below (from the original
> review) have been addressed: AES is now authenticated GCM + PKCS7 with a
> salted KDF, password hashing migrated to a salted self-describing format with
> a `legacy=` flag and `verify_hexdigest`, RSA hardened (SHA-256, 0600 perms,
> instance state), and packaging/CLI/docs fixed. See `CHANGELOG.md`. The
> "original findings" below are retained for historical context.

A small Python cryptography toolbox built on **pycryptodomex** (`Cryptodome`
namespace). Provides AES (+ file utils) and RSA helpers plus a CLI file
encryption/copy tool (`scripts/aes-cp`).

---

## Design Principles

- **Simplicity / convenience over completeness.** The library is a thin,
  ergonomic wrapper around a trusted backend (pycryptodomex). No crypto is
  implemented from scratch.
- **Bytes-first with tolerance.** Public API accepts `bytes` or `str` and
  normalizes internally (see `CryptoAESBase`, `CryptoRSABase` docstrings).
- **Self-contained file helpers.** `read_from_file` / `write_to_file` /
  `get_crc_from_file` bundle common I/O next to the crypto primitives.
- **Module-level convenience exports.** `__init__.py` re-exports the classes
  and utility functions so callers can do `from nucosCR import CryptoAESBase`.
- **CLI parity with the library.** `scripts/aes-cp` exercises the same classes
  used by programmatic callers, keeping the two paths in sync.
- **Cross-version intent.** Code carries Python 2/3 branching (`cryptorsabase.py`
  `ispython3`), though Python 2 support is effectively legacy.

---

## Weaknesses

### Crypto / Security
1. **AES uses an AEAD mode but never authenticates.** `CryptoAESBase.encryption`
   uses `AES.MODE_EAX` but calls `cipher.encrypt(...)` without
   `encrypt_and_digest()`, and `decryption` never verifies a tag. Only the nonce
   is returned/propagated. This drops EAX integrity/authentication guarantees —
   tamper detection is effectively absent. (`cryptoaesbase.py`)
2. **Non-standard padding.** Padding is a fixed character `b"{"` and decryption
   does `rstrip(self.PADDING)`. Any plaintext ending in `{` is corrupted on
   decrypt, and the scheme is not PKCS7. (`cryptoaesbase.py`)
3. **Weak key derivation — no salt/KDF.** AES key is a single unsalted
   `SHA256(passwd)`; `hexdigest_n` does naive repeated hashing. No PBKDF2/scrypt,
   no salt, so low-entropy passwords are weak and the scheme is non-standard.
   (`cryptoaesbase.py`, used by `scripts/aes-cp`)
4. **Legacy/deprecated hashing in RSA.** `cryptorsabase.py` uses `SHA` (SHA-1)
   for message digest and `PKCS1_v1_5`. Functional, but SHA-1 is weak and
   flagged by modern tooling.
5. **Weak key-management defaults.** `CryptoRSABase` stores keys under
   `os.getcwd()/PEM` with a fixed `localkey.pem` naming convention, writes them
   with `0644` semantics (no permission tightening), and reuses class-level
   mutable state (`fullkey`, `filename`), which is **not thread-safe**.
6. **`random()` returns hex, not raw bytes.** `random(n)` hexlifies
   `Random.read(n)`, so the byte length is 2× the requested `n`. Callers (tests,
   CLI) treat the result as raw bytes — surprising and inconsistent.

### Engineering / Maintainability
7. **Setup metadata inconsistencies.** `setup.py` points `url`/`download_url` at
   `DocBO/nucosCR` while the README points at `NuCOS/nucosCR`; classifiers claim
   `1 - Planning` and Python ≤3.8 while the code/version have moved past that.
8. **Dead/stale packaging code.** `setup.py` walks a `doc` folder for
   `data_files` but the folder is `docs` (dead on every install), and
   `test_suite='setup.my_test_suite'` references a non-importable symbol.
9. **Outdated README.** Still documents the old `pycrypto` backend and win
   wheels; `install_requires` is `pycryptodomex`. Docs and code disagree on the
   backend story.
10. **Minimal test coverage.** Only two small `unittest` files; no CI config in
    the repo, no coverage, no negative/tamper tests (which is notable given the
    missing EAX authentication).
11. **Documentation drift.** `docs/` is empty; sphinx sources live in `sphinx/`
    and reference a hosted readthedocs build. No CHANGELOG present.

---

## Urgent Fixes (priority order)

1. **Authenticate AES properly (HIGH).** Either commit to EAX and store+verify
   the tag (use `encrypt_and_digest` / `decrypt_and_verify`), or switch to
   `MODE_GCM` / `MODE_OPENPGP` and return `nonce + tag + ciphertext` as a single
   blob. This is the single largest correctness/security gap.
2. **Replace fixed-character padding (HIGH).** Use PKCS7 (`pad`/`unpad`) so
   plaintext byte collisions on `{` no longer corrupt data.
3. **Fix key derivation (MEDIUM).** Add a salted KDF (e.g.
   `Crypto.Protocol.KDF.PBKDF2` or scrypt) with a stored salt/iteration count on
   both AES and the CLI path.
4. **Align packaging metadata (MEDIUM).** Fix `url`/`download_url`, bump
   classifiers to actual Python support, point `data_files` at the real docs
   folder (or drop it), and correct/remove the broken `test_suite`.
5. **Harden RSA (MEDIUM).** Move off SHA-1 (use SHA256 in
   `Crypto.Signature`/hash-based integrity), tighten file permissions on written
   keys, and remove class-level mutable state for thread safety.
6. **Update README + docs (LOW/MEDIUM).** Replace pycrypto/win-wheel text with
   the pycryptodomex reality and add a CHANGELOG.

---

## Recommendations

- Move AES to a single-argument, self-describing ciphertext format
  (`nonce || tag || ct`) so keys are the only thing callers must manage.
- Add a CI matrix (the repo has no CI; `requirements`/`tox` absent) and expand
  tests to cover round-trip via the CLI, tamper/negative cases, and Unicode
  inputs with non-`{` endings.
- Reset/migrate `sphinx/` so `docs/` can host the source and a CHANGELOG rather
  than pointing only at an external build.
- Before any public release, run a security pass (e.g. `bandit`) and re-verify
  the algorithm choices against pycryptodomex's current API (EAX/GCM usage).

---

## Build / Test State

- Backend: `pycryptodomex` (`from Cryptodome ...`), consistent between package
  code, tests, and CLI.
- **Testing: pytest-only.** The legacy nose2 / junitxml pipeline and its
  artifacts (`aftermath.py`, `nose2-junit_py2/py3.xml`) were removed. Tests live
  in `nucosCR/test/` as pytest-native modules (`test_crypto_aes.py`,
  `test_crypto_rsa.py`, `test_cli.py`) and are discovered via `pyproject.toml`
  (`testpaths` + `pythonpath`). **21 tests** cover AES round-trip, `{`-suffix
  plaintext, tamper/wrong-password detection, salted-hash verify, legacy-hash
  migration, RSA key perms + round-trip + tamper, file I/O, the CLI
  encrypt/decrypt round-trip, and CLI tamper rejection.
- **Deployment: modern tooling.** `genie.sh` builds sdist + wheel via
  `python -m build` and runs `pytest` inside a Python 3.10+ `venv`; package
  metadata is defined in `setup.py`/`pyproject.toml` with
  `python_requires=">=3.10"`. The old conda py2.7/py3.5 pipeline was removed.
- Remaining follow-ups: add CI, coverage, and concurrency tests; finish
  migration of the sphinx sources into `docs/`.
