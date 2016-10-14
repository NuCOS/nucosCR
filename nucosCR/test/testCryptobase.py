from __future__ import print_function
import unittest
import sys, random
sys.path.append('../')

from cryptobase import Cryptonize

global c

class UTestCryptonize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global c
        c = Cryptonize("test")

        
    def test_encrypt(self):
        global c
        text = b"alsdfjalskdfha"
        en = c.encryption(text)
        print(en)    
        de = c.decryption(en)
        
        self.assertEqual(text, de)
        
if __name__ == '__main__':
    unittest.main()
