from rsa import PrivateKey, PublicKey, pkcs1,


class RSAPrivateKey:
    def __init__(self, keyfile):
        with open(keyfile, 'rb') as kf:
            self.key = PrivateKey._load_pkcs1_pem(kf.read())

    def sign(self, message):
        sg = pkcs1.sign(message, self.key, 'SHA-256')
        return sg

    def signfile(self, file):
        with open(file, 'rb') as sigfile:
            sg = pkcs1.sign(sigfile.read().decode('utf-8'), self.key, 'SHA-256')
        return sg

    def decrypt(self, message):
        dec = pkcs1.decrypt(message, self.key)
        return dec


class RSAPublicKey:
    def __init__(self, keyfile):
        with open(keyfile, 'rb') as kf:
            self.key = PublicKey._load_pkcs1_pem(kf.read())

    def verify(self, message, signature):
        vf = pkcs1.verify(message, signature, self.key)
        return vf

    def verifyfile(self, file, sigfile):
        with open(file, 'rb') as vfile:
            with open(sigfile, 'rb') as sigfile:
                vf = pkcs1.verify(vfile.read(), sigfile.read(), self.key)
        return vf == 'SHA-256'

    def encrypt(self, message):
        enc = pkcs1.encrypt(message, self.key)
        return enc
