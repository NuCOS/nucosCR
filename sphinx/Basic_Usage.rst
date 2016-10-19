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
    key1 = self.c.create_rsa_key(name)
    key2 = self.c.get_key_by_file(name)
    self.assertEqual(key1, key2)

Internally the PEM-files are stored in a folder relative to the working directory called *./PEM*. The full key can be read with the function *get_key_by_file*.
The *name* is always the reference to the key. It can be any *string*.


An example for en- and decoding with the previously generated key would be 

.. code-block:: python

    name = "test_admin"
    hexkey = self.c.get_hex_key(name)    
    txt = b"my own secret message"
    #encryption with
    en = self.c.encrypt(txt, hexkey)
    #decryption with
    de = self.c.decrypt(name, en)
    self.assertEqual(txt, de)


AES-Suite
---------

To work with the AES-Suite you should import the following

.. code-block:: python

    from nucosCR import CryptoAESBase

A usual working example would be

.. code-block:: python

    cr = CryptoAESBase("secret")
    text = b"my message"
    #encryption with
    en = self.c.encryption(text)
    #decryption with
    de = self.c.decryption(en)
    self.assertEqual(text, de)

The class works internally with *bytes* and so does the decryption produce bytes as a result. For convenience the passed argument in the
encryption function may also be *string*.

The class is instanciated with a password (in our example case *secret*). Internally the password is digested with SHA256 into a much longer passphrase.



