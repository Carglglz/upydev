import socket
import hashlib
from binascii import hexlify
import os
import time
import sys
from datetime import timedelta
import select
import ssl
import getpass
from upydev import __path__ as _PATH

BLOCKLEN = 4096

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


class OTAServer:
    """
    OTA Server Class
    """

    def __init__(self, dev, port, firmware, buff=BLOCKLEN, tls=False, zt=False):

        try:
            self.host = self.find_localip()
            # print(self.host)
        except Exception as e:
            print(e)
        self.dev = dev
        self.port = port
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = None
        self.buff = bytearray(buff)
        self.conn = None
        self.addr_client = None
        self._use_tls = tls
        self.host_fwd = None
        if zt:
            self.host_fwd = self.dev.hostname
            self.host = zt
        if tls:
            self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            id_bytes = self.dev.wr_cmd("from machine import unique_id; unique_id()",
                                       silent=True, rtn_resp=True)
            dev_id = hexlify(id_bytes).decode()
            self.key = os.path.join(_PATH[0], f'SSL_key{dev_id}.pem')
            self.cert = os.path.join(_PATH[0], f'SSL_certificate{dev_id}.pem')
            my_p = self.dev.passphrase
            if not my_p:
                while True:
                    try:
                        my_p = getpass.getpass(
                            prompt="Enter passphrase for key "
                                   f"'{self.key.split('/')[-1]}':",
                            stream=None)
                        self.context.load_cert_chain(keyfile=self.key,
                                                     certfile=self.cert,
                                                     password=my_p)
                        break
                    except ssl.SSLError:
                        # print(e)
                        print('Passphrase incorrect, try again...')
            else:
                self.context.load_cert_chain(keyfile=self.key,
                                             certfile=self.cert,
                                             password=my_p)
            self.context.verify_mode = ssl.CERT_REQUIRED
            self.context.load_verify_locations(cafile=self.cert)
        self._fw_file = firmware
        with open(firmware, 'rb') as fwr:
            self.firmware = fwr.read()
        self.sz = len(self.firmware)
        self._n_blocks = (self.sz // BLOCKLEN) + 1
        hf = hashlib.sha256(self.firmware)
        hf.update(b'\xff'*((self._n_blocks*BLOCKLEN)-self.sz))
        self.check_sha = hexlify(hf.digest()).decode()

    def find_localip(self):
        ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_soc.connect(('8.8.8.8', 1))
        local_ip = ip_soc.getsockname()[0]
        ip_soc.close()
        return local_ip

    def start_ota(self):
        while True:
            try:
                self.serv_soc.bind((self.host, self.port))
                break
            except Exception:
                self.port += 2
        self.serv_soc.listen(1)
        print('OTA Server listening...')
        if self._use_tls:
            print('OTA TLS enabled...')
        self.dev.wr_cmd('from ota import OTA')
        host = self.host
        if self.host_fwd:
            host = self.host_fwd
        self.dev.cmd_nb(f'mOTA = OTA("{host}","{self.port}", "{self.check_sha}", '
                        f'{self._use_tls})',
                        block_dev=False)
        self.conn, self.addr_client = self.serv_soc.accept()
        print('Connection received...')
        if self._use_tls:
            self.conn = self.context.wrap_socket(self.conn, server_side=True)
            print('Connection TLS enabled...')
        # print(self.addr_client)
        self.conn.settimeout(2)
        print('Starting OTA Firmware update...')
        print()
        self.dev.cmd_nb(f'mOTA.do_ota({self._n_blocks},True)', block_dev=False)
        self.do_ota()
        print('Checking Firmware...')
        self.dev.flush()
        ota_ok = False
        try:
            ota_ok = self.dev.wr_cmd('mOTA.check_ota(True)', rtn_resp=True, silent=True)

        except Exception as e:
            print(e)
        if ota_ok:
            if self.dev.wr_cmd('mOTA._OK', rtn_resp=True, silent=True):
                print('OTA Firmware Updated Succesfully!')
            else:
                print('OTA Firmware Update Failed.')
        else:
            print('OTA Firmware Update Failed.')

    def do_ota(self):
        columns, rows = os.get_terminal_size(0)
        cnt_size = 65
        if columns > cnt_size:
            size_bar = int((columns - cnt_size))
            pb = True
        else:
            size_bar = 1
            pb = False
        wheel = ['|', '/', '-', "\\"]
        sz = len(self.firmware)
        print(f"{self._fw_file}  [{sz / 1000:.2f} kB]")
        put_soc = [self.conn]
        cnt = 0
        t_start = time.time()
        with open(self._fw_file, "rb") as f:
            self.buff = f.read(BLOCKLEN)
            while True:
                try:
                    readable, writable, exceptional = select.select(put_soc,
                                                                    put_soc,
                                                                    put_soc)
                    # self.buff = f.read(1024)  # 1 KB
                    # print(len(chunk))
                    if len(writable) == 1:
                        if self.buff != b'':
                            # in python use 'i'
                            cnt += len(self.buff)
                            if len(self.buff) < BLOCKLEN:  # fill last block
                                for i in range(BLOCKLEN - len(self.buff)):
                                    self.buff += b'\xff'  # erased flash is ff
                            self.conn.sendall(self.buff)
                            loop_index_f = (cnt/sz)*size_bar
                            loop_index = int(loop_index_f)
                            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                            nb_of_total = "{:.2f}/{:.2f} kB".format(
                                cnt/(1000), sz/(1000))
                            percentage = cnt / sz
                            t_elapsed = time.time() - t_start
                            t_speed = "{:^2.2f}".format((cnt/(1000))/t_elapsed)
                            ett = sz / (cnt / t_elapsed)
                            if pb:
                                do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
                                          t_elapsed, loop_index_l, percentage, ett,
                                          size_bar)
                            else:
                                sys.stdout.write("Sent %d of %d bytes\r" % (cnt, sz))
                                sys.stdout.flush()
                            self.buff = f.read(BLOCKLEN)
                            # chunk = def_chunk
                            # final_file += chunk
                        else:
                            break

                except Exception:
                    # print(e)
                    time.sleep(0.02)
                    pass

        print('\n')
        print()
