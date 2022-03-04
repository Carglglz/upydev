import socket
import ssl
import os
import time
import sys
# import select
import gc
from ubinascii import hexlify
from machine import unique_id
# from hashlib import sha256
import re


class SSL_socket_client_repl:
    """
    SSL Socket client simple class repl
    """

    def __init__(self, host, port=8443, buff=1024, init=True, auth=True):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.auth = auth
        self._key = 'SSL_key{}.der'.format(hexlify(unique_id()).decode())
        self._cert = 'SSL_certificate{}.der'.format(hexlify(unique_id()).decode())
        self.key = None
        self.cert = None
        with open(self._key, 'rb') as keyfile:
            self.key = keyfile.read()
        with open(self._cert, 'rb') as certfile:
            self.cert = certfile.read()
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.wrepl = None
        if hasattr(os, 'dupterm_notify'):
            self.cli_soc.setsockopt(socket.SOL_SOCKET, 20, os.dupterm_notify)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(buff)
        self.buff_size = buff
        if init:
            print('>>> ')
            time.sleep(0.5)
            self.connect_SOC()
            # self.key = None
            # self.cert = None

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        # self.cli_soc.settimeout(1)
        if self.auth:
            self.cli_soc = ssl.wrap_socket(self.cli_soc, key=self.key,
                                           cert=self.cert)
            assert self.cert == self.cli_soc.getpeercert(
                True), "Peer Certificate Invalid"
        # self.cli_soc = ssl.wrap_socket(self.cli_soc)
        else:
            self.cli_soc = ssl.wrap_socket(self.cli_soc)

        self.cli_soc.setblocking(False)
        # self.cli_soc.settimeout(1)
        print('>>> ')
        self.wrepl = os.dupterm(self.cli_soc, 0)

    def flush(self):
        flushed = 0
        while flushed == 0:
            try:
                self.cli_soc.recv(128)
            except Exception as e:
                flushed = 1
                print('flushed!')

    def send_message(self, message):
        self.cli_soc.write(bytes(message, 'utf-8'))

    def recv_message(self):
        try:
            self.buff[:] = self.cli_soc.read(self.buff_size)
            print(self.buff.decode())
        except Exception as e:
            pass

    def switch_wrepl(self):
        print('>>> ')
        self.cli_soc = os.dupterm(self.wrepl, 0)
        # print('WebREPL enabled!')

    def switch_ssl_repl(self):
        print('>>> ')
        self.wrepl = os.dupterm(self.cli_soc, 0)
        # print('SSL_REPL enabled!')


class SSL_socket_client_tool:
    """
    Socket client simple class io tool
    """

    def __init__(self, host, port=8433, init=False):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(4096)
        self.readable = None
        self.writable = None
        self.exceptional = None

    def connect_SOC(self, key, cert):
        print('>>> ')
        # self.cli_soc.close()
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        time.sleep(0.2)
        self.cli_soc.connect(self.addr)
        # self.cli_soc.settimeout(2)
        self.cli_soc = ssl.wrap_socket(self.cli_soc, key=key,
                                       cert=cert)
        assert cert == self.cli_soc.getpeercert(
            True), "Peer Certificate Invalid"
        self.cli_soc.setblocking(False)
        # self.cli_soc.settimeout(2)

    def put(self, filetoget, size, chunk=4096, dbg=False):
        local_size = 0
        chunk = chunk
        # put_soc = [self.cli_soc]
        # chunk_sizes = [chunk]
        print(size)
        if size < chunk:
            chunk = size
            chunk_rest = size % chunk
        else:
            # chunk_sizes = [chunk for i in range(size//chunk)] + [size % chunk]
            chunk_rest = size % chunk
        with open(filetoget, 'wb') as log:
            pass
        time.sleep(0.1)
        while True:
            try:
                # self.readable, self.writable, self.exceptional = select.select(put_soc,
                #                                                 put_soc,
                #                                                 put_soc)
                # if len(self.readable) == 1:
                if local_size == (size // (chunk))*(chunk):
                    chunk = chunk_rest

                # self.buff = self.cli_soc.read(chunk)  # 4 KB
                # print(self.buff)
                self.buff = self.cli_soc.read(chunk)
                if self.buff is None:
                    if dbg:
                        print('ZERO BYTES')
                    pass
                else:
                    if self.buff != b'':
                        local_size += len(self.buff)
                        with open(filetoget, 'ab') as log:
                            log.write(self.buff)
                        if local_size >= size:
                            break
                    else:
                        break
            except Exception as e:
                if e == KeyboardInterrupt:
                    break
                else:
                    sys.print_exception(e)
        print(local_size)
        self.buff = b''
        gc.collect()

    def get_size(self, filetoget):
        return os.stat(filetoget)[6]

    def get(self, filetoget, chunk=4096, dbg=False):
        size = self.get_size(filetoget)
        remote_size = 0
        chunk = chunk
        write_b = 0
        write_buff = 0
        if size < chunk:
            chunk = size
            chunk_rest = size % chunk
        else:
            # chunk_sizes = [chunk for i in range(size//chunk)] + [size % chunk]
            chunk_rest = size % chunk
        # final_file = b''
        time.sleep(0.1)
        with open(filetoget, 'rb') as log:
            self.buff = log.read(chunk)
            while True:
                try:
                    # print(len(chunk))
                    if self.buff != b'':
                        # in python use 'i'
                        write_b = self.cli_soc.write(self.buff)
                        if isinstance(write_b, int):
                            write_buff += write_b
                            if dbg:
                                print(write_b)
                            if remote_size == (size // (chunk))*(chunk):
                                chunk = chunk_rest
                            # final_file += chunk
                            self.buff = log.read(chunk)
                            remote_size += len(self.buff)
                    else:
                        # print('END OF FILE')
                        # soc.sendall(b'EOF\x8a\xb1\x1a\xcb\x11')
                        # soc.close()
                        # gc.collect()

                        time.sleep(0.1)
                        print(write_buff)
                        break
                except Exception as e:
                    if e == KeyboardInterrupt:
                        break
                    else:
                        sys.print_exception(e)
            # self.buff = b''
            # gc.collect()


def start(host, port, auth=True):
    ssl_repl_serv = SSL_socket_client_repl(host, port=port, auth=auth)
    return ssl_repl_serv


def get_files_cwd():
    return [file for file in os.listdir() if not os.stat(file)[0] & 0x4000]


def get_files_re(reg):
    pattrn = re.compile(reg)
    return [file for file in get_files_cwd() if pattrn.match(file)]


def get_files_dir(filelist):
    return [file for file in get_files_cwd() if file in filelist]
