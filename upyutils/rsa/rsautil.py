from rsa import PrivateKey, pkcs1


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
