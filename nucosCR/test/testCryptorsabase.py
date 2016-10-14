from __future__ import print_function
import unittest
import sys, random, os
sys.path.append('../')

from cryptorsabase import CryptoRSABase


class UTestCryptoRSABase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = CryptoRSABase()
        
    @classmethod
    def tearDownClass(cls):
        try:
            os.remove('../PEM/test_admin_localkey.pem')
        except:
            pass

    def test_create_rsa_key(self):
        name = "test_admin"
        key1 = self.c.create_rsa_key(name)
        key2 = self.c.get_key_by_file(name)
        #print (key1, key2)
        self.assertEqual(key1, key2)
        
    def test_encrypt(self):
        name = "test_admin"
        hexkey = self.c.get_hex_key(name)    
        txt = b"message"
        en = self.c.encrypt(txt, hexkey)
        de = self.c.decrypt(name, en)
        self.assertEqual(txt, de)
        
                

if __name__ == '__main__':
    unittest.main()
