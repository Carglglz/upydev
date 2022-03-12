from upydevice import Device
import sys
from upydev.fileio import BleFileIO, SerialFileIO, WebSocketFileIO
from upydevice import check_device_type
from upydev.devicemanagement import check_zt_group
import getpass
import os
import json
import upydev
from binascii import hexlify
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import string
import secrets
import hashlib
import netifaces
import socket
import locale
from datetime import datetime, timedelta
import ipaddress
import argparse
import shlex
rawfmt = argparse.RawTextHelpFormatter

dict_arg_options = {'kg': ['t', 'zt', 'p', 'wss', 'f', 'rkey', 'tfkey', 'key_size',
                           'show_key', 'g', 'to', 'fre'],
                    'rsa': ['t', 'zt', 'p', 'wss', 'fre', 'f']}


KG = dict(help="to generate a key pair (RSA) or key & certificate (ECDSA) for ssl",
          desc="generate key pair and exchange with device, or refresh WebREPL "
               "password",
          mode=dict(help='indicate a key {rsa, ssl, wr}',
                    metavar='mode',
                    choices=['rsa', 'ssl', 'wr'],
                    nargs='?'),
          subcmd=dict(help='indicate if RSA key pair is for host',
                      metavar='host',
                      nargs='?'),
          options={"-t": dict(help="device target address",
                              required=True),
                   "-p": dict(help='device password or baudrate',
                              required=True),
                   "-wss": dict(help='use WebSocket Secure',
                                required=False,
                                default=False,
                                action='store_true'),
                   "-zt": dict(help='internal flag for zerotierone device',
                               required=False,
                               default=False,
                               action='store_true'),
                   "-rst": dict(help='internal flag for reset',
                                required=False,
                                default=False,
                                action='store_true'),
                   "-key_size": dict(help="RSA key size, default:2048",
                                     default=2048,
                                     required=False,
                                     type=int),
                   "-show_key": dict(help='show generated RSA key',
                                     required=False,
                                     default=False,
                                     action='store_true'),
                   "-tfkey": dict(help='transfer keys to device',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                   "-rkey": dict(help='option to remove private device key from host',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                   "-g": dict(help='option to store new WebREPL password globally',
                              required=False,
                              default=False,
                              action='store_true'),
                   "-to": dict(help='serial device name to upload to',
                               required=False)})

RSA = dict(help="to perform operations with RSA key pair as sign, verify or "
                "authenticate",
           desc="sign files, verify signatures or authenticate devices with "
                "RSA challenge\nusing device keys or host keys",
           mode=dict(help='indicate an action {sign, verify, auth}',
                     metavar='mode',
                     choices=['sign', 'verify', 'auth']),
           subcmd=dict(help='indicate a file to sign/verify',
                       metavar='file/signature',
                       nargs='?'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-host": dict(help='to use host keys',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                    "-rst": dict(help='internal flag for reset',
                                 required=False,
                                 default=False,
                                 action='store_true')})

KG_CMD_DICT_PARSER = {"kg": KG, "rsa": RSA}

usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('keygen/cryptography tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in KG_CMD_DICT_PARSER.items():
    if 'desc' in subcmd.keys():
        _desc = f"{subcmd['help']}\n\n{subcmd['desc']}"
    else:
        _desc = subcmd['help']
    _subparser = subparser_cmd.add_parser(command, help=subcmd['help'],
                                          description=_desc,
                                          formatter_class=rawfmt)
    for pos_arg in subcmd.keys():
        if pos_arg not in ['subcmd', 'help', 'desc', 'options', 'alt_ops']:
            _subparser.add_argument(pos_arg, **subcmd[pos_arg])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)


def parseap(command_args):
    try:
        return parser.parse_known_args(command_args)
    except SystemExit:  # argparse throws these because it assumes you only want
        # to do the command line
        return None  # should be a default one


def sh_cmd(cmd_inp):
    # parse args
    command_line = shlex.split(cmd_inp)

    all_args = parseap(command_line)

    if not all_args:
        return
    else:
        args, unknown_args = all_args

    return args, unknown_args


def filter_bool_opt(k, v):
    if v and isinstance(v, bool):
        return f"{k}"
    else:
        return ""


def expand_margs(v):
    if isinstance(v, list):
        return ' '.join([str(val) for val in v])
    else:
        return v


UPYDEV_PATH = upydev.__path__[0]

CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'
OK = '\033[92mOK\x1b[0m'
FAIL = '\u001b[31;1mF\u001b[0m'

KEYGEN_HELP = """
> KEYGEN: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - gen_rsakey: To generate RSA-2048 bit key pair that will be shared with the device
                      (it is unique for each device) use -tfkey to send this key to the
                      device (use only if connected directly to the AP of the device or a
                      "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                      upload the key (it is stored in upydev.__path__) by USB/Serial connection.
                      *Use -rkey option to remove private key from host (only store public key).
                      To generate a host key pair use 'kg rsa host'. Then the public key will be sent
                      to the device so it can verify or authenticate the host signature.


        - rsa_sign: To sign a file with device RSA key, (rsa lib required), use -f to indicate
                   the file to sign or use alias form: $ upydev rsa sign [FILE]
                   * To sign a file with host RSA key: $ upydev rsa sign host [FILE]

        - rsa_verify: To verify a signature of a file made with device RSA key, use -f to indicate
                   the signature file to verify or use alias form: $ upydev rsa verify [FILE]
                   * To verify in device a signature made with host RSA key: $ upydev rsa verify host [FILE]

        - rsa_auth: To authenticate a device with RSA encrypted challenge (Public Keys exchange must be done first)

        - rf_wrkey: To "refresh" the WebREPL password with a new random password derivated from
                    the RSA key previously generated. A token then is sent to the device to generate
                    the same password from the RSA key previously uploaded. This won't leave
                    any clues in the TCP Websocekts packages of the current WebREPL password.
                    (Only the token will be visible; check this using wireshark)
                    (This needs upysecrets.py)

        - sslgen_key:  To generate ECDSA key and a self-signed certificate to enable SSL sockets
                       This needs a passphrase, that will be required every time the key is loaded.
                       Use -tfkey to upload this key to the device
                       (use only if connected directly to the AP of the device or a
                       "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                       upload the key (it is stored in upydev.__path__) by USB/Serial connection.
                       Use -to [serial devname] flag with -tfkey to transfer keys by USB/Serial
"""


# CRYPTO


def rsa_keygen(args, dir='', store=True, show_key=False, id='00', host=False):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=args.key_size,
        backend=default_backend())
    # my_p = getpass.getpass(prompt='Password: ', stream=None)
    # pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
    #                                 encryption_algorithm=serialization.BestAvailableEncryption(bytes(my_p, 'utf-8')))
    key_ser = serialization.NoEncryption()
    if host:
        my_p = getpass.getpass(prompt='Password: ', stream=None)
        # print(my_p)
        key_ser = serialization.BestAvailableEncryption(bytes(my_p, 'utf-8'))
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                                    encryption_algorithm=key_ser)
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PublicFormat.PKCS1)
    if show_key:
        print(pem)
    if store:
        pv_key = f'upy_pv_rsa{id}.key'
        pb_key = f'upy_pub_rsa{id}.key'
        if host:
            pv_key = f'upy_host_pv_rsa{id}.key'
            pb_key = f'upy_host_pub_rsa{id}.key'
        # private key
        keypv_path_file = os.path.join(dir, pv_key)
        with open(keypv_path_file, 'wb') as keyfile:
            keyfile.write(pem)
        # public key
        keypb_path_file = os.path.join(dir, pb_key)
        with open(keypb_path_file, 'wb') as keyfile:
            keyfile.write(pub_pem)
    return pem  # , my_p


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


def load_rsa_pvkey(dir='', show_key=False, id='00'):
    buff_key = b''
    rsa_key_abs = os.path.join(dir, 'upy_pv_rsa{}.key'.format(id))
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

    der = key.private_bytes(encoding=serialization.Encoding.DER,
                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                            encryption_algorithm=serialization.NoEncryption())

    if store:
        key_path_file_pem = os.path.join(dir, f'SSL_key{unique_id}.pem')
        with open(key_path_file_pem, 'wb') as keyfile:
            keyfile.write(pem)

        key_path_file_der = os.path.join(dir, f'SSL_key{unique_id}.der')
        with open(key_path_file_der, 'wb') as keyfile:
            keyfile.write(der)
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
    # if '.local' in args.t:
    #     args.t = socket.gethostbyname(args.t)
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
        dev_ip = args.zt["dev"]
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
                                                                                                                     x509.DNSName(
                                                                                                                         u"wss://{}:8833".format(dev_ip))]),
                                                      critical=False
                                                      ).sign(key, hashes.SHA256(), default_backend())
    if store:
        cert_path_file_pem = os.path.join(dir, f'SSL_certificate{unique_id}.pem')
        with open(cert_path_file_pem, 'wb') as certfile:
            certfile.write(cert.public_bytes(serialization.Encoding.PEM))

        cert_path_file_der = os.path.join(dir, f'SSL_certificate{unique_id}.der')
        with open(cert_path_file_der, 'wb') as certfile:
            certfile.write(cert.public_bytes(serialization.Encoding.DER))

    if args.tfkey:
        print('Transfering ECDSA key and certificate to the device...')
        ssl_k = key_path_file_der
        ssl_c = cert_path_file_der
        return {'ACTION': 'put', 'mode': 'SSL', 'Files': [ssl_k, ssl_c]}


# with open(sys.argv[1], 'rb') as input:
#     key = PrivateKey.load_pkcs1(input.read())
#     d = {}
#     d['n'] = key.n
#     d['e'] = key.e
#     d['d'] = key.d
#     d['p'] = key.p
#     d['q'] = key.q
#     with open(sys.argv[2], 'w') as output:
#         output.write(json.dumps(d))

# CRYPTO


def get_rsa_key(args):
    # print('Generating RSA key...')
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
        print('Loading RSA key...')
        key_abs = os.path.join(UPYDEV_PATH, 'upy_pv_rsa{}.key'.format(unique_id))
        key_abs_pub = os.path.join(UPYDEV_PATH, 'upy_pub_rsa{}.key'.format(unique_id))
        print('Transfering RSA key to the device...')
        return {'ACTION': 'put', 'mode': 'RSA', 'Files': [key_abs, key_abs_pub]}


def get_rsa_key_host(args):
    # print('Generating RSA key...')
    # print('Getting Host unique id...')
    # bb = 6
    # while True:
    #     try:
    #         unique_id = hexlify(uuid.getnode().to_bytes(bb, 'big')).decode()
    #         break
    #     except OverflowError:
    #         bb += 1
    unique_id = hexlify(os.environ['USER'].encode()).decode()[:12]

    # print('Host ID: {}'.format(unique_id))
    pkey = rsa_keygen(args, dir=UPYDEV_PATH, show_key=args.show_key, id=unique_id,
                      host=True)
    print('Done!')

    if args.tfkey:  # move out for now
        print('Loading Host Public RSA key...')
        key_abs_pub = os.path.join(UPYDEV_PATH, f'upy_host_pub_rsa{unique_id}.key')
        print('Transfering Host Public RSA key to the device...')
        return {'ACTION': 'put', 'mode': 'RSA', 'Files': [key_abs_pub]}


def refresh_wrkey(args, device):
    print('Generating new random WebREPL password for {}...'.format(device))
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
    # Encrypt password and decrypt on device
    is_rsa = dev.cmd("import os; 'rsa' in os.listdir('/lib')", silent=True,
                     rtn_resp=True)
    if is_rsa:
        dev_pubkey = serialization.load_pem_public_key(pvkey)
        dev_pvkey = f'upy_pv_rsa{unique_id}.key'
        dev.cmd(
            f"from rsa.rsautil import RSAPrivateKey; pv = RSAPrivateKey('{dev_pvkey}')")
        enc_new_p = dev_pubkey.encrypt(new_p.encode(), padding.PKCS1v15())
        dev.cmd("new_pass = b''")
        # Send password
        for i in range(0, len(enc_new_p), 32):
            dev.cmd(f"new_pass += {enc_new_p[i:i+32]}")
        # Save password
        dev.cmd("pv._decrypt_passwd(new_pass)")
    else:
        dev.cmd("from upysecrets import load_key, upy_keygen")
        dev.cmd("rk = load_key()")
        dev.cmd("newp = upy_keygen(rk, {})".format(new_token))

    print('New random password generated!')
    dev.reset(reconnect=False)
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


def rsa_sign(args, file, **kargs):
    device = kargs.get('device')
    args.m = 'put'
    args.rst = False
    _sigfile = file.split('/')[-1]
    # fileio_action(args, **kargs)
    dt = check_device_type(args.t)
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    if dt == 'WebSocketDevice':
        devIO = WebSocketFileIO(dev, args, devname=device)
    elif dt == 'SerialDevice':
        devIO = SerialFileIO(dev, devname=device)
    elif dt == 'BleDevice':
        devIO = BleFileIO(dev, devname=device)
    devIO.put(file, _sigfile, ppath=True)
    print(f'Signing file {_sigfile} with {device} RSA key')
    id_bytes = dev.wr_cmd("from machine import unique_id; unique_id()",
                          silent=True, rtn_resp=True)
    unique_id = hexlify(id_bytes).decode()
    pvkey = f"upy_pv_rsa{unique_id}.key"
    print(f'{device} ID: {unique_id}')
    dev.wr_cmd(f"from rsa.rsautil import RSAPrivateKey;pk=RSAPrivateKey('{pvkey}')")
    # dev.disconnect()
    print(f"Key ID: {dev.wr_cmd('pk', silent=True, rtn_resp=True)}")
    dev.wr_cmd(f"sg = pk.signfile('{_sigfile}')", silent=False, follow=True)
    sg = dev.wr_cmd("sg", silent=True, rtn_resp=True)
    with open(f"{file.split('/')[-1]}.sign", 'wb') as signfile:
        signfile.write(sg)
    dev.wr_cmd(f"import os;os.remove('{_sigfile}')")
    dev.wr_cmd('import gc;del(sg);gc.collect()')
    dev.disconnect()
    print('Signature done!')


def rsa_verify(args, file, device):
    print(f'Verifying {file} signature from {device} RSA key')
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    id_bytes = dev.cmd("from machine import unique_id; unique_id()",
                       silent=True, rtn_resp=True)
    dev.disconnect()
    unique_id = hexlify(id_bytes).decode()
    print(f"Assuming signed data in {file.replace('.sign', '')}")
    print(f'{device} ID: {unique_id}')
    key_abs = os.path.join(UPYDEV_PATH, f'upy_pub_rsa{unique_id}.key')
    # load key.pem
    with open(key_abs, "rb") as key_file:
        pub_key = serialization.load_pem_public_key(key_file.read())
        kz = pub_key.key_size
        key_hash = hashlib.sha256()
        key_hash.update(pub_key.public_bytes(serialization.Encoding.DER,
                                             serialization.PublicFormat.PKCS1))
        hashed_key = hexlify(key_hash.digest()).decode('ascii').upper()
        print(f"Using {kz} bits RSA Public key {hashed_key[:40]}")
    # load message
    with open(file.replace('.sign', ''), 'rb') as message:
        message_bytes = message.read()

    with open(file, 'rb') as signature:
        signature_bytes = signature.read()

    try:
        pub_key.verify(signature_bytes, message_bytes, padding.PKCS1v15(),
                       hashes.SHA256())

        print('Verification: OK')
    except InvalidSignature:
        print('Verification failed: Invalid Signature')


def rsa_sign_host(args, file, **kargs):
    _sigfile = file.split('/')[-1]
    # fileio_action(args, **kargs)
    # bb = 6
    # while True:
    #     try:
    #         unique_id = hexlify(uuid.getnode().to_bytes(bb, 'big')).decode()
    #         break
    #     except OverflowError:
    #         bb += 1
    unique_id = hexlify(os.environ['USER'].encode()).decode()[:12]
    print('Host ID: {}'.format(unique_id))
    print(f'Signing file {_sigfile} with Host RSA key')
    pvkey = f"upy_host_pv_rsa{unique_id}.key"
    key_abs = os.path.join(UPYDEV_PATH, pvkey)
    with open(key_abs, "rb") as key_file:
        while True:
            try:
                my_p = getpass.getpass(
                    prompt=f"Enter passphrase for key '{pvkey}':", stream=None)
                # print(my_p)
                private_key = serialization.load_pem_private_key(
                    key_file.read(), my_p.encode())
                break
            except ValueError:
                # print(e)
                key_file.seek(0)
                print('Passphrase incorrect, try again...')
    with open(file, 'rb') as file_to_sign:
        key_hash = hashlib.sha256()
        kz = private_key.key_size
        key_hash.update(private_key.private_bytes(serialization.Encoding.DER,
                                                  serialization.PrivateFormat.TraditionalOpenSSL,
                                                  serialization.NoEncryption()))
        hashed_key = hexlify(key_hash.digest()).decode('ascii').upper()
        print(f"Using {kz} bits RSA Private key {hashed_key[:40]}")
        signature = private_key.sign(file_to_sign.read(), padding.PKCS1v15(),
                                     hashes.SHA256())
    with open(f"{file}.sign", 'wb') as signedfile:
        signedfile.write(signature)
    print('Signature done!')


def rsa_verify_host(args, file, device):
    print(f'{device} verifying {file} signature from Host RSA key')
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print(f"Assuming signed data in {file.replace('.sign', '')}")
    # bb = 6
    # while True:
    #     try:
    #         unique_id = hexlify(uuid.getnode().to_bytes(bb, 'big')).decode()
    #         break
    #     except OverflowError:
    #         bb += 1
    unique_id = hexlify(os.environ['USER'].encode()).decode()[:12]
    print(f'Host ID: {unique_id}')
    key_abs = os.path.join(UPYDEV_PATH, f'upy_host_pub_rsa{unique_id}.key')
    # load key.pem
    with open(key_abs, "rb") as key_file:
        pub_key = serialization.load_pem_public_key(key_file.read())
        kz = pub_key.key_size
        key_hash = hashlib.sha256()
        key_hash.update(pub_key.public_bytes(serialization.Encoding.DER,
                                             serialization.PublicFormat.PKCS1))
        hashed_key = hexlify(key_hash.digest()).decode('ascii').upper()
        print(f"Host: {kz} bits RSA Public key {hashed_key[:40]}")
    pubkey = f"upy_host_pub_rsa{unique_id}.key"
    dev.wr_cmd(f"from rsa.rsautil import RSAPublicKey;pbk=RSAPublicKey('{pubkey}')")
    ftv = file.replace('.sign', '')
    print(f"{device}: Verifying with {dev.wr_cmd('pbk', silent=True, rtn_resp=True)} ")
    dev.wr_cmd(f"vf = pbk.verifyfile('{ftv}', '{file}')", silent=False, follow=True)
    vf = dev.wr_cmd("vf", silent=True, rtn_resp=True)
    if vf is True:
        print('Verification: OK')
    else:
        print('Verification failed: Invalid Signature')
    dev.wr_cmd('import gc;del(vf);gc.collect()')
    dev.disconnect()

# AUTHENTICATE CHALLENGE


def rsa_auth(args, device):
    # load device public key
    print(f'Authenticating {device} with RSA Challenge...')
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    id_bytes = dev.cmd("from machine import unique_id; unique_id()",
                       silent=True, rtn_resp=True)
    # dev.disconnect()
    unique_id_dev = hexlify(id_bytes).decode()
    print(f'{device} ID: {unique_id_dev}')
    key_abs = os.path.join(UPYDEV_PATH, f'upy_pub_rsa{unique_id_dev}.key')
    # load key.pem
    with open(key_abs, "rb") as key_file:
        pub_key = serialization.load_pem_public_key(key_file.read())
        kz = pub_key.key_size
        key_hash = hashlib.sha256()
        key_hash.update(pub_key.public_bytes(serialization.Encoding.DER,
                                             serialization.PublicFormat.PKCS1))
        hashed_key = hexlify(key_hash.digest()).decode('ascii').upper()
        print(f"Using {kz} bits RSA Public key {hashed_key[:40]}")
    # generate random token
    token = secrets.token_urlsafe(32).encode()
    # encrypt token with public key
    try:
        token_challenge = pub_key.encrypt(token, padding.PKCS1v15())

    except ValueError as e:
        print(f'Encryption failed: {e}')
    # send encrypted token
    print('Sending challenge...')
    if len(token_challenge) > 50:
        dev.wr_cmd("token_challenge = b''", silent=True)
        for i in range(0, len(token_challenge), 50):
            dev.wr_cmd(f'token_challenge += {token_challenge[i:i+50]}', silent=True)
    pvkey = f"upy_pv_rsa{unique_id_dev}.key"
    dev.wr_cmd(f"from rsa.rsautil import RSAPrivateKey, "
               f"RSAPublicKey;pk=RSAPrivateKey('{pvkey}')")
    # print(f"Key ID: {dev.wr_cmd('pk', silent=True, rtn_resp=True)}")
    print('Decrypting challenge...')
    dev.wr_cmd("token = pk.decrypt(token_challenge)", silent=False, follow=True)
    # bb = 6
    # while True:
    #     try:
    #         unique_id = hexlify(uuid.getnode().to_bytes(bb, 'big')).decode()
    #         break
    #     except OverflowError:
    #         bb += 1
    print('Encrypting challenge with host public key...')
    unique_id = hexlify(os.environ['USER'].encode()).decode()[:12]
    print(f'Host ID: {unique_id}')
    # device decrypt and encrypt with host public key
    host_pb_key = f'upy_host_pub_rsa{unique_id}.key'
    dev.wr_cmd(f"pubk=RSAPublicKey('{host_pb_key}')", silent=True)
    print(f"Host Key ID: {dev.wr_cmd('pubk', silent=True, rtn_resp=True)}")
    dev.wr_cmd("token_resp = pubk.encrypt(token)", silent=False, follow=True)
    # send encrypted token
    token_resp = dev.wr_cmd("token_resp", silent=True, rtn_resp=True)
    host_pv_key = f"upy_host_pv_rsa{unique_id}.key"
    key_abs = os.path.join(UPYDEV_PATH, host_pv_key)
    with open(key_abs, "rb") as key_file_host:
        key_data = key_file_host.read()
        while True:
            try:
                my_p = getpass.getpass(
                    prompt=f"Enter passphrase for key '{host_pv_key}':", stream=None)
                # print(my_p)
                private_key = serialization.load_pem_private_key(key_data,
                                                                 my_p.encode())
                break
            except ValueError:
                # print(e)
                print('Passphrase incorrect, try again...')

    # decrypt and verify is original token
    dev_type = check_device_type(args.t)

    # decrypt and verify is original token
    try:
        token_dev = private_key.decrypt(token_resp, padding.PKCS1v15())
        assert token == token_dev
        print(f'Device {device} authenticated')
        print(f'{device:10} -> {dev_type} @ {args.t} -> [AUTH {OK}] {CHECK}')
    except (AssertionError, ValueError):
        print("ERROR, AUTHENTICATION FAILED")
        print(f'{device:10} -> {dev_type} @ {args.t} -> [AUTH {XF}] {FAIL}]')

    dev.wr_cmd('import gc;del(token_resp);del(token_challenge);gc.collect()')
    dev.disconnect()

    # interface --> same as probe


def keygen_action(args, unkwargs, **kargs):
    dev_name = kargs.get('device')
    args_dict = {f"-{k}": v for k, v in vars(args).items()
                 if k in dict_arg_options[args.m]}
    args_list = [f"{k} {expand_margs(v)}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    cmd_inp = f"{args.m} {' '.join(unkwargs)} {' '.join(args_list)}"
    # print(cmd_inp)
    # sys.exit()
    # debug command:
    if cmd_inp.startswith('!'):
        args = parseap(shlex.split(cmd_inp[1:]))
        print(args)
        return
    if '-h' in unkwargs:
        sh_cmd(f"{args.m} -h")
        sys.exit()

    result = sh_cmd(cmd_inp)
    if not result:
        sys.exit()
    else:
        args, unknown_args = result
    if hasattr(args, 'subcmd'):
        command, rest_args = args.m, args.subcmd
        if rest_args is None:
            rest_args = []
    else:
        command, rest_args = args.m, []
    # print(f"{command}: {args} {rest_args} {unknown_args}")
    # sys.exit()
    # GEN_RSAKEY

    if command == 'kg':
        # TODO: gen rsa key in device
        if args.mode == 'rsa':
            if not rest_args:
                print('Generating RSA key for {}...'.format(dev_name))
                rsa_key = get_rsa_key(args)
                if rsa_key:
                    return rsa_key
                else:
                    sys.exit()
            else:
                # Check if exists:
                print('Getting Host unique id...')
                # bb = 6
                # while True:
                #     try:
                #         unique_id = hexlify(uuid.getnode().to_bytes(bb, 'big')).decode()
                #         break
                #     except OverflowError:
                #         bb += 1
                unique_id = hexlify(os.environ['USER'].encode()).decode()[:12]

                print('Host ID: {}'.format(unique_id))
                pbkey = f"upy_host_pub_rsa{unique_id}.key"
                if pbkey in os.listdir(UPYDEV_PATH):
                    nk = input('Host RSA key detected, generate new one? [y/n]: ')
                    if nk == 'y':
                        print('Generating Host RSA key...')
                        rsa_key = get_rsa_key_host(args)
                        if rsa_key:
                            return rsa_key
                        else:
                            sys.exit()
                    else:
                        tfk = input(
                            'Transfer existent Host Public RSA key to device? [y/n]: ')
                        if tfk == 'y':
                            key_abs_pub = os.path.join(UPYDEV_PATH, pbkey)
                            print('Transfering Host Public RSA key to the device...')
                            return {'ACTION': 'put', 'mode': 'RSA', 'Files': [key_abs_pub]}
                        else:
                            sys.exit()

                else:
                    print('Generating Host RSA key...')
                    rsa_key = get_rsa_key_host(args)
                    if rsa_key:
                        return rsa_key
                    else:
                        sys.exit()
        # SSLGEN_KEY
        elif args.mode == 'ssl':
            print('Generating SSL ECDSA key, cert for : {}'.format(dev_name))
            # check if device in ZeroTier group.
            args.zt = check_zt_group(dev_name, args)
            ssl_key_cert = get_ssl_keycert(args)
            if ssl_key_cert:
                return ssl_key_cert
            else:
                sys.exit()
        # RF_WRKEY
        elif args.mode == 'wr':
            refresh_wrkey(args, dev_name)
            sys.exit()

    # RSA Sign & Verify
    elif command == 'rsa':
        if args.mode == 'sign':
            if not rest_args:
                print("rsa: sign error: the following arguments are required: file")
                sys.exit()
            if not args.host:
                rsa_sign(args, rest_args, **kargs)
            else:
                rsa_sign_host(args, rest_args, **kargs)
            sys.exit()

        elif args.mode == 'verify':
            if not rest_args:
                print("rsa: verify error: the following arguments are required: file")
                sys.exit()
            if not args.host:
                rsa_verify(args, rest_args, dev_name)
            else:
                rsa_verify_host(args, rest_args, dev_name)
            sys.exit()

        elif args.mode == 'auth':
            rsa_auth(args, dev_name)
            sys.exit()

    # TODO: RSA key exchange
    #    -->: Host keypair (unique)
    #    -->: Device keypair (unique)
    #  HOST send Public Key
    #  DEVICE send Public Key
    # Authenticated message sending --> Encrypt and sign
    # Authenticated message receiving --> Verify and decrypt
    # Authenticated message receiving --> Verify and decrypt
