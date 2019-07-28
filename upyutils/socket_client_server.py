#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-25T02:38:19+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T22:52:04+01:00


import socket
try:
    import network
except Exception as e:
    print('Python 3 version')


class socket_client:
    """
    Socket client simple class
    """

    def __init__(self, host, port, buff=1024):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(buff)

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        self.cli_soc.settimeout(1)

    def flush(self):
        flushed = 0
        while flushed == 0:
            try:
                self.cli_soc.recv(128)
            except Exception as e:
                flushed = 1
                print('flushed!')

    def send_message(self, message):
        self.cli_soc.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.cli_soc.recv(len(self.buff))
        print(self.buff.decode())


class socket_server:
    """
    Socket server simple class
    """

    def __init__(self, port, buff=1024):
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
        self.buff = bytearray(buff)
        self.conn = None
        self.addr_client = None

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
        self.conn, self.addr_client = self.serv_soc.accept()
        print('Connection received...')
        print(self.addr_client)
        self.conn.settimeout(1)

    def start_SOC_AP(self):
        self.serv_soc.bind((self.host_ap, self.port))
        self.serv_soc.listen(1)
        print('Server listening...')
        self.conn, self.addr_client = self.serv_soc.accept()
        print('Connection received...')
        print(self.addr_client)
        self.conn.settimeout(1)

    def flush(self):
        flushed = 0
        while flushed == 0:
            try:
                self.serv_soc.recv(128)
            except Exception as e:
                flushed = 1
                print('flushed!')

    def send_message(self, message):
        self.conn.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.conn.recv(len(self.buff))
        print(self.buff.decode())
