# Security Policy

nucosCR is a cryptography toolkit currently in **alpha**. Cryptographic code
must be held to a high bar, so please report vulnerabilities even if they seem
minor.

## Reporting a vulnerability

**Do not open a public GitHub issue for security problems.** Instead, report
privately to the maintainers by email:

- **Contact**: Oliver Braun — [oliver.braun@nucos.de](mailto:oliver.braun@nucos.de)

Please include:
- the affected version(s),
- a description of the issue and its impact,
- a minimal, self-contained reproduction if possible.

You will receive an acknowledgement. We aim to respond within a reasonable
timeframe and to coordinate a fix before any public disclosure.

## Supported versions

Only the latest release is actively supported. Given the alpha stage, users
should generally run the newest version.

## Security notes for users

- This is **alpha** software: use it at your own risk.
- Passwords are derived with a salted KDF (`PBKDF2-HMAC-SHA256`) via
  `hexdigest` (default) / AES key derivation.
- AES encryption is authenticated (GCM). Decryption reports failure on
  tampering or a wrong password; always check the returned `success` flag.
- For migration of legacy unsalted `hexdigest` values, use `verify_hexdigest`
  (see the README) rather than storing plaintext.

## Disclosure

If we fix a vulnerability, we will note it in `CHANGELOG.md` and, where
appropriate, credit the reporter (unless anonymity is requested).
