from upydevice import Device
import sys
from upydev.helpinfo import see_help
from upydevice import check_device_type
import getpass
import os
import json
import upydev
from binascii import hexlify
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import string
import secrets
import hashlib
import netifaces
import socket
import locale
from datetime import datetime, timedelta
import shlex
import subprocess
import ipaddress


UPYDEV_PATH = upydev.__path__[0]

KEYGEN_HELP = """
> KEYGEN: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - gen_rsakey: To generate RSA-2048 bit key that will be shared with the device
                      (it is unique for each device) use -tfkey to send this key to the
                      device (use only if connected directly to the AP of the device or a
                      "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                      upload the key (it is stored in upydev.__path__) by USB/Serial connection.

        - rf_wrkey: To "refresh" the WebREPL password with a new random password derivated from
                    the RSA key previously generated. A token then is sent to the device to generate
                    the same password from the RSA key previously uploaded. This won't leave
                    any clues in the TCP Websocekts packages of the current WebREPL password.
                    (Only the token will be visible; check this using wireshark)
                    (This needs upysecrets.py)

        - sslgen_key: (This needs openssl available in $PATH)
                       To generate ECDSA key and a self-signed certificate to enable SSL sockets
                       This needs a passphrase, that will be required every time the key is loaded.
                       Use -tfkey to upload this key to the device
                       (use only if connected directly to the AP of the device or a
                       "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                       upload the key (it is stored in upydev.__path__) by USB/Serial connection.
                       Use -to [serial devname] flag with -tfkey to transfer keys by USB/Serial
"""


# CRYPTO


def rsa_keygen(args, dir='', store=True, show_key=False, id='00'):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=args.key_size,
        backend=default_backend())
    my_p = getpass.getpass(prompt='Password: ', stream=None)
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                                    encryption_algorithm=serialization.BestAvailableEncryption(bytes(my_p, 'utf-8')))
    if show_key:
        print(pem)
    if store:
        key_path_file = os.path.join(dir, 'upy_pub_rsa{}.key'.format(id))
        with open(key_path_file, 'wb') as keyfile:
            keyfile.write(pem)
    return pem


def load_rsa_key(dir='', show_key=False, id='00'):
    buff_key = b''
    rsa_key_abs = os.path.join(dir, 'upy_pub_rsa{}.key'.format(id))
    try:
        with open(rsa_key_abs, 'rb') as keyfile:
            while True:
                try:
                    buff = keyfile.read(2000)
                    if buff != b'':
                        buff_key += buff
                    else:
                        break
                except Exception as e:
                    print(e)
        if show_key:
            print(buff_key)
        return buff_key
    except Exception as e:
        print("No RSA key found for this device, generate one first with '$ upydev gen_rsakey -tfkey' ")


def upy_keygen(rsa_key):
    aZ09 = bytes(string.ascii_letters + string.digits, 'ascii')
    raw_key_list = [line for line in rsa_key.splitlines()[1:-1]]
    raw_key = b''
    for line in raw_key_list:
        raw_key += line
    random_token = secrets.token_bytes(32)  # send this
    for b in random_token:
        raw_key += bytes(chr(raw_key[b]), 'utf-8')
    key_hash = hashlib.sha256()
    key_hash.update(raw_key)
    hashed_key = key_hash.digest()
    index_key = [secrets.randbelow(len(hashed_key)) for i in range(8)]  # send this
    password_long = bytes([hashed_key[val] for val in index_key])
    password_short = bytes([aZ09[val % len(aZ09)] for val in password_long]).decode()

    return (password_short, random_token + bytes(index_key))


def get_cert_data():
    # MAC ADDRESS IF
    try:
        try:
            ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_soc.connect(('8.8.8.8', 1))
            local_ip = ip_soc.getsockname()[0]
            ip_soc.close()
            addrs = local_ip
        except Exception as e:
            addrs = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for
                     iface in netifaces.interfaces() if netifaces.AF_INET in
                     netifaces.ifaddresses(iface)][-1]

        USER = os.environ['USER']
        HOST_NAME = socket.gethostname()
        COUNTRY_CODE = locale.getlocale()[0].split('_')[1]
        return {'addrs': addrs, 'USER': USER, 'HOST_NAME': HOST_NAME,
                'COUNTRY_CODE': COUNTRY_CODE}
    except Exception as e:
        default_temp = {'addrs': 'xxxx', 'USER': 'xxxx', 'HOST_NAME': 'xxxx',
                        'COUNTRY_CODE': 'XX'}
        return default_temp


def ssl_ECDSA_key_certgen(args, dir='', store=True):
    # print('Generating RSA key and Cerficate...')
    print('Getting unique id...')
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss,
                 autodetect=True)
    id_bytes = dev.cmd("from machine import unique_id; unique_id()",
                       silent=True, rtn_resp=True)
    unique_id = hexlify(id_bytes).decode()
    print('ID: {}'.format(unique_id))
    dev_platform = dev.dev_platform
    dev.disconnect()
    # key = rsa.generate_private_key(
    #     public_exponent=65537,
    #     key_size=args.key_size,
    #     backend=default_backend())
    key = ec.generate_private_key(
        ec.SECP256R1(),
        backend=default_backend())

    my_p = getpass.getpass(prompt='Passphrase: ', stream=None)
    pem = key.private_bytes(encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                            encryption_algorithm=serialization.BestAvailableEncryption(bytes(my_p, 'utf-8')))

    if store:
        key_path_file_pem = os.path.join(dir, 'SSL_key{}.pem'.format(unique_id))
        with open(key_path_file_pem, 'wb') as keyfile:
            keyfile.write(pem)
    cert_data = get_cert_data()
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, u"{}".format(cert_data['COUNTRY_CODE'])),
                                  x509.NameAttribute(
                                      NameOID.USER_ID, u"{}".format(cert_data['USER'])),
                                  x509.NameAttribute(
                                      NameOID.SURNAME, u"{}".format(cert_data['HOST_NAME'])),
                                  x509.NameAttribute(
                                      NameOID.STREET_ADDRESS, u"{}".format(cert_data['addrs'])),
                                  x509.NameAttribute(
                                      NameOID.ORGANIZATION_NAME, u"MicroPython"),
                                  x509.NameAttribute(NameOID.COMMON_NAME, u"{}@{}".format(dev_platform, unique_id))])
    host_ip = ipaddress.IPv4Address(cert_data['addrs'])
    if '.local' in args.t:
        args.t = socket.gethostbyname(args.t)
    if not args.zt:
        cert = x509.CertificateBuilder().subject_name(
                    subject).issuer_name(issuer).public_key(key.public_key()
                                                            ).serial_number(x509.random_serial_number()
                                                                            ).not_valid_before(datetime.utcnow()
                                                                                               ).not_valid_after(datetime.utcnow() + timedelta(days=365)
                                                                                                                 ).add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost"),
                                                                                                                                                              x509.IPAddress(
                                                                                                                                                                  host_ip),
                                                                                                                                                              x509.DNSName(
                                                                                                                     u"wss://{}:8833".format(args.t)),
                                                                                                                     x509.DNSName(u"wss://192.168.4.1:8833")]),
                                                      critical=False
                                                      ).sign(key, hashes.SHA256(), default_backend())
    else:
        cert = x509.CertificateBuilder().subject_name(
                    subject).issuer_name(issuer).public_key(key.public_key()
                                                            ).serial_number(x509.random_serial_number()
                                                                            ).not_valid_before(datetime.utcnow()
                                                                                               ).not_valid_after(datetime.utcnow() + timedelta(days=365)
                                                                                                                 ).add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost"),
                                                                                                                                                              x509.IPAddress(
                                                                                                                                                                  host_ip),
                                                                                                                                                              x509.DNSName(
                                                                                                                     u"wss://{}:8833".format(args.t)),
                                                                                                                     x509.DNSName(
                                                                                                                         u"wss://192.168.4.1:8833"),
                                                                                                                     x509.DNSName(u"wss://{}:8833".format(args.zt))]),
                                                      critical=False
                                                      ).sign(key, hashes.SHA256(), default_backend())
    if store:
        cert_path_file_pem = os.path.join(dir,
                                          'SSL_certificate{}.pem'.format(unique_id))
        with open(cert_path_file_pem, 'wb') as certfile:
            certfile.write(cert.public_bytes(serialization.Encoding.PEM))

    # CONVERT TO DER FORMAT
    cert_path_file_der = os.path.join(dir, 'SSL_certificate{}.der'.format(unique_id))
    cert_args = shlex.split(
        'openssl x509 -in {} -out {} -outform DER'.format(cert_path_file_pem,
                                                          cert_path_file_der))
    subprocess.call(cert_args)
    key_path_file_der = os.path.join(dir, 'SSL_key{}.der'.format(unique_id))
    key_args = shlex.split(
        'openssl ec -in {} -out {} -outform DER'.format(key_path_file_pem,
                                                        key_path_file_der))
    subprocess.call(key_args)

    if args.tfkey:
        print('Transfering ECDSA key and Certificates to the device...')
        ssl_k = key_path_file_der
        ssl_c = cert_path_file_der
        return {'ACTION': 'put', 'mode': 'SSL', 'Files': [ssl_k, ssl_c]}


# CRYPTO


def get_rsa_key(args):
    print('Generating RSA key...')
    print('Getting unique id...')
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    id_bytes = dev.cmd("from machine import unique_id; unique_id()",
                       silent=True, rtn_resp=True)
    dev.disconnect()

    unique_id = hexlify(id_bytes).decode()
    print('ID: {}'.format(unique_id))
    pkey = rsa_keygen(args, dir=UPYDEV_PATH, show_key=args.show_key, id=unique_id)
    print('Done!')

    if args.tfkey:  # move out for now
        print('Transfering RSA key to the device...')
        key_abs = os.path.join(UPYDEV_PATH, 'upy_pub_rsa{}.key'.format(unique_id))
        return {'ACTION': 'put', 'mode': 'RSA', 'Files': [key_abs]}
        # print('Done!')


def refresh_wrkey(args, device):
    print('Generating new random WebREPL password for {}...'.format(device))
    if args.localkey_id is None:
        print('Getting unique id...')
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        id_bytes = dev.cmd("from machine import unique_id; unique_id()",
                           silent=True, rtn_resp=True)
        unique_id = hexlify(id_bytes).decode()
        print('ID: {}'.format(unique_id))
        pvkey = load_rsa_key(dir=UPYDEV_PATH, show_key=args.show_key,
                             id=unique_id)
        print('Generating random password from RSA key...')
        new_p, new_token = upy_keygen(pvkey)
        dev.cmd("from upysecrets import load_key, upy_keygen")
        dev.cmd("rk = load_key()")
        dev.cmd("newp = upy_keygen(rk, {})".format(new_token))
        print('New random password generated!')
        dev.reset(reconnect=False)
    else:
        unique_id = args.localkey_id
        print('ID: {}'.format(unique_id))
        pvkey = load_rsa_key(dir=UPYDEV_PATH, show_key=args.show_key,
                             id=unique_id)
        print('Generating random password from RSA key...')
        new_p, new_token = upy_keygen(pvkey)
        print('Use this token to generate new password in the device:\n', new_token)
    upydev_ip = args.t
    upydev_pass = new_p
    upy_conf = {'addr': upydev_ip, 'passwd': upydev_pass, 'name': device}
    file_conf = 'upydev_.config'
    if args.g:
        file_conf = os.path.join(UPYDEV_PATH, 'upydev_.config')
    with open(file_conf, 'w') as config_file:
        config_file.write(json.dumps(upy_conf))
    if args.g:
        print('{} settings saved globally!'.format(device))
    else:
        print('{} settings saved in working directory!'.format(device))
    # check if device is in global group
    dt = check_device_type(args.t)
    upydev_name = device
    group_file = 'UPY_G.config'
    group_file_path = os.path.join(UPYDEV_PATH, group_file)
    if group_file in os.listdir(UPYDEV_PATH):
        with open(group_file_path, 'r', encoding='utf-8') as group:
            devices = json.loads(group.read())

        if upydev_name in devices:
            devices.update({upydev_name: [upydev_ip, upydev_pass]})
            with open(group_file_path, 'w', encoding='utf-8') as group:
                group.write(json.dumps(devices))
            print('{} {} settings saved in global group!'.format(dt, upydev_name))


def get_ssl_keycert(args):
    # print('Generating SSL ECDSA key and certificates...')
    ssl_dict = ssl_ECDSA_key_certgen(args, dir=UPYDEV_PATH)
    if ssl_dict:
        return ssl_dict


def keygen_action(args, **kargs):
    dev_name = kargs.get('device')
    # GEN_RSAKEY

    if args.m == 'gen_rsakey':
        print('Generating RSA key for {}...'.format(dev_name))
        rsa_key = get_rsa_key(args)
        if rsa_key:
            return rsa_key
        else:
            sys.exit()

    # RF_WRKEY
    elif args.m == 'rf_wrkey':
        refresh_wrkey(args, dev_name)
        sys.exit()

    # SSLGEN_KEY

    elif args.m == 'sslgen_key':
        print('Generating SSL ECDSA key, cert for : {}'.format(dev_name))
        ssl_key_cert = get_ssl_keycert(args)
        if ssl_key_cert:
            return ssl_key_cert
        else:
            sys.exit()
