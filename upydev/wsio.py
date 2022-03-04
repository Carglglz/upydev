#!/usr/bin/env python3
import sys
import os
import struct
import time
import ssl
from datetime import timedelta
import socket
from upydev import websocket_helper
from upydev import wss_helper_host
from upydevice import Device, DeviceNotFound, DeviceException
from upydevice.wsclient import load_custom_CA_data
from upydev.helpinfo import see_help
from upydev import __path__ as _CA_PATH
import glob

CA_PATH = _CA_PATH[0]

# Define to 1 to use builtin "uwebsocket" module of MicroPython
USE_BUILTIN_UWEBSOCKET = 0
# Treat this remote directory as a root for file transfers
SANDBOX = ""
# SANDBOX = "/tmp/webrepl/"
DEBUG = 0

WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2
WEBREPL_GET_VER = 3

bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]

columns, rows = os.get_terminal_size(0)
cnt_size = 65
if columns > cnt_size:
    bar_size = int((columns - cnt_size))
    pb = True
else:
    bar_size = 1
    pb = False


def do_pg_bar(index, wheel, nb_of_total, speed, time_e, loop_l,
              percentage, ett, size_bar=bar_size):
    l_bloc = bloc_progress[loop_l]
    if index == size_bar:
        l_bloc = "█"
    sys.stdout.write("\033[K")
    print('▏{}▏{:>2}{:>5} % | {} | {:>5} kB/s | {}/{} s'.format("█" * index + l_bloc + " "*((size_bar+1) - len("█" * index + l_bloc)),
                                                                wheel[index % 4],
                                                                int((percentage)*100),
                                                                nb_of_total, speed,
                                                                str(timedelta(seconds=time_e)).split(
                                                                    '.')[0][2:],
                                                                str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
    sys.stdout.flush()


def debugmsg(msg):
    if DEBUG:
        print(msg)


class websocket:

    def __init__(self, s):
        self.s = s
        self.buf = b""

    def write(self, data):
        l = len(data)
        if l < 126:
            # TODO: hardcoded "binary" type
            hdr = struct.pack(">BB", 0x82, l)
        else:
            hdr = struct.pack(">BBH", 0x82, 126, l)
        self.s.send(hdr)
        self.s.send(data)

    def recvexactly(self, sz):
        res = b""
        while sz:
            data = self.s.recv(sz)
            if not data:
                break
            res += data
            sz -= len(data)
        return res

    def read(self, size, text_ok=False):
        if not self.buf:
            while True:
                hdr = self.recvexactly(2)
                assert len(hdr) == 2
                fl, sz = struct.unpack(">BB", hdr)
                if sz == 126:
                    hdr = self.recvexactly(2)
                    assert len(hdr) == 2
                    (sz,) = struct.unpack(">H", hdr)
                if fl == 0x82:
                    break
                if text_ok and fl == 0x81:
                    break
                debugmsg(
                    "Got unexpected websocket record of type %x, skipping it" % fl)
                while sz:
                    skip = self.s.recv(sz)
                    debugmsg("Skip data: %s" % skip)
                    sz -= len(skip)
            data = self.recvexactly(sz)
            assert len(data) == sz
            self.buf = data

        d = self.buf[:size]
        self.buf = self.buf[size:]
        assert len(d) == size, len(d)
        return d

    def ioctl(self, req, val):
        assert req == 9 and val == 2


def login(ws, passwd):
    while True:
        c = ws.read(1, text_ok=True)
        if c == b":":
            assert ws.read(1, text_ok=True) == b" "
            break
    ws.write(passwd.encode("utf-8") + b"\r")


def read_resp(ws):
    data = ws.read(4)
    sig, code = struct.unpack("<2sH", data)
    assert sig == b"WB"
    return code


def send_req(ws, op, sz=0, fname=b""):
    rec = struct.pack(WEBREPL_REQ_S, b"WA", op, 0, 0, sz, len(fname), fname)
    debugmsg("%r %d" % (rec, len(rec)))
    ws.write(rec)


def get_ver(ws):
    send_req(ws, WEBREPL_GET_VER)
    d = ws.read(3)
    d = struct.unpack("<BBB", d)
    return d


def put_file(ws, local_file, remote_file):
    columns, rows = os.get_terminal_size(0)
    cnt_size = 65
    if columns > cnt_size:
        size_bar = int((columns - cnt_size))
        pb = True
    else:
        size_bar = 1
        pb = False
    wheel = ['|', '/', '-', "\\"]
    sz = os.stat(local_file)[6]
    dest_fname = (SANDBOX + remote_file).encode("utf-8")
    rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_PUT_FILE,
                      0, 0, sz, len(dest_fname), dest_fname)
    debugmsg("%r %d" % (rec, len(rec)))
    ws.write(rec[:10])
    ws.write(rec[10:])
    assert read_resp(ws) == 0
    cnt = 0
    t_start = time.time()
    # print('\n')
    with open(local_file, "rb") as f:
        while True:
            buf = f.read(1024)
            if not buf:
                break
            ws.write(buf)
            cnt += len(buf)
            loop_index_f = (cnt/sz)*size_bar
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = f"{cnt/(1000):.2f}/{sz/(1000):.2f} kB"
            percentage = cnt/sz
            t_elapsed = time.time() - t_start
            t_speed = f"{(cnt/(1000))/t_elapsed:^2.2f}"
            ett = sz / (cnt / t_elapsed)
            if pb:
                do_pg_bar(loop_index, wheel, nb_of_total, t_speed, t_elapsed,
                          loop_index_l, percentage, ett, size_bar)
            else:
                sys.stdout.write("Sent %d of %d bytes\r" % (cnt, sz))
                sys.stdout.flush()
        if sz == 0:
            sz = 1
            cnt += len(buf)
            loop_index_f = (cnt/sz)*size_bar
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = f"{0:.2f}/{0:.2f} kB"
            percentage = cnt/sz
            t_elapsed = time.time() - t_start
            t_speed = f"{0:^2.2f}"
            ett = 0
            if pb:
                do_pg_bar(loop_index, wheel, nb_of_total, t_speed, t_elapsed,
                          loop_index_l, percentage, ett, size_bar)

    print('\n')
    print()
    assert read_resp(ws) == 0


def get_file(ws, local_file, remote_file, file_size):
    columns, rows = os.get_terminal_size(0)
    cnt_size = 65
    if columns > cnt_size:
        size_bar = int((columns - cnt_size))
        pb = True
    else:
        size_bar = 1
        pb = False
    sz_r = file_size
    wheel = ['|', '/', '-', "\\"]
    src_fname = (SANDBOX + remote_file).encode("utf-8")
    rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_GET_FILE,
                      0, 0, 0, len(src_fname), src_fname)
    debugmsg("%r %d" % (rec, len(rec)))
    ws.write(rec)
    assert read_resp(ws) == 0
    t_start = time.time()
    # print('\n')
    with open(local_file, "wb") as f:
        cnt = 0
        while True:
            ws.write(b"\0")
            (sz,) = struct.unpack("<H", ws.read(2))
            if sz == 0:
                break
            while sz:
                buf = ws.read(sz)
                if not buf:
                    raise OSError()
                cnt += len(buf)
                f.write(buf)
                sz -= len(buf)
                if pb:
                    if file_size > 0:
                        loop_index_f = (cnt/sz_r)*size_bar
                        loop_index = int(loop_index_f)
                        loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                        nb_of_total = f"{cnt/(1000):.2f}/{sz_r/(1000):.2f} kB"
                        percentage = cnt / sz_r
                        t_elapsed = time.time() - t_start
                        t_speed = f"{(cnt/(1000))/t_elapsed:^2.2f}"
                        ett = sz_r / (cnt / t_elapsed)
                        do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
                                  t_elapsed, loop_index_l, percentage, ett, size_bar)
                else:
                    sys.stdout.write("Received %d bytes\r" % cnt)
                    sys.stdout.flush()
        if file_size == 0:
            sz = 1
            cnt = 1
            loop_index_f = (cnt/sz)*size_bar
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = f"{0:.2f}/{0:.2f} kB"
            percentage = cnt/sz
            t_elapsed = time.time() - t_start
            t_speed = f"{0:^2.2f}"
            ett = 0
            if pb:
                do_pg_bar(loop_index, wheel, nb_of_total, t_speed, t_elapsed,
                          loop_index_l, percentage, ett, size_bar)

    print()
    print('\n')
    assert read_resp(ws) == 0


def error(msg):
    print(msg)
    sys.exit(1)


def parse_remote(remote, ssl=False):
    host, fname = remote.rsplit(":", 1)
    if fname == "":
        fname = "/"
    port = 8266
    if ssl:
        port = 8833
    if ":" in host:
        host, port = host.split(":")
        port = int(port)
    return (host, port, fname)


def connect_ws(host, port, passwd, websec):
    s = socket.socket()
    s.settimeout(10)
    _hostname = host
    if host.endswith('.local'):
        host = socket.gethostbyname(host)
    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]
    try:
        if websec:
            hostname = f"wss://{_hostname}:{port}"
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cadata=load_custom_CA_data(CA_PATH))
            # load cert from hostname
            # key, cert = load_cert_from_hostname(capath, hostname)
            # if cert:
            # context.load_cert_chain(cert, key)
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            s = context.wrap_socket(s, server_hostname=hostname)
            s.connect(addr)
            wss_helper_host.client_handshake(s, ssl=True)
        else:
            s.connect(addr)
            websocket_helper.client_handshake(s)
    except socket.timeout:
        try:
            if websec:
                raise DeviceNotFound(
                    f"WebSocketDevice @ wss://{host}:{port} is not reachable")
            else:
                raise DeviceNotFound(
                    f"WebSocketDevice @ ws://{host}:{port} is not reachable")
        except Exception as e:
            print(f'ERROR {e}')
            return False

    ws = websocket(s)

    login(ws, passwd)

    # Set websocket to send data marked as "binary"
    ws.ioctl(9, 2)

    return ws


def wsfileio(args, file, upyfile, devname, dev=None):
    op = args.m
    passwd = args.p
    websec = args.wss
    # multiple_files = args.fre
    source = args.s
    if ":" in args.t:
        host, port = args.t.split(":")
        port = int(port)
    else:
        host = args.t
        port = 8266

    if op == 'get':
        source = ''
        assert isinstance(upyfile, tuple) is True, "file must be tuple (size, name)"
        if not websec:
            host, port, src_file = host, port, source + upyfile[1]
        else:
            if port == 8266:
                port = 8833
            host, port, src_file = host, port, source + upyfile[1]
        dst_file = '.'
        if os.path.isdir(dst_file):
            basename = src_file.rsplit("/", 1)[-1]
            dst_file += "/" + basename
    elif op == 'put':
        if not websec:
            host, port, dst_file = host, port, source + upyfile
        else:
            if port == 8266:
                port = 8833
            host, port, dst_file = host, port, source + upyfile
        src_file = file
        if dst_file[-1] == "/":
            basename = src_file.rsplit("/", 1)[-1]
            dst_file += basename

    if not args.fre:
        if op == 'put':
            abs_dst_file = dst_file
            if not dst_file.startswith('/'):
                abs_dst_file = f'/{dst_file}'
            print(f"{src_file} -> {devname}:{abs_dst_file}")
        if op == 'get':
            abs_src_file = src_file
            if not src_file.startswith('/'):
                abs_src_file = f'/{src_file}'
            print(f"{devname}:{abs_src_file} -> {dst_file}")
            size_file_to_get = upyfile[0]

    if dev:
        if dev.connected:
            # if dev.connected:
            dev.ws.sock.settimeout(10)
            ws = websocket(dev.ws.sock)
    else:
        ws = connect_ws(host, port, passwd, websec)

    if ws:

        if op == "get":
            if not args.fre:
                print(f'\n{src_file} [{size_file_to_get/1000:.2f} kB]')
                try:
                    get_file(ws, dst_file, src_file, size_file_to_get)
                except socket.timeout:
                    # print(e, 'Device {} unreachable'.format(devname))
                    try:
                        if args.wss:
                            raise DeviceNotFound(
                                f"WebSocketDevice @ wss://{host}:{port} is not reachable")
                        else:
                            raise DeviceNotFound(
                                f"WebSocketDevice @ ws://{host}:{port} is not reachable")
                    except Exception as e:
                        print(f'ERROR {e}')
                        return False
                except (KeyboardInterrupt, Exception):
                    print('KeyboardInterrupt: get Operation Canceled')
                    # flush ws
                    dev.flush()
                    dev.disconnect()
                    if not dev.connected:
                        ws.s.close()
                    return False
            else:
                for size_file_to_get, file in args.fre:
                    src_file = file
                    dst_file = '.'
                    if os.path.isdir(dst_file):
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += "/" + basename
                    abs_src_file = src_file
                    if not src_file.startswith('/'):
                        abs_src_file = f'/{src_file}'
                    print(f"{devname}:{abs_src_file} -> {dst_file}")
                    print(f'\n{src_file} [{size_file_to_get/1000:.2f} kB]')
                    try:
                        get_file(ws, dst_file, src_file, size_file_to_get)
                    except (KeyboardInterrupt, Exception):
                        print('KeyboardInterrupt: get Operation Canceled')
                        # flush ws and reset
                        dev.flush()
                        dev.disconnect()
                        if input('Continue get Operation with next file? [y/n]') == 'y':
                            dev.connect(ssl=websec, auth=websec)
                        else:
                            print('Canceling file queue..')
                            dev.connect(ssl=websec, auth=websec)
                            raise KeyboardInterrupt
                        dev.ws.sock.settimeout(10)
                        ws = websocket(dev.ws.sock)
                        if not dev.connected:
                            ws.s.close()
                        time.sleep(0.2)
                        if not dev.connected:
                            ws = connect_ws(host, port, passwd, websec)
                    except socket.timeout:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:
                            if args.wss:
                                raise DeviceNotFound(
                                    f"WebSocketDevice @ wss://{host}:{port} is not reachable")
                            else:
                                raise DeviceNotFound(
                                    f"WebSocketDevice @ ws://{host}:{port} is not reachable")
                        except Exception as e:
                            print(f'ERROR {e}')
                            return False
        elif op == "put":
            if not args.fre:
                print(f'\n{src_file} [{os.stat(src_file)[6]/1000:.2f} kB]')
                try:
                    put_file(ws, src_file, dst_file)
                except socket.timeout:
                    # print(e, 'Device {} unreachable'.format(devname))
                    try:
                        if args.wss:
                            raise DeviceNotFound(
                                f"WebSocketDevice @ wss://{host}:{port} is not reachable")
                        else:
                            raise DeviceNotFound(
                                f"WebSocketDevice @ ws://{host}:{port} is not reachable")
                    except Exception as e:
                        print(f'ERROR {e}')
                        return False
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: put Operation Canceled')
                    if not dev.connected:
                        ws.s.close()
                    return False
            else:
                for file in args.fre:
                    src_file = file
                    if source != '/':
                        if source.startswith('.'):
                            source = source.replace('.', '')
                        dst_file = source + '/' + file.split('/')[-1]
                    else:
                        dst_file = '/' + file.split('/')[-1]
                    if dst_file[-1] == "/":
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += basename
                    print(f"{src_file} -> {devname}:{dst_file}")
                    print(f'\n{src_file} [{os.stat(src_file)[6]/1000:.2f} kB]')
                    try:
                        put_file(ws, src_file, dst_file)
                    except KeyboardInterrupt:
                        print('KeyboardInterrupt: put Operation Canceled')
                        if input('Continue get Operation with next file? [y/n]') == 'y':
                            pass
                        else:
                            raise KeyboardInterrupt
                        if not dev.connected:
                            ws.s.close()
                        time.sleep(0.2)
                        if not dev.connected:
                            ws = connect_ws(host, port, passwd, websec)
                    except socket.timeout:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:
                            if args.wss:
                                raise DeviceNotFound(
                                    f"WebSocketDevice @ wss://{host}:{port} is not reachable")
                            else:
                                raise DeviceNotFound(
                                    f"WebSocketDevice @ ws://{host}:{port} is not reachable")
                        except Exception as e:
                            print(f'ERROR {e}')
                            return False
        if not dev.connected:
            ws.s.close()
        return True


class WebSocketFileIO:
    def __init__(self, dev, args=None, devname=''):
        self.dev = dev
        self.args = args
        self.dev_name = devname

    def put(self, src, dst_file, ppath=False, dev_name=None):
        self.args.m = 'put'
        self.args.s = ''
        wsfileio(self.args, src, dst_file, self.dev_name, self.dev)

    def put_files(self, args, dev_name):
        args.m = 'put'
        wsfileio(args, '', '', dev_name, self.dev)

    def get(self, src, dst_file, ppath=False, dev_name=None):
        self.args.m = 'get'
        self.args.s = ''
        wsfileio(self.args, src, dst_file, self.dev_name, self.dev)

    def get_files(self, args, dev_name):
        args.m = 'get'
        wsfileio(args, '', ('', ''), dev_name, self.dev)


def wstool(args, dev_name):
    if not dev_name:
        if vars(args)['@'] is not None:
            dev_name = vars(args)['@']
    if not args.f and not args.fre:
        print('args -f or -fre required:')
        see_help(args.m)
        sys.exit()
    if args.m == 'put':
        if not args.f and not args.fre:
            print('args -f or -fre required:')
            see_help(args.m)
            sys.exit()
        if args.f:
            if os.path.isdir(args.f):
                os.chdir(args.f)
                args.fre = ['.']
        if not args.fre:
            # One file:
            source = ''
            if args.s == 'sd':
                source += '/' + args.s
            file = args.f
            if args.dir is not None:
                source += '/' + args.dir
            file_in_upy = file.split('/')[-1]
            # Check if file exists:
            if source:
                args.s = source + '/'
            try:
                os.stat(file)[6]
                if not os.path.isdir(file):
                    result = None
                    dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                 auth=args.wss)
                    if args.s:

                        is_dir_cmd = f"import uos, gc; uos.stat('{source}')[0] & 0x4000"
                        is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                        # dev.disconnect()
                        if dev._traceback.decode() in dev.response:
                            try:
                                raise DeviceException(dev.response)
                            except Exception as e:
                                print(e)
                                print(f'Directory {dev_name}:{source} does NOT exist')
                                result = False
                        else:
                            if is_dir:
                                print(f'Uploading file {file_in_upy} @ {dev_name}...')
                                result = wsfileio(args, file, file_in_upy, dev_name,
                                                  dev=dev)
                    else:
                        args.s = source
                        print(f'Uploading file {file_in_upy} @ {dev_name}...')
                        result = wsfileio(args, file, file_in_upy, dev_name, dev)

                    # Reset:
                    if result:
                        if args.rst is None:
                            # time.sleep(0.1)
                            # dev = Device(args.t, args.p, init=True, ssl=args.wss,
                            #              auth=args.wss)
                            time.sleep(0.2)
                            dev.reset(reconnect=False)
                            time.sleep(0.5)
                else:
                    print(f'FileNotFoundError: {file} is a directory')
            except FileNotFoundError as e:
                print('FileNotFoundError:', e)
            except KeyboardInterrupt:
                print('KeyboardInterrupt: put Operation Canceled')
        else:
            # Handle special cases:
            # CASE [cwd]:
            if args.fre[0] == 'cwd' or args.fre[0] == '.':
                args.fre = [fname for fname in os.listdir(
                    './') if os.path.isfile(fname) and not fname.startswith('.')]
                print(f"Files in ./{os.getcwd().split('/')[-1]} to put: ")
            elif '*' in args.fre[0]:
                args.fre = glob.glob(args.fre[0])
                print('Files to put: ')
            else:
                print('Files to put: ')

            files_to_put = []
            for file in args.fre:
                try:
                    filesize = os.stat(file)[6]
                    if not os.path.isdir(file):
                        files_to_put.append(file)
                        print(f'- {file} [{filesize/1000:.2f} kB]')
                    else:
                        filesize = 'IsDirectory'
                        print(f'- {file} [{filesize}]')
                except Exception:
                    filesize = 'FileNotFoundError'
                    print(f'- {file} [{filesize}]')
            args.fre = files_to_put
            # Multiple file:
            source = ''
            if args.s == 'sd':
                source += '/' + args.s
            file = ''
            if args.dir is not None:
                source += '/' + args.dir
            file_in_upy = file.split('/')[-1]
            if source:
                args.s = source
            try:
                dev = Device(args.t, args.p, init=True, ssl=args.wss,
                             auth=args.wss)
                if args.s:

                    is_dir_cmd = f"import uos, gc; uos.stat('{source}')[0] & 0x4000"
                    is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                    # dev.disconnect()
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print(f'Directory {dev_name}:{source} does NOT exist')
                            result = False
                    else:
                        if is_dir:
                            print(f'\nUploading files @ {dev_name}...\n')
                            result = wsfileio(args, 'fre', 'fre', dev_name, dev)
                else:
                    args.s = source
                    print(f'\nUploading files @ {dev_name}...\n')
                    result = wsfileio(args, 'fre', 'fre', dev_name, dev)

                # Reset:
                if result:
                    if args.rst is None:
                        # time.sleep(0.1)
                        # dev = Device(args.t, args.p, init=True,
                        #              ssl=args.wss, auth=args.wss)
                        time.sleep(0.2)
                        dev.reset(reconnect=False)
                        time.sleep(0.2)
                        # dev.disconnect()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: put Operation Canceled')
        return
    elif args.m == 'get':
        if not args.f and not args.fre:
            print('args -f or -fre required:')
            see_help(args.m)
            sys.exit()
        if args.f:
            if '/' in args.f:
                if len(args.f.rsplit('/', 1)) > 1:
                    args.dir, args.f = args.f.rsplit('/', 1)
                    if args.f == '':
                        args.fre = ['.']
        if not args.fre:
            if args.s is None and args.dir is None:
                print(f'Looking for file in {dev_name}:/ dir ...')
                cmd_str = (f"import uos;[(uos.stat(file)[6], file) for file "
                           f"in uos.listdir() if file == '{args.f}' and not "
                           f"uos.stat(file)[0] & 0x4000]")
                dir = ''
            if args.dir is not None or args.s is not None:
                if args.s is not None:
                    args.dir = f'{args.s}/{args.dir}'
                print(f'Looking for file in {dev_name}:/{args.dir} dir')
                cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], file)"
                           f" for file in uos.listdir('/{args.dir}')"
                           f" if file == '{args.f}' and "
                           f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                dir = f'/{args.dir}'
            try:
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print(f'Directory {dev_name}:{dir} does NOT exist')
                        result = False
                if isinstance(file_exists, list) and file_exists:
                    print(f'Downloading file {args.f} @ {dev_name}...')
                    file_to_get = (file_exists[0][0], args.f)
                    if args.s == 'sd':
                        file_to_get = (file_exists[0][0], f'/sd/{args.f}')
                    if args.dir is not None:
                        file_to_get = (file_exists[0][0], f'/{args.dir}/{args.f}')
                    result = wsfileio(args, '', file_to_get, dev_name, dev=dev)
                    print('Done!')
                else:
                    if not file_exists:
                        if dir == '':
                            dir = '/'
                        print(f'File Not found in {dev_name}:{dir} directory or')
                        if dir == '/':
                            dir = ''
                        print(f'{dev_name}:{dir}/{args.f} is a directory')
            except DeviceNotFound as e:
                print(f'ERROR {e}')
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
        else:
            # list to filter files:
            # regular names:
            # wildcard names:
            # cwd:
            filter_files = []
            for file in args.fre:
                if file not in ['cwd', '.']:
                    filter_files.append(file.replace(
                        '.', '\.').replace('*', '.*') + '$')
            # print(filter_files)
            if args.s is None and args.dir is None:
                print(f'Looking for files in {dev_name}:/ dir ...')
                if filter_files:
                    cmd_str = ("import uos;[(uos.stat(file)[6], file) for file in "
                               "uos.listdir() if any([patt.match(file) for patt in "
                               "pattrn]) and not uos.stat(file)[0] & 0x4000]")
                else:
                    cmd_str = ("import uos;[(uos.stat(file)[6], file) for file "
                               "in uos.listdir() if not "
                               "uos.stat(file)[0] & 0x4000]")
                dir = ''
            elif args.dir is not None or args.s is not None:
                if args.s is not None:
                    args.dir = f'{args.s}/{args.dir}'
                print(f'Looking for files in {dev_name}:/{args.dir} dir')
                if filter_files:
                    cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], file) "
                               f"for file in uos.listdir('/{args.dir}') if "
                               f"any([patt.match(file) for patt in pattrn]) and "
                               f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                else:
                    cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], file)"
                               f"for file in uos.listdir('/{args.dir}') if "
                               f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                dir = f'/{args.dir}'
            try:
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                if filter_files:
                    if len(f"filter_files = {filter_files}") < 250:
                        filter_files_cmd = f"filter_files = {filter_files}"
                        dev.cmd(filter_files_cmd, silent=True)
                    else:
                        dev.cmd("filter_files = []", silent=True)
                        for i in range(0, len(filter_files), 15):
                            filter_files_cmd = f"filter_files += {filter_files[i:i+15]}"
                            dev.cmd(filter_files_cmd, silent=True)
                    dev.cmd("import re; pattrn = [re.compile(f) for "
                            "f in filter_files]", silent=True)
                    cmd_str += ';import gc;del(filter_files);del(pattrn);gc.collect()'
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print(f'Directory {dev_name}:{dir} does NOT exist')
                        result = False
                else:
                    files_to_get = []
                    # Handle special cases:
                    # CASE [cwd]:
                    if len(args.fre) == 1:
                        if args.fre[0] == 'cwd' or args.fre[0] == '.':
                            args.fre = file_exists
                        elif '*' in args.fre[0]:
                            start_exp, end_exp = args.fre[0].split('*')
                            args.fre = [file for file in file_exists if
                                        file[1].startswith(start_exp)
                                        and file[1].endswith(end_exp)]
                    if dir == '':
                        dir = '/'
                    print(f'Files in {dev_name}:{dir} to get: \n')
                    # print(file_exists)
                    # print(args.fre)
                    # print([nfile[1] for nfile in file_exists])
                    if file_exists == args.fre:
                        args.fre = [nfile[1] for nfile in file_exists]
                    for file in args.fre:
                        if file in [nfile[1] for nfile in file_exists]:
                            for sz, nfile in file_exists:
                                # print(file, nfile)
                                if file == nfile:
                                    files_to_get.append((sz, nfile))
                                    print(f'- {nfile} [{sz/1000:.2f} kB]')
                        elif '*' in file:
                            start_exp, end_exp = file.split('*')
                            for reg_file in file_exists:
                                if reg_file[1].startswith(start_exp) and reg_file[1].endswith(end_exp):
                                    files_to_get.append(reg_file)
                                    print(
                                        f'- {reg_file[1]} [{reg_file[0]/1000:.2f} kB]')
                        else:
                            filesize = 'FileNotFoundError'
                            print(f'- {file} [{filesize}]')
                    if files_to_get:
                        print(f'\nDownloading files @ {dev_name}...')
                        # file_to_get = args.f
                        if args.dir is not None:
                            args.fre = [(file[0], f'/{args.dir}/{file[1]}')
                                        for file in files_to_get]
                        else:
                            args.fre = files_to_get
                        wsfileio(args, '', ('', ''), dev_name, dev=dev)
                        print('Done!')
                    else:
                        if dir == '':
                            dir = '/'
                        print(f'Files Not found in {dev_name}:{dir} directory')
            except DeviceNotFound as e:
                print(f'ERROR {e}')
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
        return

# TODO: TEST ALL CASES
# TODO: DEBUG DSYNCIO
# TODO: DEBUG RSYNCIO
# FIX SERIALIO GET PATTRN MATCH
# FIX BLEIO GET PATTRN MATCH
