# @Author: carlosgilgonzalez
# @Date:   2019-03-13T22:31:44+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-14T04:37:48+01:00


from machine import I2C, Pin, Timer
import time
import usocket as socket
from ustruct import pack
from array import array
from micropython import const

try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


class MY_ADS:
    def __init__(self, my_ads_class, i2c, cli_soc=None, channel=0):
        self.cli_soc = None
        self.i2c = i2c
        self.addr = 72
        self.range_dict = {0: 6.144, 1: 4.096, 2: 2.048, 3: 1.024, 4: 0.512,
                           5: 0.256}
        self.gain_dict = {0: 'x2/3', 1: 'x1', 2: 'x2', 3: 'x4', 4: 'x8',
                          5: 'x16'}
        self.gain = 1
        self.BUFFERSIZE = const(20)
        self.buff = bytearray(1)
        self.tim = Timer(-1)
        self.irq_busy = False
        self.ads_lib = my_ads_class
        self.ads = None
        self.filelogname = None
        self.variables = None
        self.data = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.index_put = 0
        self.channel = channel

    def init(self):
        ready = 0
        while ready == 0:
            try:
                self.ads = self.ads_lib(self.i2c, self.addr, self.gain)
                ready = 1
                time.sleep(1)
                self.ads.set_conv(7, channel1=self.channel)
                print('ads ready!')
                print('ADS configuration:')
                print('Channel: A{} | Voltage Range: +/- {} V | Gain: {} V/V'.format(
                    self.channel, self.range_dict[self.gain], self.gain_dict[self.gain]))
            except Exception as e:
                pass
            time.sleep(1)

    def read_V(self):
        for i in range(4):
            self.data[0] = self.ads.read_rev()
        self.data[0] = self.ads.read_rev()
        return self.ads.raw_to_v(self.data[0])

    def connect_SOC(self, host):
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, 8005)[0][-1]
        self.cli_soc.connect(soc_addr)

    def time_print(self):
        return ('{}_{}_{}_{}_{}_{}'.format(time.localtime()[1],
                                           time.localtime()[2],
                                           time.localtime()[0],
                                           time.localtime()[3],
                                           time.localtime()[4],
                                           time.localtime()[5]))

    def gen_name_file(self, mode):
        name_file = '/sd/log{}_{}.txt'.format(mode, self.time_print())
        return name_file

# stream through socket
    def sample_send_V(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack('f',
                                      self.ads.raw_to_v(self.ads.alert_read())))
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start_send(self, sampling_sensor, timeout=100):
        self.irq_busy = False
        self.ads.conversion_start(7, channel1=self.channel)
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=sampling_sensor)

    def stop_send(self):
        self.tim.deinit()
        self.cli_soc.close()
        self.irq_busy = False

    def chunk_send_V(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE:
                self.data[self.index_put] = self.ads.raw_to_v(self.ads.alert_read())
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE:
                self.cli_soc.sendall(self.data)
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False
