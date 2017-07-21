# nucosCR 
*nucosCR* is a convenient cryptography module in python, works as a working toolbox for the module *pycrypto*.
This module is in alpha stage, any usage is on your own risk and responsibility.

## Install
```
pip install nucosCR
```
or download the tarball at [https://github.com/DocBO/nucosCR](https://github.com/DocBO/nucosCR), unzip and type
```
python setup.py install
```

On MS Windows you may need the binaries for *pycrypto* if you do not have an appropriate compiler on your machine. The binaries can be downloaded from github (for 64 bit architecture):

```
pip install --use-wheel --no-index --find-links=https://github.com/sfbahr/PyCrypto-Wheels/raw/master/pycrypto-2.6.1-cp35-none-win_amd64.whl pycrypto
```

For different architectures see there.

## Documentation
[https://pythonhosted.org/nucosCR](https://pythonhosted.org/nucosCR)

## Recommended test runner
```
nose2 --plugin nose2.plugins.junitxml --junit-xml
```

## Licence
MIT License

## Platforms
No specific platform dependency. Python 2.7 should work as well as Python 3.4/3.5. Up to now only Linux OS is tested.

