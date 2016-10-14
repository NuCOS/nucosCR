from __future__ import print_function
import unittest
import sys, random
sys.path.append('../')

from cryptorsabase import CryptoRSABase

global c

class UTestCryptoRSABase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global c
        c = CryptoRSABase()

    def test_create_rsa_key(self):
        global c
        name = "admin"
        key1 = c.create_rsa_key(name)
        key2 = c.get_key_by_file(name)
        #print (key1, key2)
        self.assertEqual(key1, key2)
        
    def test_encrypt(self):
        global c
        name = "admin"
        hexkey = c.get_hex_key(name)
        print(hexkey)    
        txt = "message"
        en = c.encrypt(txt, hexkey)
        #print txt, en
        de = c.decrypt(name, en)
        self.assertEqual(txt, de)
        
if __name__ == '__main__':
    unittest.main()
