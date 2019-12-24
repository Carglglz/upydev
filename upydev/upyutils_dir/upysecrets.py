#!/usr/bin/env python

from ubinascii import hexlify, unhexlify
from machine import unique_id
import uos
import urandom
import hashlib
import ucryptolib
import json
import gc
import sys
import io

aZ09 = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def load_key(p_key=False):
    id = hexlify(unique_id()).decode()
    buff_key = b''
    with open('upy_pub_rsa{}.key'.format(id), 'rb') as keyfile:
        while True:
            try:
                buff = keyfile.read(2000)
                if buff != b'':
                    buff_key += buff
                else:
                    break
            except Exception as e:
                print(e)
    if p_key:
        print(buff_key)
    return buff_key


def upy_keygen(rsa_key, token, save_pass=True):
    if sys.platform == 'esp8266':
        raw_key_list = [line.encode() for line in rsa_key.decode().split('\n')[1:-2]]
    else:
        raw_key_list = [line for line in rsa_key.splitlines()[1:-1]]
    raw_key = b''
    for line in raw_key_list:
        raw_key += line
    random_token = token[:32]
    for b in random_token:
        raw_key += bytes(chr(raw_key[b]), 'utf-8')
    key_hash = hashlib.sha256()
    key_hash.update(raw_key)
    hashed_key = key_hash.digest()
    index_key = token[32:40]
    password_long = bytes([hashed_key[val] for val in index_key])
    password_short = bytes([aZ09[val % len(aZ09)] for val in password_long]).decode()

    if save_pass:
        with open('webrepl_cfg.py', 'wb') as wr_config:
            wr_config.write(bytes("PASS = '{}'\n".format(password_short), 'utf-8'))
    print('New password saved in the device!')
    return (password_short)


def upy_session_keygen(rsa_key, save_sessionkey=False, token=None):
    if sys.platform == 'esp8266':
        raw_key_list = [line.encode() for line in rsa_key.decode().split('\n')[1:-2]]
    else:
        raw_key_list = [line for line in rsa_key.splitlines()[1:-1]]
    raw_key = b''
    for line in raw_key_list:
        raw_key += line
    if token is None:
        random_token = uos.urandom(32) # send this
    else:
        random_token = token[:32]
    for b in random_token:
        raw_key += bytes(chr(raw_key[b]), 'utf-8')
    key_hash = hashlib.sha256()
    key_hash.update(raw_key)
    hashed_key = key_hash.digest()
    if token is None:
        if sys.platform == 'esp8266':
            index_pvkey = [urandom.getrandbits(4)+urandom.getrandbits(4) for i in range(32)]
        else:
            index_pvkey = [urandom.randrange(0, len(hashed_key)) for i in range(32)] # send this
    else:
        index_pvkey = token[32:64]
    pv_key = bytes([hashed_key[val] for val in index_pvkey])
    if token is None:
        if sys.platform == 'esp8266':
            index_ivkey = [urandom.getrandbits(4)+urandom.getrandbits(4) for i in range(16)]
        else:
            index_ivkey = [urandom.randrange(0, len(hashed_key)) for i in range(16)] # send this
    else:
        index_ivkey = token[64:]
    iv = bytes([hashed_key[val] for val in index_ivkey])

    if save_sessionkey:
        if token is None:
            with open('session.key', 'wb') as sess_config:
                sess_keys = dict(SKEY=pv_key, IV=iv)
                sess_config.write(json.dumps(sess_keys))
            print('New session.key saved in the device!')
        else:
            id = 'session{}.key'.format(hexlify(unique_id()).decode())
            with open(id, 'wb') as sess_config:
                sess_keys = dict(SKEY=pv_key, IV=iv)
                sess_config.write(json.dumps(sess_keys))
            print('New {} saved in the device!'.format(id))
    if token is None:
        return (pv_key, iv, [random_token + bytes(index_pvkey) + bytes(index_ivkey)])
    else:
        return (pv_key, iv)


class CRYPTOGRAPHER:
    def __init__(self, mode=2, key_enc=None, iv_enc=None, key_dec=None,
                 iv_dec=None, load_keys=False, buffer_size=2048):
        self.sess_keyfile_dev = 'session.key'
        self.sess_keyfile_host = 'session{}.key'.format(hexlify(unique_id()).decode())
        self.mode = mode
        self.block_len = 0
        self.key_e = key_enc
        self.iv_e = iv_enc
        self.msg_hex = b''
        self.buff = bytearray(buffer_size)
        self.buff_size = buffer_size
        self.err_buff = io.StringIO(100)
        self.buff_out = io.StringIO(500)
        self.gbls = globals()
        self.wrepl = None
        self.buff_crepl = None
        self.message_out = ''
        self.data_bytes = bytearray(20)
        self.rec_msg = ''
        self.resp_msg = ''
        if key_dec is None:
            self.key_d = key_enc
            self.iv_d = iv_enc
        else:
            self.key_d = key_dec
            self.iv_d = iv_dec
        if load_keys:
            try:
                with open(self.sess_keyfile_dev, 'r') as sess_config:
                    sess_keys_dev = json.load(sess_config)
                    self.key_e = sess_keys_dev['SKEY']
                    self.iv_e = sess_keys_dev['IV']

                with open(self.sess_keyfile_host, 'r') as sess_config:
                    sess_keys_host = json.load(sess_config)
                    self.key_d = sess_keys_host['SKEY']
                    self.iv_d = sess_keys_host['IV']
            except Exception as e:
                print('No session keys found in the device')
                pass

        self.enc = ucryptolib.aes(self.key_e, self.mode, self.iv_e)
        self.dec = ucryptolib.aes(self.key_d, self.mode, self.iv_d)

    def decrypt(self, msg):
        self.buff[:] = bytearray(self.buff_size)
        self.dec = ucryptolib.aes(self.key_d, self.mode, self.iv_d)
        self.dec.decrypt(msg, self.buff)
        gc.collect()
        return self.buff.decode().split('\x00')[0]

    def encrypt(self, msg):
        self.buff[:] = bytearray(self.buff_size)
        self.enc = ucryptolib.aes(self.key_e, self.mode, self.iv_e)
        self.data_bytes = msg.encode()
        self.block_len = len(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16))
        self.enc.encrypt(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16), self.buff)
        gc.collect()
        return bytes(self.buff[:self.block_len])

    def decrypt_hex(self, msg):
        self.msg_hex = unhexlify(msg)
        self.buff[:] = bytearray(self.buff_size)
        self.dec = ucryptolib.aes(self.key_d, self.mode, self.iv_d)
        self.dec.decrypt(self.msg_hex, self.buff)
        gc.collect()
        return self.buff.decode().split('\x00')[0]

    def encrypt_hex(self, msg):
        self.buff[:] = bytearray(self.buff_size)
        self.enc = ucryptolib.aes(self.key_e, self.mode, self.iv_e)
        self.data_bytes = msg.encode()
        self.block_len = len(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16))
        self.enc.encrypt(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16), self.buff)
        gc.collect()
        return hexlify(bytes(self.buff[:self.block_len]))

    def encrypt_hex_bytes(self, msg):
        self.buff[:] = bytearray(self.buff_size)
        self.enc = ucryptolib.aes(self.key_e, self.mode, self.iv_e)
        self.data_bytes = msg
        self.block_len = len(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16))
        self.enc.encrypt(self.data_bytes + b'\x00' * ((16 - (len(self.data_bytes) % 16)) % 16), self.buff)
        gc.collect()
        return hexlify(bytes(self.buff[:self.block_len]))

    def recv_send(self, msg):
        rec_msg = self.decrypt_hex(msg)
        return self.encrypt_hex(rec_msg)

    def crepl(self, msg):
        self.rec_msg = self.decrypt_hex(msg)
        self.buff_out = io.StringIO(500)
        try:
            self.wrepl = uos.dupterm(self.buff_out, 0)
            self.resp_msg = eval(self.rec_msg)
            # self.buff_crepl = uos.dupterm(self.wrepl, 0)
            if self.resp_msg is None:
                self.message_out = self.buff_out.getvalue()
                self.buff_crepl = uos.dupterm(self.wrepl, 0)
                if self.message_out == '':
                    gc.collect()
                    return None
                else:
                    return self.encrypt_hex(self.message_out)
            else:
                self.buff_crepl = uos.dupterm(self.wrepl, 0)
                return self.encrypt_hex(str(self.resp_msg))
        except Exception as e:
            try:
                # self.buff_crepl = uos.dupterm(self.wrepl, 0)
                exec(self.rec_msg, self.gbls)
                self.message_out = self.buff_out.getvalue()
                self.buff_crepl = uos.dupterm(self.wrepl, 0)
                if self.message_out == '':
                    gc.collect()
                    return None
                else:
                    return self.encrypt_hex(self.message_out)
            except Exception as e:
                self.buff_crepl = uos.dupterm(self.wrepl, 0)
                sys.print_exception(e, self.err_buff)
                self.resp_msg = self.err_buff.getvalue()
                self.err_buff.seek(0)
                return self.encrypt_hex(self.resp_msg)

# TODO: ENCRYPT/DECRYPT FILE

# TODO: DECRYPT/ENCRYPT MESSAGE

# TODO: WCRYPL (WEB CRYTO REPL)
