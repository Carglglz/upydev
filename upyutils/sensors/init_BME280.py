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


class MY_BME280:
    def __init__(self, my_bme_class, i2c, cli_soc=None):
        self.cli_soc = None
        self.i2c = i2c
        self.addr = 119
        self.BUFFERSIZE = const(20)
        self.buff = bytearray(1)
        self.tim = Timer(-1)
        self.irq_busy = False
        self.bme_lib = my_bme_class
        self.bme = None
        self.filelogname = None
        self.variables = None
        self.data = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.index_put = 0

    def init(self):
        ready = 0
        while ready == 0:
            try:
                self.bme = self.bme_lib(i2c=self.i2c)
                ready = 1
                time.sleep(1)
                print('BME280 ready!')
            except Exception as e:
                pass
            time.sleep(1)

    def read_values(self):
        return [val for val in self.bme.read_compensated_data()]

    def connect_SOC(self, host):
        self.irq_busy = True
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, 8005)[0][-1]
        self.cli_soc.connect(soc_addr)
        self.irq_busy = False

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
    def sample_send_data(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(self.bme.read_compensated_data())
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start_send(self, sampling_sensor, timeout=100):
        self.irq_busy = False
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=sampling_sensor)

    def stop_send(self):
        self.tim.deinit()
        self.cli_soc.close()
        self.irq_busy = False

    # def chunk_send_V(self, x):
    #     if self.irq_busy:
    #         return
    #     try:
    #         self.irq_busy = True
    #         if self.index_put < self.BUFFERSIZE:
    #             self.data[self.index_put] = self.ads.raw_to_v(self.ads.alert_read())
    #             self.index_put += 1
    #         elif self.index_put == self.BUFFERSIZE:
    #             self.cli_soc.sendall(self.data)
    #             self.index_put = 0
    #         self.irq_busy = False
    #     except Exception as e:
    #         self.irq_busy = False
