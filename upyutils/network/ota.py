# Adapted from:
# @tve
# https://github.com/tve/mqboard/blob/master/mqrepl/mqrepl.py#L22-L84
# MicroPython forum thread
# https://forum.micropython.org/viewtopic.php?f=18&t=7066&p=61715&hilit=ota#p61715
# MicroPython docs [Flash partitions]
# http://docs.micropython.org/en/latest/library/esp32.html

from esp32 import Partition
import hashlib
from micropython import const
import binascii
import socket
import gc
import time
from machine import unique_id
import ssl


BLOCKLEN = const(4096)  # data bytes in a flash block

# OTA manages a MicroPython firmware update over-the-air.
# It assumes that there are two "app" partitions in the partition table and updates the one
# that is not currently running. When the update is complete, it sets the new partition as
# the next one to boot. It does not reset/restart, use machine.reset() explicitly.


class OTA:
    def __init__(self, host, port, check_sha, tls=False):
        self.part = Partition(Partition.RUNNING).get_next_update()
        self.sha = hashlib.sha256()
        self.block = 0
        self.buf = bytearray(BLOCKLEN)
        self.buflen = 0
        self._key = f'SSL_key{binascii.hexlify(unique_id()).decode()}.der'
        self._cert = f'SSL_certificate{binascii.hexlify(unique_id()).decode()}.der'
        self.tls = tls
        if tls:
            with open(self._key, 'rb') as keyfile:
                self.key = keyfile.read()
            with open(self._cert, 'rb') as certfile:
                self.cert = certfile.read()
        self.cli_soc = self.connect(host, port)
        self.check_sha = check_sha
        self._total_blocks = 0
        self._OK = False

    def connect(self, host, port):
        cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, port)[0][-1]
        cli_soc.connect(soc_addr)
        if self.tls:
            try:
                cli_soc = ssl.wrap_socket(cli_soc, key=self.key, cert=self.cert,
                                          ca_certs=self.cert,
                                          cert_reqs=ssl.CERT_REQUIRED)
            except Exception:
                cli_soc = ssl.wrap_socket(cli_soc, key=self.key, cert=self.cert)
            # assert self.cert == cli_soc.getpeercert(True), "Peer Certificate Invalid"
        return cli_soc

    # handle processes one message with a chunk of data in msg. The sequence number seq needs
    # to increment sequentially and the last call needs to have last==True as well as the
    # sha set to the hashlib.sha256(entire_data).hexdigest().

    def do_ota(self, blocks=0, debug=False):
        # final_file = b'
        self._total_blocks = blocks
        time.sleep(1)
        if self.tls:
            self.cli_soc.setblocking(False)
        else:
            self.cli_soc.settimeout(2)
        while True:
            try:
                if self.tls:
                    self.buf = self.cli_soc.read(BLOCKLEN)
                else:
                    self.buf = self.cli_soc.recv(BLOCKLEN)  # 2 KB
                if self.buf != b'':
                    if len(self.buf) < BLOCKLEN:
                        if self.tls:
                            if self.block < self._total_blocks - 1:
                                while len(self.buf) < BLOCKLEN:
                                    self.buf += self.cli_soc.read(
                                        BLOCKLEN - len(self.buf))
                        else:
                            if self.block < self._total_blocks - 1:
                                while len(self.buf) < BLOCKLEN:
                                    self.buf += self.cli_soc.recv(
                                        BLOCKLEN - len(self.buf))
                    self.buflen = len(self.buf)
                    self.sha.update(self.buf)
                    if self.buflen == BLOCKLEN:
                        self.part.writeblocks(self.block, self.buf)
                    if debug:
                        print(f"BLOCK # {self.block}; LEN = {self.buflen}", end='\r')
                    self.block += 1
                    if self.block == self._total_blocks:
                        break
                else:
                    print('END OF FILE')
                    break
            except Exception as e:
                if e == KeyboardInterrupt:
                    break
        gc.collect()

    def check_ota(self, debug=False):
        del self.buf
        calc_sha = binascii.hexlify(self.sha.digest()).decode()
        if calc_sha != self.check_sha:
            raise ValueError(
                "SHA mismatch calc:{} check={}".format(calc_sha, self.check_sha))
        else:
            self._OK = True
        self.part.set_boot()
        return True
