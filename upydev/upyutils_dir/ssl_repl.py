import socket
import ssl
import os
import time


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


def start(host, port):
    ssl_repl_serv = SSL_socket_client_repl(host, port=port)
    return ssl_repl_serv
