#!/usr/bin/env python
import socket
import ssl
import os
import time
try:
    import network
except Exception as e:
    print('Python 3 version')


class SSL_socket_client:
    """
    SSL Socket client simple class
    """

    def __init__(self, host, port=8443, buff=1024, auth=False):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(buff)
        self.buff_size = buff
        self._key = 'SSL_key.der'
        self._cert = 'SSL_certificate.der'
        self.key = None
        self.cert = None
        self.auth = auth
        with open(self._key, 'rb') as keyfile:
            self.key = keyfile.read()
        with open(self._cert, 'rb') as certfile:
            self.cert = certfile.read()

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)

        if self.auth:
            self.cli_soc = ssl.wrap_socket(self.cli_soc, key=self.key,
                                           cert=self.cert)
        else:
            self.cli_soc = ssl.wrap_socket(self.cli_soc)
        self.cli_soc.setblocking(False)

    def send_message(self, message):
        self.cli_soc.write(bytes(message, 'utf-8'))

    def recv_message(self):
        try:
            self.buff[:] = self.cli_soc.read(self.buff_size)
            print(self.buff.decode())
        except Exception as e:
            pass


class SSL_socket_client_repl:
    """
    SSL Socket client simple repl class
    """

    def __init__(self, host, port=8443, buff=1024, init=True, auth=False):
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
        self._key = 'SSL_key.der'
        self._cert = 'SSL_certificate.der'
        self.key = None
        self.cert = None
        self.auth = auth
        with open(self._key, 'rb') as keyfile:
            self.key = keyfile.read()
        with open(self._cert, 'rb') as certfile:
            self.cert = certfile.read()
        if init:
            print('>>> ')
            time.sleep(2)
            self.connect_SOC()

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        if self.auth:
            self.cli_soc = ssl.wrap_socket(self.cli_soc, key=self.key,
                                           cert=self.cert)
        else:
            self.cli_soc = ssl.wrap_socket(self.cli_soc)
        self.cli_soc.setblocking(False)
        print('>>> ')
        self.wrepl = os.dupterm(self.cli_soc, 0)

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


class HOST_SSL_socket_server:
    """
    SSL HOST Socket server simple class
    """

    def __init__(self, port=8443, buff=1024, auth=False, key='SSL_key.pem',
                 cert='SSL_certificate.pem'):
        try:
            self.host = network.WLAN(network.STA_IF).ifconfig()[0]
            print(self.host)
        except Exception as e:
            try:
                self.host = self.find_localip()
                print(self.host)
            except Exception as e:
                print(e)
        self.host_ap = '192.168.4.1'
        self.port = port
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = None
        self.b_buff = bytearray(buff)
        self.buff = b''
        self.message = b''
        self.prompt = b'>>> '
        self.prompt_seen = True
        self.conn = None
        self.addr_client = None
        self.output = None
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.key = key
        self.cert = cert
        self.auth = auth

    def find_localip(self):
        ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_soc.connect(('8.8.8.8', 1))
        local_ip = ip_soc.getsockname()[0]
        ip_soc.close()
        return local_ip

    def start_SOC(self):
        self.serv_soc.bind((self.host, self.port))
        self.serv_soc.listen(1)
        print('Server listening...')
        # self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(keyfile=self.key, certfile=self.cert)
        if self.auth:
            self.context.verify_mode = ssl.CERT_REQUIRED
            self.context.load_verify_locations(cafile=self.cert)
        self.conn, self.addr_client = self.serv_soc.accept()
        self.conn = self.context.wrap_socket(self.conn, server_side=True)
        print('Connection received...')
        print(self.addr_client)
        self.conn.settimeout(0)

    def flush_conn(self):
        flushed = 0
        while flushed < 2:
            try:
                self.conn.recv()
            except Exception as e:
                flushed += 1

    def send_message(self, message):
        self.conn.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        try:
            self.buff = b''
            self.buff += self.conn.recv()
            print(self.buff.decode())
        except Exception as e:
            if self.buff.decode() == '':
                pass
            else:
                print(self.buff.decode())
            pass

    def ssl_repl(self, inp, just_recv=False):
        self.buff = b''
        if not just_recv:
            self.send_message(inp+'\r')
        # WAIT TILL DATA AVAILABLE
        # CATCH PROMPT
        while True:
            try:
                self.message = self.conn.recv()
                # print('DATA RECEIVED: ', self.message)
                break
            except Exception as e:
                pass
        # CATCH MESSAGE
        while True:
            try:
                self.message = self.conn.recv()
                self.buff += self.message
                if self.message == b'>>> ':
                    break
            except Exception as e:
                pass
        # WAIT TILL NO DATA AVAILABLE
        while True:
            try:
                self.message = self.conn.recv()
                self.buff += self.message
                if self.message == b'>>> ':
                    break
            except Exception as e:
                break
        if self.buff != b'':
            self.output = '\n'.join([m.decode() for m in self.buff.splitlines()[1:-1]])
            if self.output != '':
                print(self.output)
