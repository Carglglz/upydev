from rsa import PrivateKey, PublicKey, pkcs1
from rsa.pem import load_pem
import hashlib
from binascii import hexlify


class RSAPrivateKey:
    def __init__(self, keyfile):
        with open(keyfile, 'rb') as kf:
            self.key = PrivateKey._load_pkcs1_pem(kf.read())
            kf.seek(0)
            key_der = load_pem(kf.read(), b'RSA PRIVATE KEY')
            self.sz = len(bin(self.key.n)) - 2
            _hash = hashlib.sha256(key_der)
            _result = _hash.digest()
            self.id = hexlify(_result).decode('ascii').upper()[:40]

    def __repr__(self):
        return f'{self.sz} bits RSA Private key {self.id}'

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

    def _decrypt_passwd(self, passwd, save=True):
        _passwd = self.decrypt(passwd)
        if save:
            with open('webrepl_cfg.py', 'wb') as wr_config:
                wr_config.write(bytes("PASS = '{}'\n".format(_passwd.decode()),
                                      'utf-8'))


class RSAPublicKey:
    def __init__(self, keyfile):
        with open(keyfile, 'rb') as kf:
            self.key = PublicKey._load_pkcs1_pem(kf.read())
            kf.seek(0)
            key_der = load_pem(kf.read(), b'RSA PUBLIC KEY')
            self.sz = len(bin(self.key.n)) - 2
            _hash = hashlib.sha256(key_der)
            _result = _hash.digest()
            self.id = hexlify(_result).decode('ascii').upper()[:40]

    def __repr__(self):
        return f'{self.sz} bits RSA Public key {self.id}'

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
