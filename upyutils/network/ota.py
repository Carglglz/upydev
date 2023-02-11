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
    def __init__(self, host, port, check_sha, tls=False, log=None, read_size=512):
        self.part = Partition(Partition.RUNNING).get_next_update()
        self.sha = hashlib.sha256()
        self.block = 0
        self.buf = bytearray(BLOCKLEN)
        self._tmp_buf = b""
        self.buflen = 0
        self._key = f"SSL_key{binascii.hexlify(unique_id()).decode()}.der"
        self._cert = f"SSL_certificate{binascii.hexlify(unique_id()).decode()}.der"
        self._cadata = "ROOT_CA_cert.pem"
        self.tls = tls
        self.log = log
        if tls:
            with open(self._key, "rb") as keyfile:
                self.key = keyfile.read()
            with open(self._cert, "rb") as certfile:
                self.cert = certfile.read()
            with open(self._cadata, "rb") as cadatafile:
                self.cadata = cadatafile.read()
        self.cli_soc = self.connect(host, port)
        self.check_sha = check_sha
        self.read_size = read_size
        self._total_blocks = 0
        self._OK = False

    def connect(self, host, port):
        cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, port)[0][-1]
        cli_soc.connect(soc_addr)
        if self.tls:
            try:
                cli_soc = ssl.wrap_socket(
                    cli_soc,
                    key=self.key,
                    cert=self.cert,
                    cadata=self.cadata,
                    cert_reqs=ssl.CERT_REQUIRED,
                )
            except Exception as e:
                if self.log:
                    self.log.exception(e, "SSL ERROR")
                raise e
        return cli_soc

    # handle processes one message with a chunk of data in msg. The sequence number seq needs
    # to increment sequentially and the last call needs to have last==True as well as the
    # sha set to the hashlib.sha256(entire_data).hexdigest().

    def do_ota(self, blocks=0, debug=False):
        self._total_blocks = blocks
        time.sleep(1)
        if self.tls:
            self.cli_soc.setblocking(False)
        else:
            self.cli_soc.settimeout(2)
        nb = 0
        idx = 0
        while True:
            try:
                if self.tls:
                    self._tmp_buf = self.cli_soc.read(self.read_size)
                else:
                    self._tmp_buf = self.cli_soc.recv(self.read_size)
                nb = len(self._tmp_buf)
                if self._tmp_buf != b"":
                    self.buf[idx : idx + nb] = self._tmp_buf
                    idx += nb

                    if idx < BLOCKLEN:
                        if self.block < self._total_blocks:
                            while idx < BLOCKLEN:
                                if BLOCKLEN - idx < self.read_size:
                                    if self.tls:
                                        self._tmp_buf = self.cli_soc.read(
                                            BLOCKLEN - idx
                                        )
                                    else:
                                        self._tmp_buf = self.cli_soc.recv(
                                            BLOCKLEN - idx
                                        )
                                else:
                                    if self.tls:
                                        self._tmp_buf = self.cli_soc.read(
                                            self.read_size
                                        )
                                    else:
                                        self._tmp_buf = self.cli_soc.recv(
                                            self.read_size
                                        )

                                nb = len(self._tmp_buf)
                                if self._tmp_buf != b"":
                                    self.buf[idx : idx + nb] = self._tmp_buf
                                    idx += nb

                    self.buflen = idx
                    self.sha.update(self.buf)
                    if self.buflen == BLOCKLEN:
                        self.part.writeblocks(self.block, self.buf)
                    if debug:
                        print(f"BLOCK # {self.block}; LEN = {self.buflen}", end="\r")
                    self.block += 1
                    idx = 0
                    if self.block == self._total_blocks:
                        break
                else:
                    print("END OF FILE")
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
                "SHA mismatch calc:{} check={}".format(calc_sha, self.check_sha)
            )
        else:
            self._OK = True
        self.part.set_boot()
        return True
