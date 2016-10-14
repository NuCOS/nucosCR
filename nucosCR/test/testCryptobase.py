from __future__ import print_function
import unittest
import sys
sys.path.append('../')

from cryptobase import Cryptonize, random

class UTestCryptonize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Cryptonize("test")

    def test_encrypt(self):
        text = random(80000)
        en = self.c.encryption(text)    
        de = self.c.decryption(en)
        self.assertEqual(text, de)
        
    
if __name__ == '__main__':
    unittest.main()
