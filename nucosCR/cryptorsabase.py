from __future__ import print_function
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
import binascii, os
import nucosMQ

_path_ = os.path.dirname(os.path.abspath(__file__))

class CryptoRSABase():
    fullkey = None
    extkey = None
    path = os.path.join(_path_,"PEM")
    filename = 'localkey.pem'
    
    def create_rsa_key(self, name):
        self.filename = ''.join([self.path,"/",name,'_localkey.pem'])
        self.fullkey = key = RSA.generate(2048)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with open(self.filename,'w') as f:
            f.write(nucosMQ.unicoding(key.exportKey('PEM')))
        return key

    def get_key_by_file(self, name):
        print("get key by file")
        self.filename = ''.join([self.path,"/",name,'_localkey.pem'])
        if not os.path.exists(self.filename):
            self.create_rsa_key(name)
        with open(self.filename, 'r') as f:
            key_txt = f.read()
        self.fullkey = key = RSA.importKey(key_txt)
        #now produce the public pair part
        #filename = ''.join([self.path,name,'_publickey.pem'])
        #with open (filename,'w') as f:
        #    f.write(key.publickey().exportKey('PEM'))
        return key

    def get_hex_key(self, name):
        if not self.fullkey:
            self.get_key_by_file(name)
        return nucosMQ.unicoding(binascii.hexlify(self.fullkey.publickey().exportKey('DER')))

    def set_hex_key(self, hextxt):
        self.extkey = key = RSA.importKey(binascii.unhexlify(hextxt))
        return True
        
    def random(self,n):
        out = Random.new()
        number = out.read(n)
        hexnumber = binascii.hexlify(number)
        return hexnumber

    def encrypt(self,message,hexkey):
        if not type(message) is bytes:
            message = message.encode()

        h = SHA.new(message)
        #try:
        key = RSA.importKey(binascii.unhexlify(hexkey))
        cipher = PKCS1_v1_5.new(key)
        tail = h.digest()
        return cipher.encrypt(message+tail)
        #except:
        #    print ("----- no hexkey ------")
        #    return None
        
    def decrypt(self,name,ciphertext):
        if not self.fullkey:
            self.get_key_by_file(name)
        cipher = PKCS1_v1_5.new(self.fullkey)
        dsize = SHA.digest_size
        sentinel = Random.new().read(20+dsize)      # Let's assume that average data length is 15
        message = cipher.decrypt(ciphertext, sentinel)
        digest = SHA.new(message[:-dsize]).digest()
        if digest==message[-dsize:]:                # Note how we DO NOT look for the sentinel
            #print ("Encryption was correct..",message[:-dsize])
            return nucosMQ.unicoding(message[:-dsize])
        else:
            #print ("Encryption was not correct.")
            return nucosMQ.unicoding(message[:-dsize])
        
