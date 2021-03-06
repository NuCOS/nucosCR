#!/usr/bin/env python
from __future__ import print_function

import os
import sys

#from distutils.core import setup
from setuptools import setup, find_packages

import unittest
#use of setup.py
# to distribute in pypi: python setup.py sdist upload -r pypitest/pypi
# to install locally: python setup.py install (builds the egg in side-packages)
#                     or better pip install -e ./

name = "nucosCR"


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(name,'test'), pattern='test*.py')
    return test_suite

rootdir = os.path.abspath(os.path.dirname(__file__))


long_description = """

Dokumentation: [http://nucoscr.readthedocs.io/]

"""

# Python 2.7 or later needed
if sys.version_info < (2, 7, 0, 'final', 0):
    raise SystemExit('Python 2.7 or later is required!')

# Build a list of all project modules
packages = []
for dirname, dirnames, filenames in os.walk(name):
        if '__init__.py' in filenames:
            packages.append(dirname.replace('/', '.'))

package_dir = {name: name}

# Data files used e.g. in tests
package_data = {} #{name: [os.path.join(name, 'tests', 'prt.txt')]}

# The current version number - MSI accepts only version X.X.X
exec(open(os.path.join(name, 'version.py')).read())
print("Version:", version)

# Scripts
scripts = []
for dirname, dirnames, filenames in os.walk('scripts'):
    for filename in filenames:
        if not filename.endswith('.bat'):
            scripts.append(os.path.join(dirname, filename))

# Provide bat executables in the tarball (always for Win)
if 'sdist' in sys.argv or os.name in ['ce', 'nt']:
    for dirname, dirnames, filenames in os.walk('scripts'):
        for filename in filenames:
            if filename.endswith('.bat'):
                scripts.append(os.path.join(dirname, filename))

# Data_files (e.g. doc) needs (directory, files-in-this-directory) tuples
data_files = []
for dirname, dirnames, filenames in os.walk('doc'):
        fileslist = []
        for filename in filenames:
            fullname = os.path.join(dirname, filename)
            fileslist.append(fullname)
        data_files.append(('share/' + name + '/' + dirname, fileslist))

setup(name=name,
      version=version,  # PEP440
      description='nucosCR - convenient python crypto-tools',
      long_description=long_description,
      url='https://github.com/DocBO/nucosCR',
      download_url = 'https://github.com/DocBO/nucosCR/tarball/0.0.1',
      author='Oliver Braun',
      author_email='oliver.braun@nucos.de',
      license='MIT',
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8'
      ],
      keywords='cryptography',
      packages=packages,
      package_dir=package_dir,
      package_data=package_data,
      scripts=scripts,
      data_files=data_files,
      test_suite='setup.my_test_suite', 
      install_requires=['pycryptodomex'],
      include_package_data=True,

      )
