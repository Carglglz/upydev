#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-25T02:38:19+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T22:52:04+01:00


import socket
import binascii
import ssl
try:
    import network
except Exception as e:
    print('Python 3 version')

key = binascii.unhexlify(
    b'3082013b020100024100cc20643fd3d9c21a0acba4f48f61aadd675f52175a9dcf07fbef'
    b'610a6a6ba14abb891745cd18a1d4c056580d8ff1a639460f867013c8391cdc9f2e573b0f'
    b'872d0203010001024100bb17a54aeb3dd7ae4edec05e775ca9632cf02d29c2a089b563b0'
    b'd05cdf95aeca507de674553f28b4eadaca82d5549a86058f9996b07768686a5b02cb240d'
    b'd9f1022100f4a63f5549e817547dca97b5c658038e8593cb78c5aba3c4642cc4cd031d86'
    b'8f022100d598d870ffe4a34df8de57047a50b97b71f4d23e323f527837c9edae88c79483'
    b'02210098560c89a70385c36eb07fd7083235c4c1184e525d838aedf7128958bedfdbb102'
    b'2051c0dab7057a8176ca966f3feb81123d4974a733df0f958525f547dfd1c271f9022044'
    b'6c2cafad455a671a8cf398e642e1be3b18a3d3aec2e67a9478f83c964c4f1f')
cert = binascii.unhexlify(
    b'308201d53082017f020203e8300d06092a864886f70d01010505003075310b3009060355'
    b'0406130258583114301206035504080c0b54686550726f76696e63653110300e06035504'
    b'070c075468654369747931133011060355040a0c0a436f6d70616e7958595a3113301106'
    b'0355040b0c0a436f6d70616e7958595a3114301206035504030c0b546865486f73744e61'
    b'6d65301e170d3139313231383033333935355a170d3239313231353033333935355a3075'
    b'310b30090603550406130258583114301206035504080c0b54686550726f76696e636531'
    b'10300e06035504070c075468654369747931133011060355040a0c0a436f6d70616e7958'
    b'595a31133011060355040b0c0a436f6d70616e7958595a3114301206035504030c0b5468'
    b'65486f73744e616d65305c300d06092a864886f70d0101010500034b003048024100cc20'
    b'643fd3d9c21a0acba4f48f61aadd675f52175a9dcf07fbef610a6a6ba14abb891745cd18'
    b'a1d4c056580d8ff1a639460f867013c8391cdc9f2e573b0f872d0203010001300d06092a'
    b'864886f70d0101050500034100b0513fe2829e9ecbe55b6dd14c0ede7502bde5d46153c8'
    b'e960ae3ebc247371b525caeb41bbcf34686015a44c50d226e66aef0a97a63874ca5944ef'
    b'979b57f0b3')


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

    def __init__(self, port, buff=1024, key=key, cert=cert, ssl=False):
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
        self._ssl = ssl
        self.key = key
        self.cert = cert

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
        if self._ssl:
            self.conn = ssl.wrap_socket(self.conn, server_side=True,
                                        key=self.key, cert=self.cert)
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
