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
from upydev.helpinfo import see_help
import glob


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
    print('▏{}▏{:>2}{:>5} % | {} | {:>5} KB/s | {}/{} s'.format("█" *index + l_bloc  + " "*((size_bar+1) - len("█" *index + l_bloc)),
                                                                    wheel[index % 4],
                                                                    int((percentage)*100),
                                                                    nb_of_total, speed,
                                                                    str(timedelta(seconds=time_e)).split('.')[0][2:],
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
            t_0 = time.time()
            # sys.stdout.write("Sent %d of %d bytes\r" % (cnt, sz))
            # sys.stdout.flush()
            buf = f.read(1024)
            if not buf:
                break
            ws.write(buf)
            cnt += len(buf)
            loop_index_f = (cnt/sz)*size_bar
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = "{:.2f}/{:.2f} KB".format(cnt/(1024), sz/(1024))
            percentage = cnt/sz
            t_elapsed = time.time() - t_start
            t_speed = "{:^2.2f}".format((cnt/(1024))/t_elapsed)
            ett = sz / (cnt / t_elapsed)
            if pb:
                do_pg_bar(loop_index, wheel, nb_of_total, t_speed, t_elapsed,
                          loop_index_l, percentage, ett, size_bar)
            else:
                sys.stdout.write("Sent %d of %d bytes\r" % (cnt, sz))
                sys.stdout.flush()

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
                    loop_index_f = (cnt/sz_r)*size_bar
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = "{:.2f}/{:.2f} KB".format(cnt/(1024), sz_r/(1024))
                    percentage = cnt / sz_r
                    t_elapsed = time.time() - t_start
                    t_speed = "{:^2.2f}".format((cnt/(1024))/t_elapsed)
                    ett = sz_r / (cnt / t_elapsed)
                    do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
                              t_elapsed, loop_index_l, percentage, ett, size_bar)
                else:
                    sys.stdout.write("Received %d bytes\r" % cnt)
                    sys.stdout.flush()
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

    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]
    try:
        if websec:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            # sock = context.wrap_socket(sock, server_hostname=hostname)
            s = context.wrap_socket(s)
            s.connect(addr)
            wss_helper_host.client_handshake(s, ssl=True)
        else:
            s.connect(addr)
        # s = s.makefile("rwb")
            websocket_helper.client_handshake(s)
    except socket.timeout as e:
        # print(e, 'Device {} unreachable'.format(devname))
        try:
            if websec:
                raise DeviceNotFound("WebSocketDevice @ wss://{}:{} is not reachable".format(host, port))
            else:
                raise DeviceNotFound("WebSocketDevice @ ws://{}:{} is not reachable".format(host, port))
        except Exception as e:
            print('ERROR {}'.format(e))
            return False

    ws = websocket(s)

    login(ws, passwd)
    # print("Remote WebREPL version:", get_ver(ws))

    # Set websocket to send data marked as "binary"
    ws.ioctl(9, 2)

    return ws


def wsfileio(args, file, upyfile, devname, dev=None):
    op = args.m
    passwd = args.p
    websec = args.wss
    multiple_files = args.fre
    source = args.s

    if op == 'get':
        source = ''
        if not websec:
            host, port, src_file = args.t, 8266, source + upyfile
        else:
            host, port, src_file = args.t, 8833, source + upyfile
        dst_file = '.'
        if os.path.isdir(dst_file):
            basename = src_file.rsplit("/", 1)[-1]
            dst_file += "/" + basename
    elif op == 'put':
        if not websec:
            host, port, dst_file = args.t, 8266, source + upyfile
        else:
            host, port, dst_file = args.t, 8833, source + upyfile
        src_file = file
        if dst_file[-1] == "/":
            basename = src_file.rsplit("/", 1)[-1]
            dst_file += basename

    # if True:
        # print("op:%s, host:%s, port:%d, passwd:%s." %
        #       (op, host, port, '*'*len(passwd)))
    if not args.fre:
        if op == 'put':
            abs_dst_file = dst_file
            if not dst_file.startswith('/'):
                abs_dst_file = '/{}'.format(dst_file)
            print("{} -> {}:{}".format(src_file, devname, abs_dst_file))
        if op == 'get':
            abs_src_file = src_file
            if not src_file.startswith('/'):
                abs_src_file = '/{}'.format(src_file)
            print("{}:{} -> {}".format(devname, abs_src_file, dst_file))
            if dev:
                dev.cmd("import uos, gc; uos.stat('{}')[6]; gc.collect()".format(src_file), silent=True)
                size_file_to_get = dev.output

    else:
        if op == 'get':

            sizes_files_to_get = []
            for fsz in args.fre:
                sz_cmd = "import uos, gc; uos.stat('{}')[6]; gc.collect()".format(fsz)
                sizes_files_to_get.append(dev.cmd(sz_cmd, silent=True, rtn_resp=True))

    # HERE CATCH -wss and do handshake
    if dev:
        if dev.connected:
            dev.disconnect()
    time.sleep(0.1)

    ws = connect_ws(host, port, passwd, websec)
    if ws:

        if op == "get":
            if not args.fre:
                print('\n{} [{:.2f} KB]'.format(src_file, dev.output/1024))
                try:
                    get_file(ws, dst_file, src_file, size_file_to_get)
                except socket.timeout as e:
                    # print(e, 'Device {} unreachable'.format(devname))
                    try:
                        if args.wss:
                            raise DeviceNotFound("WebSocketDevice @ wss://{}:{} is not reachable".format(host, port))
                        else:
                            raise DeviceNotFound("WebSocketDevice @ ws://{}:{} is not reachable".format(host, port))
                    except Exception as e:
                        print('ERROR {}'.format(e))
                        return False
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: get Operation Cancelled')
                    ws.s.close()
                    return False
            else:
                fz_dict = dict(zip(args.fre, sizes_files_to_get))
                for file in args.fre:
                    src_file = file
                    dst_file = '.'
                    if os.path.isdir(dst_file):
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += "/" + basename
                    size_file_to_get = fz_dict[src_file]
                    abs_src_file = src_file
                    if not src_file.startswith('/'):
                        abs_src_file = '/{}'.format(src_file)
                    print("{}:{} -> {}".format(devname, abs_src_file, dst_file))
                    print('\n{} [{:.2f} KB]'.format(src_file, size_file_to_get/1024))
                    try:
                        get_file(ws, dst_file, src_file, size_file_to_get)
                    except KeyboardInterrupt as e:
                        print('KeyboardInterrupt: get Operation Cancelled')
                        ws.s.close()
                        time.sleep(0.2)
                        ws = connect_ws(host, port, passwd, websec)
                    except socket.timeout as e:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:
                            if args.wss:
                                raise DeviceNotFound("WebSocketDevice @ wss://{}:{} is not reachable".format(host, port))
                            else:
                                raise DeviceNotFound("WebSocketDevice @ ws://{}:{} is not reachable".format(host, port))
                        except Exception as e:
                            print('ERROR {}'.format(e))
                            return False

        elif op == "put":
            if not args.fre:
                print('\n{} [{:.2f} KB]'.format(src_file, os.stat(src_file)[6]/1024))
                try:
                    put_file(ws, src_file, dst_file)
                except socket.timeout as e:
                    # print(e, 'Device {} unreachable'.format(devname))
                    try:
                        if args.wss:
                            raise DeviceNotFound("WebSocketDevice @ wss://{}:{} is not reachable".format(host, port))
                        else:
                            raise DeviceNotFound("WebSocketDevice @ ws://{}:{} is not reachable".format(host, port))
                    except Exception as e:
                        print('ERROR {}'.format(e))
                        return False
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: put Operation Cancelled')
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
                    print("{} -> {}:{}".format(src_file, devname, dst_file))
                    print('\n{} [{:.2f} KB]'.format(src_file, os.stat(src_file)[6]/1024))
                    try:
                        put_file(ws, src_file, dst_file)
                    except KeyboardInterrupt as e:
                        print('KeyboardInterrupt: put Operation Cancelled')
                        ws.s.close()
                        time.sleep(0.2)
                        ws = connect_ws(host, port, passwd, websec)
                    except socket.timeout as e:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:
                            if args.wss:
                                raise DeviceNotFound("WebSocketDevice @ wss://{}:{} is not reachable".format(host, port))
                            else:
                                raise DeviceNotFound("WebSocketDevice @ ws://{}:{} is not reachable".format(host, port))
                        except Exception as e:
                            print('ERROR {}'.format(e))
                            return False
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
        wsfileio(args, '', '', dev_name, self.dev)


def wstool(args, dev_name):
    if not args.f and not args.fre:
        print('args -f or -fre required:')
        see_help(args.m)
        sys.exit()
    if args.m == 'put':
        if not args.f and not args.fre:
            print('args -f or -fre required:')
            see_help(args.m)
            sys.exit()
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
                    if args.s:
                        dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                     auth=args.wss)
                        is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                        is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                        dev.disconnect()
                        if dev._traceback.decode() in dev.response:
                            try:
                                raise DeviceException(dev.response)
                            except Exception as e:
                                print(e)
                                print('Directory {}:{} does NOT exist'.format(dev_name, source))
                                result = False
                        else:
                            if is_dir:
                                print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                                result = wsfileio(args, file, file_in_upy, dev_name)
                    else:
                        args.s = source
                        print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                        result = wsfileio(args, file, file_in_upy, dev_name)

                    # Reset:
                    if result:
                        if args.rst is None:
                            time.sleep(0.1)
                            dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                         auth=args.wss)
                            time.sleep(0.2)
                            dev.reset(reconnect=False)
                            time.sleep(0.5)
                else:
                    print('FileNotFoundError: {} is a directory'.format(file))
            except FileNotFoundError as e:
                print('FileNotFoundError:', e)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: put Operation Cancelled')
        else:
            # Handle special cases:
            # CASE [cwd]:
            if args.fre[0] == 'cwd' or args.fre[0] == '.':
                args.fre = [fname for fname in os.listdir('./') if os.path.isfile(fname) and not fname.startswith('.')]
                print('Files in ./{} to put: '.format(os.getcwd().split('/')[-1]))
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
                        print('- {} [{:.2f} KB]'.format(file, filesize/1024))
                    else:
                        filesize = 'IsDirectory'
                        print('- {} [{}]'.format(file, filesize))
                except Exception as e:
                    filesize = 'FileNotFoundError'
                    print('- {} [{}]'.format(file, filesize))
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
                if args.s:
                    dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                 auth=args.wss)
                    is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                    is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                    dev.disconnect()
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print('Directory {}:{} does NOT exist'.format(dev_name, source))
                            result = False
                    else:
                        if is_dir:
                            print('\nUploading files @ {}...\n'.format(dev_name))
                            result = wsfileio(args, 'fre', 'fre', dev_name)
                else:
                    args.s = source
                    print('\nUploading files @ {}...\n'.format(dev_name))
                    result = wsfileio(args, 'fre', 'fre', dev_name)

                # Reset:
                if result:
                    if args.rst is None:
                        time.sleep(0.1)
                        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                        time.sleep(0.2)
                        dev.reset(reconnect=False)
                        time.sleep(0.2)
                        # dev.disconnect()
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: put Operation Cancelled')
        return
    elif args.m == 'get':
        if not args.f and not args.fre:
            print('args -f or -fre required:')
            see_help(args.m)
            sys.exit()
        if not args.fre:
            if args.s is None and args.dir is None:
                print('Looking for file in {}:/ dir ...'.format(dev_name))
                cmd_str = "import uos;'{}' in uos.listdir()".format(args.f)
                dir = ''
            if args.dir is not None or args.s is not None:
                if args.s is not None:
                    args.dir = '{}/{}'.format(args.s, args.dir)
                print('Looking for file in {}:/{} dir'.format(dev_name, args.dir))
                cmd_str = "import uos; '{}' in uos.listdir('/{}')".format(args.f, args.dir)
                dir = '/{}'.format(args.dir)
            try:
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print('Directory {}:{} does NOT exist'.format(dev_name, dir))
                        result = False
                else:
                    if file_exists is True:
                        cmd_str = "import uos; not uos.stat('{}')[0] & 0x4000 ".format(dir + '/' + args.f)
                        is_file = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if file_exists is True and is_file:
                    print('Downloading file {} @ {}...'.format(args.f, dev_name))
                    file_to_get = args.f
                    if args.s == 'sd':
                        file_to_get = '/sd/{}'.format(args.f)
                    if args.dir is not None:
                        file_to_get = '/{}/{}'.format(args.dir, args.f)
                    # if not args.wss:
                    #     copyfile_str = 'upytool -p {} {}:{} .{}'.format(
                    #         passwd, target, file_to_get, id_file)
                    result = wsfileio(args, '', file_to_get, dev_name, dev=dev)
                    print('Done!')
                else:
                    if file_exists is False:
                        if dir == '':
                            dir = '/'
                        print('File Not found in {}:{} directory'.format(dev_name, dir))
                    elif file_exists is True:
                        if is_file is not True:
                            print('{}:{} is a directory'.format(dev_name, dir + '/' + args.f))
            except DeviceNotFound as e:
                print('ERROR {}'.format(e))
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: get Operation Cancelled')
        else:
            if args.s is None and args.dir is None:
                print('Looking for files in {}:/ dir ...'.format(dev_name))
                cmd_str = "import uos;[file for file in uos.listdir() if not uos.stat(file)[0] & 0x4000]"
                dir = ''
            elif args.dir is not None or args.s is not None:
                if args.s is not None:
                    args.dir = '{}/{}'.format(args.s, args.dir)
                print('Looking for files in {}:/{} dir'.format(dev_name, args.dir))
                cmd_str = "import uos;[file for file in uos.listdir('/{0}') if not uos.stat('/{0}/'+file)[0] & 0x4000]".format(args.dir)
                dir = '/{}'.format(args.dir)
            try:
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print('Directory {}:{} does NOT exist'.format(dev_name, dir))
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
                            args.fre = [file for file in file_exists if file.startswith(start_exp) and file.endswith(end_exp)]
                    if dir == '':
                        dir = '/'
                    print('Files in {}:{} to get: '.format(dev_name, dir))
                    for file in args.fre:
                        if file in file_exists:
                            files_to_get.append(file)
                            print('- {} '.format(file))
                        elif '*' in file:
                            start_exp, end_exp = file.split('*')
                            for reg_file in file_exists:
                                if reg_file.startswith(start_exp) and reg_file.endswith(end_exp):
                                    files_to_get.append(reg_file)
                                    print('- {} '.format(reg_file))
                        else:
                            filesize = 'FileNotFoundError'
                            print('- {} [{}]'.format(file, filesize))
                    if files_to_get:
                        print('Downloading files @ {}...'.format(dev_name))
                        # file_to_get = args.f
                        if args.dir is not None:
                            args.fre = ['/{}/{}'.format(args.dir, file) for file in files_to_get]
                        else:
                            args.fre = files_to_get
                        wsfileio(args, '', '', dev_name, dev=dev)
                        print('Done!')
                    else:
                        if dir == '':
                            dir = '/'
                        print('Files Not found in {}:{} directory'.format(dev_name, dir))
            except DeviceNotFound as e:
                print('ERROR {}'.format(e))
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: get Operation Cancelled')
        return
