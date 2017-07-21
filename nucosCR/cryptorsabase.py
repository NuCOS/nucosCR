from __future__ import print_function
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
import binascii, os, sys

#_path_ = os.path.dirname(os.path.abspath(__file__))
_path_ = os.getcwd()

ispython3 = sys.version_info > (3, 0)

if ispython3:
    def unicoding(x):
        #print(type(x),x[0])
        if type(x) is bytearray:
            return x.decode()
        elif type(x) is bytes:
            return x.decode()
        elif type(x) is str:
            return x
        else:
            return x
               
else: 
    def unicoding(x):
        if type(x) is bytearray:
            return unicode(x) #better use decode here?
        elif type(x) is bytes:
            return unicode(x) #better use decode here?
        elif type(x) is str:
            x = x.decode()
            return x
        elif type(x) is unicode:
            return x
        else:
            return x


class CryptoRSABase():
    """
    Class is based on bytes as in- and output. Nevertheless tolerant against unicode and string input.
    """
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
            f.write(unicoding(key.exportKey('PEM')))
        return key

    def get_key_by_file(self, name):
        self.filename = ''.join([self.path,"/",name,'_localkey.pem'])
        if not os.path.exists(self.filename):
            self.create_rsa_key(name)
        with open(self.filename, 'r') as f:
            key_txt = f.read()
        self.fullkey = key = RSA.importKey(key_txt)
        return key

    def get_hex_key(self, name):
        if not self.fullkey:
            self.get_key_by_file(name)
        return unicoding(binascii.hexlify(self.fullkey.publickey().exportKey('DER')))
        
    def random(self,n):
        out = Random.new()
        number = out.read(n)
        hexnumber = binascii.hexlify(number)
        return hexnumber

    def encrypt(self,message,hexkey):
        if not type(message) is bytes:
            message = message.encode()

        h = SHA.new(message)

        key = RSA.importKey(binascii.unhexlify(hexkey))
        cipher = PKCS1_v1_5.new(key)
        tail = h.digest()
        return cipher.encrypt(message+tail)

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
            return message[:-dsize]
        else:
            #print ("Encryption was not correct.")
            return message[:-dsize]
       

            
