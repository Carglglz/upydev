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
import json
try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


class MY_INA219:
    def __init__(self, my_ina_class, i2c, cli_soc=None, addr=0x44):
        self.cli_soc = None
        self.i2c = i2c
        self.addr = addr
        self.BUFFERSIZE = const(3)
        self.buff = bytearray(1)
        self.tim = Timer(-1)
        self.irq_busy = False
        self.ina_lib = my_ina_class
        self.ina = None
        self.filelogname = None
        self.variables = None
        self.data = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.data_V = array("f", (0 for _ in range(100)))
        self.data_C = array("f", (0 for _ in range(100)))
        self.data_P = array("f", (0 for _ in range(100)))
        self.index_put = 0
        self.SHUNT_OHMS = 0.1

    def init(self):
        ready = 0
        while ready == 0:
            try:
                self.ina = self.ina_lib(self.SHUNT_OHMS, self.i2c, address=self.addr)
                ready = 1
                time.sleep(1)
                self.ina.configure()
                print('INA219 ready!')
            except Exception as e:
                pass
            time.sleep(1)

    def read_values(self):
        return [self.ina.voltage(), self.ina.current(), self.ina.power()]

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
    def sample_send_data(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.data[0], self.data[1], self.data[2] = [self.ina.voltage(), self.ina.current(), self.ina.power()]
            self.cli_soc.sendall(self.data)
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

    def batt_ts(self):
        for i in range(100):
            self.data_V[i], self.data_C[i], self.data_P[i] = [self.ina.voltage(), self.ina.current(), self.ina.power()]
            time.sleep_ms(50)
        self.data[0] = sum(self.data_V)/100
        self.data[1] = sum(self.data_C)/100
        self.data[2] = sum(self.data_P)/100
        return(self.data[0], self.data[1], self.data[2])

    def batt_ts_raw(self):
        for i in range(100):
            self.data_V[i], self.data_C[i], self.data_P[i] = [self.ina.voltage(), self.ina.current(), self.ina.power()]
            time.sleep_ms(50)

        return(json.dumps({"V": list(self.data_V), "C": list(self.data_C), "P": list(self.data_P)}))
