#!/usr/bin/env python

from ubinascii import hexlify
from machine import unique_id
import uos
import urandom
import hashlib
import json
import sys


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
        random_token = uos.urandom(32)  # send this
    else:
        random_token = token[:32]
    for b in random_token:
        raw_key += bytes(chr(raw_key[b]), 'utf-8')
    key_hash = hashlib.sha256()
    key_hash.update(raw_key)
    hashed_key = key_hash.digest()
    if token is None:
        if sys.platform == 'esp8266':
            index_pvkey = [urandom.getrandbits(
                4)+urandom.getrandbits(4) for i in range(32)]
        else:
            index_pvkey = [urandom.randrange(0, len(hashed_key))
                           for i in range(32)]  # send this
    else:
        index_pvkey = token[32:64]
    pv_key = bytes([hashed_key[val] for val in index_pvkey])
    if token is None:
        if sys.platform == 'esp8266':
            index_ivkey = [urandom.getrandbits(
                4)+urandom.getrandbits(4) for i in range(16)]
        else:
            index_ivkey = [urandom.randrange(0, len(hashed_key))
                           for i in range(16)]  # send this
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
