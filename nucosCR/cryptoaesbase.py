# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 11:19:37 2014

@author: BRAUOLI
"""
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome import Random
#base64 is used for encoding. dont confuse encoding with encryption#
#encryption is used for disguising data
#encoding is used for putting data in a specific format
import base64, os, binascii
# os is for urandom, which is an accepted producer of randomness that
# is suitable for cryptology.
#import os

def hexdigest(s):
    h = SHA256.new()
    if not type(s) == bytes:
        h.update(s.encode('utf8'))
    else:
        h.update(s)
    return h.hexdigest()

def hexdigest_n(s, n_max):
    for n in range(n_max):
        s = hexdigest(s)
    return s

def read_from_file(filename):
    with open(filename, "rb") as in_file:
        data = in_file.read()
    return data

def write_to_file(filename, data, chunksize=8192):
    """
    Write bytes from data into file
    
    :param filename: name of file
    :param data: list with data (turned into bytearrays)
    :param chunksize: the bit-size which is transmitted at once
    """
    with open(filename, "wb") as f:
        loc = 0
        length = len(data)
        while True:
            if loc+chunksize < length:
                #print filename, loc, length
                chunk=data[loc:loc+chunksize]
                f.write(chunk)
                loc += chunksize
            else:
                chunk=data[loc:length]
                f.write(chunk)
                break
            
def get_crc_from_file(filename):
    if os.path.exists(filename):
        data = read_from_file(filename) #filename includes the path of the origin
        return binascii.crc32(data)
    
def random(n):
    out = Random.new()
    number = out.read(n)
    hexnumber = binascii.hexlify(number)
    return hexnumber

class CryptoAESBase():
    """
    class is based on bytes as input and output. Nevertheless tolerant against unicode and string input.
    """
    def __init__(self, passwd):
        if not type(passwd) is bytes:
            self.passwd = passwd.encode()
        else:
            self.passwd = passwd
        myhash = SHA256.new()
        myhash.update(self.passwd)
        self.key = myhash.digest()
        self.PADDING = b"{"
        
    def encryption(self, pI):
        # the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
        BLOCK_SIZE = 16
        cipher = AES.new(self.key, AES.MODE_EAX)
        if not type(pI) is bytes:
            unipI = pI.encode()
        else:
            unipI = pI
            
        self.pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * self.PADDING
        # encrypt with AES, encode with base64
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(self.pad(s)))
        
        encoded = EncodeAES(cipher, unipI)
        return encoded, cipher.nonce
    
    def decryption(self, encryptedBytes, nonce):
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
        success = True
        #try:
        decodedBytes = DecodeAES(cipher, encryptedBytes)
        #except:
        #    decodedBytes = encryptedBytes
        #    print("seems not to be encrypted!", decodedBytes)
        #    success = False
        return decodedBytes, success

