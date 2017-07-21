.. _basic_usage:

Basic Usage
===========

.. sidebar:: Short

    - There are two classes: *CryptoRSABase* and *CryptoAESBase* 
    - The principle usage is shown in the tests

.. index:: Basic Usage

RSA-Suite
---------

To work with the RSA-Suite you should import the following

.. code-block:: python

    from nucosCR import CryptoRSABase

A usual working example for creating a public-private key file would be

.. code-block:: python

    c = CryptoRSABase()
    name = "test_admin"
    key1 = c.create_rsa_key(name)

Internally the PEM-files are stored in a folder relative to the working directory called *./PEM*. The full key can be read with the function *get_key_by_file*.
The *name* is always the reference to the key. It can be any *string*. 

After creating the key, it can be checked by

.. code-block:: python

    key2 = c.get_key_by_file(name)
    assertEqual(key1, key2)


An example for en- and decoding with the previously generated key would be 

.. code-block:: python

    name = "test_admin"
    hexkey = c.get_hex_key(name)    
    txt = b"my own secret message"
    #encryption with
    en = c.encrypt(txt, hexkey)
    #decryption with
    de = c.decrypt(name, en)
    assertEqual(txt, de)

Note here, that for *encryption* only the public part of the key must be used, which is here represented in hex. For *decryption* the full key is needed, so it is
referenced here with its *name*.

AES-Suite
---------

To work with the AES-Suite you should import the following

.. code-block:: python

    from nucosCR import CryptoAESBase

A usual working example would be

.. code-block:: python

    c = CryptoAESBase("secret")
    text = b"my message"
    #encryption with
    en = c.encryption(text)
    #decryption with
    de = c.decryption(en)
    self.assertEqual(text, de)

The class works internally with *bytes* and so does the decryption produce bytes as a result. For convenience the passed argument in the
encryption function may also be *string*.

The class is instanciated with a password (in our example case *secret*). Internally the password is digested with SHA256 into a much longer passphrase.

Copy-Script
-----------

This package provide a copy-script for copying a file or folder to a destination file or folder. During copying the script encrypts the data with the aes-algorithm.
If the source is a folder, it is copied recursively into the the destination. The usage is

.. code::

    aes-cp [-e ,-d ,-c, -o] source destination

-e source destination encryption copy

-d source destination decryption copy

-c file1 file2 check crc

-o overwrite flag (default is not overwrite), if set it overwrites the files in the destination

Before the copy process starts the user is prompted for a password. 

