#!/usr/bin/env bash
# Modern build / test / deploy driver for nucosCR.
#
# Uses only current tooling (Python 3.10+, venv, `python -m build`, pytest).
# Replaces the legacy conda/py2.7/nose2/Jenkins-junit pipeline (which was
# removed along with aftermath.py and the nose2-junit xml artifacts).
#
# Usage:
#   ./genie.sh            # full: build sdist+wheel, install, run pytest
#   ./genie.sh build      # build sdist + wheel into dist/
#   ./genie.sh test       # run pytest
#   ./genie.sh clean      # remove venv/, dist/, build/, *.egg-info, caches

set -euo pipefail

PACKAGE="nucosCR"
VENV="${VENV:-.venv}"
PYTHON="${PYTHON:-python3}"

info() {
  printf '\n\033[1;36m==> %s\033[0m\n' "$*"
}

require_py310() {
  if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
    echo "error: Python 3.10+ is required (found: $("$PYTHON" --version 2>&1))" >&2
    exit 1
  fi
}

ensure_venv() {
  if [ ! -d "$VENV" ]; then
    info "creating virtualenv: $VENV"
    "$PYTHON" -m venv "$VENV"
  fi
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install --upgrade build pytest
}

cmd_clean() {
  info "clean: removing $VENV dist/ build/ *.egg-info caches"
  rm -rf "$VENV" dist build "${PACKAGE}.egg-info" .pytest_cache
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
}

cmd_build() {
  require_py310
  ensure_venv
  info "building sdist + wheel with python -m build"
  python -m build
  info "artifacts in dist/:"
  ls -1 dist
}

cmd_test() {
  require_py310
  ensure_venv
  info "installing package (editable) and running pytest"
  python -m pip install -e .
  python -m pytest
}

cmd_full() {
  cmd_clean
  cmd_build
  info "installing built wheel into a fresh venv and running pytest"
  rm -rf "$VENV"
  ensure_venv
  python -m pip install dist/*.whl
  python -m pytest
  info "done."
}

case "${1:-all}" in
  clean)   cmd_clean ;;
  build)   cmd_build ;;
  test)    cmd_test ;;
  all)     cmd_full ;;
  *) echo "usage: $0 [build|test|all|clean]" >&2; exit 2 ;;
esac
