# @Author: carlosgilgonzalez
# @Date:   2019-03-13T22:31:44+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-14T04:37:48+01:00


from machine import I2C, Pin, Timer
# from lsm9ds1 import LSM9DS1
import time
import json
import usocket as socket
from ustruct import pack
from array import array
from micropython import const

try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


class MY_IMU:
    def __init__(self, my_imu_class, i2c, cli_soc=None):
        self.cli_soc = None
        self.i2c = i2c
        time.sleep(2)
        self.BUFFERSIZE2 = const(32)
        self.buff = bytearray(100)
        self.tim = Timer(-1)
        self.irq_busy = False
        self.imu_lib = my_imu_class
        self.lsm = None
        self.filelogname = None
        self.variables = None
        self.data_x = array("f", (0 for _ in range(self.BUFFERSIZE2)))
        self.data_y = array("f", (0 for _ in range(self.BUFFERSIZE2)))
        self.data_z = array("f", (0 for _ in range(self.BUFFERSIZE2)))
        self.index_put = 0

    def init(self):
        acc = 0
        while acc == 0:
            try:
                self.lsm = self.imu_lib(self.i2c)
                acc = 1
                time.sleep(1)
                print('imu ready!')
            except Exception as e:
                pass
            time.sleep(1)

    def read_acc(self):
        return self.lsm.read_accel()

    def read_gy(self):
        return self.lsm.read_gyro()

    def read_mag(self):
        return self.lsm.read_magnet()

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
    def sample_send_acc(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack('fff', *self.lsm.read_accel()))
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def sample_send_gy(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack('fff', *self.lsm.read_gyro()))
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def sample_send_mag(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack('fff', *self.lsm.read_magnet()))
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

# stream through socket and log to sd
    def sample_send_acc_SD(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE2:
                self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put] = self.lsm.read_accel()
                self.cli_soc.sendall(pack('fff', self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put]))
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE2:
                sample = dict(zip(self.variables, [list(self.data_x), list(self.data_y), list(self.data_z)]))
                with open(self.filelogname, 'a') as logfile:
                    logfile.write(json.dumps(sample))
                    logfile.write('\n')
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def sample_send_gy_SD(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE2:
                self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put] = self.lsm.read_gyro()
                self.cli_soc.sendall(pack(
                    'fff', self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put]))
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE2:
                sample = dict(
                    zip(self.variables, [list(self.data_x), list(self.data_y), list(self.data_z)]))
                with open(self.filelogname, 'a') as logfile:
                    logfile.write(json.dumps(sample))
                    logfile.write('\n')
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def sample_send_mag_SD(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE2:
                self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put] = self.lsm.read_magnet()
                self.cli_soc.sendall(pack('fff', self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put]))
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE2:
                sample = dict(zip(self.variables, [list(self.data_x), list(self.data_y), list(self.data_z)]))
                with open(self.filelogname, 'a') as logfile:
                    logfile.write(json.dumps(sample))
                    logfile.write('\n')
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start_send_SD(self, sampling_sensor, mode, unit, timeout=100):
        self.irq_busy = False
        fq = 1/(timeout/1000)
        header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': unit, 'fq(hz)': fq}
        self.variables = header['VAR']
        self.filelogname = self.gen_name_file(mode)
        with open(self.filelogname, 'w') as file_log:
            file_log.write(json.dumps(header))
            file_log.write('\n')

        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=sampling_sensor)
