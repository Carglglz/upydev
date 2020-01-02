import socket
import ssl
import os
import time
import sys
# import select
import gc


class SSL_socket_client_repl:
    """
    Socket client simple class repl
    """

    def __init__(self, host, port=8443, buff=1024, init=True):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.wrepl = None
        self.cli_soc.setsockopt(socket.SOL_SOCKET, 20, os.dupterm_notify)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(buff)
        self.buff_size = buff
        if init:
            print('>>> ')
            time.sleep(2)
            self.connect_SOC()

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        # self.cli_soc.settimeout(1)
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

    def connect_SOC(self):
        print('>>> ')
        # self.cli_soc.close()
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        time.sleep(1)
        self.cli_soc.connect(self.addr)
        # self.cli_soc.settimeout(2)
        self.cli_soc = ssl.wrap_socket(self.cli_soc)
        self.cli_soc.setblocking(False)
        # self.cli_soc.settimeout(2)

    def put(self, filetoget, size, chunk=4096, dbg=False):
        # final_file = b''
        # self.connect_SOC()  # for file in filelist
        local_size = 0
        index = 0
        chunk = chunk
        # put_soc = [self.cli_soc]
        # chunk_sizes = [chunk]
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
                        index += 1
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
        self.buff = b''
        gc.collect()


def start(host, port):
    ssl_repl_serv = SSL_socket_client_repl(host, port=port)
    return ssl_repl_serv
