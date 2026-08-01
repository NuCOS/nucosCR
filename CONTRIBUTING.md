# Contributing to nucosCR

Thanks for taking the time to contribute! nucosCR is a small cryptography
toolbox and we want to keep it safe, simple and reliable.

## Getting started

1. Clone the repository.
2. Create a virtual environment with **Python 3.10+**:
   ```
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e . pytest
   ```
3. Run the test suite before and after your changes:
   ```
   pytest
   ```

## Development loop

- `./genie.sh test` — install editable and run pytest
- `./genie.sh build` — build sdist + wheel
- `./genie.sh all` — clean, build, install and test in a fresh venv

## Code & style guidelines

- Keep the public API small and consistent (bytes-first with `str` tolerance).
- Do **not** roll your own cryptography. Only use primitives from
  `pycryptodomex` and follow its current recommended usage.
- Add a test for any behaviour change, including failure/negative cases.
- Run `pytest` and ensure the whole suite is green.

## Commits & pull requests

- Write clear, focused commit messages.
- Open a pull request against `master`.
- Reference any related issue in the PR description.

## Reporting bugs

Open an issue with:
- the Python and `pycryptodomex` versions you use,
- a minimal reproduction,
- expected vs. observed behaviour.

If the issue is security-related, please follow the guidance in
[`SECURITY.md`](SECURITY.md) instead of opening a public issue.

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE.txt).
