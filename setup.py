#!/usr/bin/env python
"""Package definition for nucosCR.

Modern build: ``python -m build`` from a fresh Python 3.10+ venv.
Tests: ``pytest`` (see pyproject.toml).
"""
from setuptools import setup

import os
import sys

name = "nucosCR"

ROOT = os.path.abspath(os.path.dirname(__file__))


def long_description():
    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        with open(readme, "r", encoding="utf-8") as f:
            return f.read()
    return "nucosCR - convenient python crypto-tools"


if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10 or later is required!")

# Version is centralised in nucosCR/version.py (PEP 440).
with open(os.path.join(name, "version.py"), encoding="utf-8") as f:
    exec(f.read())
print("Version:", version)

# Console scripts (bat wrappers included for Windows builds).
scripts = []
for dirname, dirnames, filenames in os.walk("scripts"):
    for filename in filenames:
        if not filename.endswith(".bat"):
            scripts.append(os.path.join(dirname, filename))
if "sdist" in sys.argv or os.name in ["ce", "nt"]:
    for dirname, dirnames, filenames in os.walk("scripts"):
        for filename in filenames:
            if filename.endswith(".bat"):
                scripts.append(os.path.join(dirname, filename))

setup(
    name=name,
    version=version,
    description="nucosCR - convenient python crypto-tools",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/NuCOS/nucosCR",
    download_url="https://github.com/NuCOS/nucosCR/tarball/{0}".format(version),
    author="Oliver Braun",
    author_email="oliver.braun@nucos.de",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="cryptography",
    packages=["nucosCR"],
    scripts=scripts,
    install_requires=["pycryptodomex"],
    include_package_data=True,
    python_requires=">=3.10",
)
