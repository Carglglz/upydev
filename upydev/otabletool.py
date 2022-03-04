import struct
import sys
import time
import os
from datetime import timedelta
import asyncio
from upydevice.bledevice import BASE_BLE_DEVICE
import hashlib
from binascii import hexlify

BLOCKLEN = 4096


class DFUOperationError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'DFUOperationError, {0} '.format(self.message)
        else:
            return 'DFUOperationError has been raised'


class OTABleController(BASE_BLE_DEVICE):
    def __init__(self, scan_dev, init=False, name=None, lenbuff=100,
                 packet_size=20, debug=False):
        super().__init__(scan_dev, init=init, name=name, lenbuff=lenbuff)
        self._dfu_packet_max_size = packet_size
        self._dfu_packet_format = 'B'
        self._size_format = 'I'
        self._image_size = b''
        self._application_len = b'\x00\x00\x00\x00'
        self._soft_device_len = b'\x00\x00\x00\x00'
        self._bootloader_len = b'\x00\x00\x00\x00'
        self._image_data = b''
        self._debug = debug
        self._sending_data_packets = False
        self._dfu_CP_char = 'DFU Control Point'
        self._dfu_Packet_char = 'DFU Packet'
        self._opcodes = {'START_DFU': 0x01, 'Initialize DFU Parameters': 0x02,
                         'Receive Firmware Image': 0x03,
                         'Validate Firmware': 0x04,
                         'Activate Image and Reset': 0x05,
                         'Reset System': 0x06,
                         'Report Received Image Size': 0x07,
                         'Packet Receipt Notification Request': 0x08,
                         'Response Code': 0x10,
                         'Packet Receipt Notification': 0x11}
        self._opcode_rev = {v: k for k, v in self._opcodes.items()}
        self._init_packet_codes = {'Receive Init Packet': 0x00,
                                   'Init Packet Complete': 0x01}
        self._response_values_codes = {0x01: 'Success',
                                       0x02: 'Invalid State',
                                       0x03: 'Not Supported',
                                       0x04: 'Data Size Exceeds Limit',
                                       0x05: 'CRC Error',
                                       0x06: 'Operation Failed'}
        self._dfu_image_type_codes = {'No Image': 0x00,
                                      'SoftDevice': 0x01,
                                      'Bootloader': 0x02,
                                      'SoftDevice-Bootloader': 0x03,
                                      'Application': 0x04}
        self._init_packet_format = ''
        self._init_packet = b''
        self._opcode_format = 'B'
        self._opcode_buffer = b''
        self._len_image_data_sent = 0
        self._notification_code = False
        self._bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
        self._loop_index = 0
        self._wheel = ['|', '/', '-', "\\"]
        self._len_total_packets = 0
        self._t_start = 0
        # TERMINAL SIZE
        columns, rows = os.get_terminal_size(0)
        cnt_size = 65
        if columns > cnt_size:
            self._bar_size = int((columns - cnt_size))
            self.pb = True
        else:
            self._bar_size = 1
            self.pb = False

    def do_pg_bar(self):
        loop_index_f = (self._len_image_data_sent
                        / self._len_total_packets) * self._bar_size
        loop_index = int(loop_index_f)
        loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
        nb_of_total = "{:.2f}/{:.2f} kB".format(self._len_image_data_sent / (1000**1),
                                                self._len_total_packets / (1000**1))
        percentage = self._len_image_data_sent / self._len_total_packets
        t_elapsed = time.time() - self._t_start
        t_speed = "{:^2.2f}".format((self._len_image_data_sent/(1000**1))/t_elapsed)
        ett = self._len_total_packets / (self._len_image_data_sent / t_elapsed)
        # if pb:
        #     do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
        #               t_elapsed, loop_index_l, percentage)
        l_bloc = self._bloc_progress[loop_index_l]
        if loop_index == self._bar_size:
            l_bloc = "█"
        sys.stdout.write("\033[K")
        print('▏{}▏{:>2}{:>5} % | {} | {:>5} kB/s | {}/{} s'.format("█" * loop_index + l_bloc + " "*((self._bar_size+1) - len("█" * loop_index + l_bloc)),
                                                                    self._wheel[loop_index % 4],
                                                                    int((percentage)*100),
                                                                    nb_of_total, t_speed,
                                                                    str(timedelta(seconds=t_elapsed)).split(
                                                                        '.')[0][2:],
                                                                    str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
        sys.stdout.flush()

    def load_image(self, img, len_application=0, len_softdevice=0, len_bootloader=0):
        with open(img, 'rb') as imagefile:
            self._image_raw_data = imagefile.read()
            n_soflen = struct.unpack(
                'HHIH', self._image_raw_data[:struct.calcsize('HHIH')])[-1]
            self._init_packet_len = struct.calcsize(
                'HHIH') + n_soflen * struct.calcsize('H') + struct.calcsize('H')
            self._image_data = self._image_raw_data[self._init_packet_len:]
            self._init_packet = self._image_raw_data[:self._init_packet_len]
            self._application_len = len(self._image_data)

    def get_image_size(self):
        self._image_size = self._soft_device_len + self._bootloader_len + \
            struct.pack(self._size_format, self._application_len)

    def get_dfu_image_type(self):
        len_sf, = struct.unpack('I', self._soft_device_len)
        len_bl, = struct.unpack('I', self._bootloader_len)
        len_app = self._application_len
        if len_sf > 0:
            return self._dfu_image_type_codes['Softdevice']
        elif len_bl > 0:
            return self._dfu_image_type_codes['Bootloader']
        elif len_app > 0:
            return self._dfu_image_type_codes['Application']

    def get_init_packet(self, initpacketlist):
        """
        uint16_t 	device_type
        uint16_t 	device_rev
        uint32_t 	app_version
        uint16_t 	softdevice_len
        uint16_t 	softdevice [1] (array)
        uint16_t    Checksum: CRC-16-CCITT for the image to transfer
        """
        self._init_packet_format = 'HHIH' + len(initpacketlist[4:]) * 'H' + 'H'
        self._init_packet = struct.pack(self._init_packet_format, *initpacketlist)

    def get_opcode_response_callback(self, sender, data):
        if not self._sending_data_packets:
            self._opcode_buffer += data
        else:
            self._notification_code, index = struct.unpack('BB', data)
            # if index < 100:
            #     print('[{:80}] {} %\r'.format(int((index/100)*80)*'#',
            #                                   index), end='')
            # else:
            #     print('[{:80}] {} %\r'.format(int((index/100)*80)*'#',
            #                                   index))
            self.do_pg_bar()

    async def as_write_read_opcode_waitp(self, opcode, response_len, action=None):
        await self.ble_client.start_notify(self.notifiables[self._dfu_CP_char],
                                           self.get_opcode_response_callback)
        await self.ble_client.write_gatt_char(self.writeables[self._dfu_CP_char],
                                              opcode)
        if action == 'START_DFU':
            await self.ble_client.write_gatt_char(self.writeables[self._dfu_Packet_char],
                                                  self._image_size)

        while len(self._opcode_buffer) < struct.calcsize('B'*response_len):
            await asyncio.sleep(0.01, loop=self.loop)
        await self.ble_client.stop_notify(self.notifiables[self._dfu_CP_char])
        if response_len == 3:
            resp_opcode, req_opcode, resp_value = struct.unpack(
                'BBB', self._opcode_buffer)
            if self._debug:
                print('Resp OPCODE: {}, Request OPCODE: {}, Resp Value: {}'.format(
                    *self._opcode_buffer))

                print('Resp OPCODE: {}, Request OPCODE: {}, Resp Value: {}'.format(self._opcode_rev[resp_opcode],
                                                                                   self._opcode_rev[req_opcode],
                                                                                   self._response_values_codes[resp_value]))
            if resp_value in [0x02, 0x03, 0x04, 0x05, 0x06]:
                raise DFUOperationError(self._response_values_codes[resp_value])
        return self._opcode_buffer

    def write_read_opcode(self, opcode, response_len, action=None):
        self._opcode_buffer = b''
        try:
            response = self.loop.run_until_complete(
                self.as_write_read_opcode_waitp(opcode, response_len, action))
            return response
        except Exception as e:
            print(e)

    # NO CONFIRMATION
    async def as_write_data_packages(self, data, response_len=3, callback=None):
        self._sending_data_packets = True
        self._len_total_packets = len(data)
        self._t_start = time.time()
        await self.ble_client.start_notify(self.notifiables[self._dfu_CP_char],
                                           self.get_opcode_response_callback)
        # if len(data) > self._dfu_packet_max_size:
        for i in range(0, len(data), self._dfu_packet_max_size):
            await self.ble_client.write_gatt_char(self.writeables[self._dfu_Packet_char],
                                                  data[i:i+self._dfu_packet_max_size])
            if callback:
                callback.emit(i)
            self._len_image_data_sent += len(data[i:i+self._dfu_packet_max_size])
            if self._len_image_data_sent < len(data):
                if self._len_image_data_sent % self._dfu_packet_max_size == 0:
                    while not self._notification_code:
                        await asyncio.sleep(0.01, loop=self.loop)
                    self._notification_code = False
                else:
                    # print('[{:80}] {} %\r'.format(int((self._len_image_data_sent/len(data))*80)*'#',
                    #                                   int((self._len_image_data_sent/len(data))*100)), end='')
                    self.do_pg_bar()
            else:
                while not self._notification_code:
                    await asyncio.sleep(0.01, loop=self.loop)
                self._notification_code = False
                self._sending_data_packets = False
                print('')
                # if self._len_image_data_sent < len(data):
                #     print('[{:80}] {} %\r'.format(int((self._len_image_data_sent/len(data))*80)*'#',
                #                                   int((self._len_image_data_sent/len(data))*100)), end='')
                #
                # if self._len_image_data_sent == len(data):
                #     print('[{:80}] {} %\r'.format(int((self._len_image_data_sent/len(data))*80)*'#',
                #                                   int((self._len_image_data_sent/len(data))*100)))

        while len(self._opcode_buffer) < struct.calcsize('B'*response_len):
            await asyncio.sleep(0.01, loop=self.loop)
        await self.ble_client.stop_notify(self.notifiables[self._dfu_CP_char])
        if response_len == 3:
            resp_opcode, req_opcode, resp_value = struct.unpack(
                'BBB', self._opcode_buffer)
            if self._debug:
                print('Resp OPCODE: {}, Request OPCODE: {}, Resp Value: {}'.format(
                    *self._opcode_buffer))
                print('Resp OPCODE: {}, Request OPCODE: {}, Resp Value: {}'.format(self._opcode_rev[resp_opcode],
                                                                                   self._opcode_rev[req_opcode],
                                                                                   self._response_values_codes[resp_value]))
            if resp_value in [0x02, 0x03, 0x04, 0x05, 0x06]:
                raise DFUOperationError(self._response_values_codes[resp_value])
        return self._opcode_buffer

    def write_data_packages(self, data):
        try:
            self.loop.run_until_complete(
                self.as_write_data_packages(data))
        except Exception as e:
            print(e)

    def write_image_size(self):
        """
        Image size:
        After writing "Start DFU" (0x01) to the DFU Control Point,
        you must write the image size to the DFU Packet characteristic.
        The image size must be written in the following format:
         <Length of SoftDevice><Length of bootloader><Length of application>
         All lengths must be uint32.
         If a length is not present the length should be given as 0
        """
        byte_opcode = struct.pack('B', self._opcodes['START_DFU'])
        byte_dfu_image_type = struct.pack('B', self.get_dfu_image_type())
        self.get_image_size()
        response_opcode = self.write_read_opcode(byte_opcode + byte_dfu_image_type, 3,
                                                 action='START_DFU')

    def write_init_packet(self):
        """
        After writing "Initialize DFU Parameters" (0x02) to the DFU Control Point,
        you must write an init packet to the DFU Packet characteristic.
        """
        byte_opcode = struct.pack('B', self._opcodes['Initialize DFU Parameters'])
        init_packet_code = struct.pack(
            'B', self._init_packet_codes['Receive Init Packet'])
        response_opcode_init = self.write_read_opcode(byte_opcode+init_packet_code, 0)
        # self.get_init_packet([0, 0, 0, 0, 0])
        self.write_char(self._dfu_Packet_char, data=self._init_packet)
        init_complete_packet_code = struct.pack(
            'B', self._init_packet_codes['Init Packet Complete'])
        response_opcode_init_complete = self.write_read_opcode(
            byte_opcode+init_complete_packet_code, 3)

    def write_image_data(self):
        """
        After writing "Receive Firmware Image" (0x03) to the DFU Control Point,
        you must write packets containing image data to the DFU Packet characteristic.
        The firmware image can be split up in multiple DFU packets.
        The full image is transferred by writing each fragment as DFU packet
        to the DFU Packet characteristic.
        """
        byte_opcode = struct.pack('B', self._opcodes['Receive Firmware Image'])
        response_opcode_init = self.write_read_opcode(byte_opcode, 0)
        response_data_packages = self.write_data_packages(self._image_data)

    def validate_image_data(self):
        """Validate the received firmware."""
        byte_opcode = struct.pack('B', self._opcodes['Validate Firmware'])
        response_opcode_validate = self.write_read_opcode(byte_opcode, 3)
        return response_opcode_validate

    def activate_image_and_reset(self):
        """
        Activate the previously received image and perform a system reset.
        There is no response to this Op Code.
        """
        byte_opcode = struct.pack('B', self._opcodes['Activate Image and Reset'])
        response_opcode_activate_reset = self.write_read_opcode(byte_opcode, 0)

    def do_dfu(self, file):
        try:
            self.load_image(file)
            self.write_image_size()
            self.write_init_packet()
            print('Starting OTA update ...')
            self.write_image_data()
            print('Validating firmware...')
            validated = self.validate_image_data()
            if validated:
                print(f'Firmware OTA uploaded successfully')
            else:
                print('OTA Failed')
            self.activate_image_and_reset()
            print('Rebooting device now')
            time.sleep(1)
            if self.is_connected():
                self.disconnect()
                print('DFU operation finished.')
            else:
                print('DFU operation finished.')
        except DFUOperationError as e:
            print(e)
            time.sleep(1)
            print('Trying again...')
            self.do_dfu(file)
        except Exception as e:
            print(e)
            self.disconnect()


# CHECKSUM CRC16: Gennady Trafimenkov, 2011 https://github.com/gtrafimenkov/pycrc16
CRC16_XMODEM_TABLE = [
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
        0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
        0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
        0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
        0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
        0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
        0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
        0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
        0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
        0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
        0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
        0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
        0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
        0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
        0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
        0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
        0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
        0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
        ]


def _crc16(data, crc, table):
    """Calculate CRC16 using the given table.
    `data`      - data for calculating CRC, must be bytes
    `crc`       - initial value
    `table`     - table for caclulating CRC (list of 256 integers)
    Return calculated value of CRC
    """
    for byte in data:
        crc = ((crc << 8) & 0xff00) ^ table[((crc >> 8) & 0xff) ^ byte]
    return crc & 0xffff


def crc16xmodem(data, crc=0):
    """Calculate CRC-CCITT (XModem) variant of CRC16.
    `data`      - data for calculating CRC, must be bytes
    `crc`       - initial value
    Return calculated value of CRC
    """
    return _crc16(data, crc, CRC16_XMODEM_TABLE)


def get_init_packet(initpacketlist):
    """
    uint16_t 	device_type
    uint16_t 	device_rev
    uint32_t 	app_version
    uint16_t 	softdevice_len
    uint16_t 	softdevice [1] (array)
    uint16_t    Checksum: CRC-16-CCITT for the image to transfer
    """
    init_packet_format = 'HHIH' + initpacketlist[3] * 'H' + 'H'
    init_packet = struct.pack(init_packet_format, *initpacketlist)
    return init_packet


def dfufy_file(file):
    # Do checksum of sha256
    try:
        with open(file, 'rb') as filetofreeze:
            data = filetofreeze.read()
            sz = len(data)
            n_blocks = (sz // BLOCKLEN) + 1
            hf = hashlib.sha256(data)
            hf.update(b'\xff'*((n_blocks*BLOCKLEN)-sz))
            # sha256 and then checksum
            hashdata = hexlify(hf.digest())
            checksum = crc16xmodem(hashdata)
            data += b'\xff'*((n_blocks*BLOCKLEN)-sz)
            print(f'Checking {file} firmware...')
            print(f'Firmware size: {len(data)}')
            print(f'Firmware SHA-256: {hashdata.decode()}')
            print(f'CRC CHECKSUM: {checksum}')
        init_packet = get_init_packet([1, 1, 1, 1, 1, checksum])
        with open(file.split('.')[0] + 'ble-ota.bin', 'wb') as filetobin:
            # namefile_data = file.encode('utf8') + b'\n' + data
            image_data = init_packet + data
            filetobin.write(image_data)
        # print('File {} ready!'.format(file.split('.')[0] + 'ble-ota.bin'))
        return file.split('.')[0] + 'ble-ota.bin'
    except Exception as e:
        print(e)
