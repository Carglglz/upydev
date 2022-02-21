# BLE DFU Profile
# The Device Firmware Update (DFU) Profile is an example for a proprietary
# profile that can be used to update firmware files using Bluetooth low energy.
# This profile is not a standard profile. It is defined by Nordic Semiconductor
# to demonstrate how a typical Device Firmware Update can be achieved.
# The DFU Profile is used to transfer application, SoftDevice, or bootloader
# images from a BLE central (for example, a computer or a smartphone)
# to a peripheral (for example, a Heart Rate Sensor)
# that supports Device Firmware Updates using the DFU Service.
# https://infocenter.nordicsemi.com/topic/com.nordic.infocenter.sdk5.v11.0.0/bledfu_transport_bleprofile.html

# This is CUSTOM IMPLEMENTATION JUST FOR esp32 application.bin (e.g micropython.bin) files
# This does not support Softdevice or Bootloader
# Expected Image structure: b'[INIT PACKET][FILE]'

import bluetooth
import struct
import time
from ble_advertising import advertising_payload
from machine import Timer, reset
from micropython import const
import os
import sys
from esp32 import Partition
import hashlib
from binascii import hexlify
try:
    from localname import NAME as LOCALNAME
except Exception:
    LOCALNAME = None


BLOCKLEN = const(4096)  # data bytes in a flash block

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.sdk5.v11.0.0%2Fbledfu_transport_bleservice.html
_DEVICE_FIRMWARE_UPDATE_SERV_UUID = bluetooth.UUID(
    "00001530-1212-efde-1523-785feabcd123")

# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.sdk5.v11.0.0%2Fbledfu_transport_bleservice.html&anchor=ota_spec_control_state
_DFU_CONTROL_POINT_CHAR = (
    bluetooth.UUID("00001531-1212-efde-1523-785feabcd123"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY
)

_DFU_PACKET_CHAR = (
    bluetooth.UUID("00001532-1212-efde-1523-785feabcd123"),
    bluetooth.FLAG_WRITE
)

_DEVICE_FIRMWARE_UPDATE_SERVICE = (
    _DEVICE_FIRMWARE_UPDATE_SERV_UUID,
    (_DFU_CONTROL_POINT_CHAR, _DFU_PACKET_CHAR),
)

# org.bluetooth.service.device_information
_DEV_INF_SERV_UUID = bluetooth.UUID(0x180A)
# org.bluetooth.characteristic.appearance
_APPEAR_CHAR = (
    bluetooth.UUID(0x2A01),
    bluetooth.FLAG_READ
)
# org.bluetooth.characteristic.manufacturer_name_string
_MANUFACT_CHAR = (
    bluetooth.UUID(0x2A29),
    bluetooth.FLAG_READ
)

# org.bluetooth.characteristic.gap.appearance
_ADV_APPEARANCE_GENERIC_KEYRING = const(576)


systeminfo = os.uname()
_MODEL_NUMBER = systeminfo.sysname
_FIRMWARE_REV = "{}-{}".format(sys.implementation[0], systeminfo.release)

_MODEL_NUMBER_CHAR = (
        bluetooth.UUID(0x2A24),
        bluetooth.FLAG_READ)

_FIRMWARE_REV_CHAR = (
        bluetooth.UUID(0x2A26),
        bluetooth.FLAG_READ)

_DEV_INF_SERV_SERVICE = (
    _DEV_INF_SERV_UUID,
    (_APPEAR_CHAR, _MANUFACT_CHAR,
     _MODEL_NUMBER_CHAR, _FIRMWARE_REV_CHAR),
)

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


def set_ble_flag(flag):
    with open('ble_flag.py', 'wb') as bleconfig:
        bleconfig.write(b'BLE = {}'.format(flag))


class BLE_DFU_TARGET:
    def __init__(self, name="esp32-DFU", led=None, gap_name="ESP32-DFU"):
        self.part = Partition(Partition.RUNNING).get_next_update()
        self.sha = hashlib.sha256()
        self.block = 0
        self.buf = bytearray(BLOCKLEN)
        self.buflen = 0
        self._total_blocks = 0
        self.timer = Timer(1)
        self.led = led
        self.irq_busy = False
        self._is_connected = False
        self._image_size = 0
        self._image_type = 0
        self._opcode = 0
        self._resp_opcode = 0x10
        self._opcodes_dict = {'START_DFU': 0x01,
                              'Initialize DFU Parameters': 0x02,
                              'Receive Firmware Image': 0x03,
                              'Validate Firmware': 0x04,
                              'Activate Image and Reset': 0x05,
                              'Reset System': 0x06,
                              'Report Received Image Size': 0x07,
                              'Packet Receipt Notification Request': 0x08,
                              'Response Code': 0x10,
                              'Packet Receipt Notification': 0x11}
        self._opcode_rev = {v: k for k, v in self._opcodes_dict.items()}
        self._response_values = {'Success': 0x01,
                                 'Invalid State': 0x02,
                                 'Not Supported': 0x03,
                                 'Data Size Exceeds Limit': 0x04,
                                 'CRC Error': 0x05,
                                 'Operation Failed': 0x06}
        self._dfu_image_type_codes = {0x00: 'No Image',
                                      0x01: 'SoftDevice',
                                      0x02: 'Bootloader',
                                      0x03: 'SoftDevice-Bootloader',
                                      0x04: 'Application'}
        self._init_packet_codes = {0x00: 'Receive Init Packet',
                                   0x01: 'Init Packet Complete'}
        self._init_packet = 0
        self._name_file_packet = False
        self._filename = b''
        self._total_image_size = 0
        self._received_image_len = 0
        self._n_packet = 0
        self._image_checksum = 0
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        if LOCALNAME:
            name = f"{LOCALNAME}-DFU"
            gap_name = f"{LOCALNAME.upper()}-DFU"
        self._ble.config(gap_name=gap_name, mtu=515, rxbuf=512)
        self._ble.irq(self._irq)
        ((self._appear, self._manufact, self._model, self._firm),
            (self._dfu_control_point, self._dfu_packet)) = self._ble.gatts_register_services(
            (_DEV_INF_SERV_SERVICE, _DEVICE_FIRMWARE_UPDATE_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _DEV_INF_SERV_UUID], appearance=_ADV_APPEARANCE_GENERIC_KEYRING
        )
        print(len(self._payload))
        # 60 seconds (fast connection) Advertising Interval 20 ms to 30 ms
        print('Advertising in fast connection mode for 60 seconds...')
        self._advertise(interval_us=30000)
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_GENERIC_KEYRING))
        self._ble.gatts_write(self._manufact, bytes('Espressif Incorporated',
                                                    'utf8'))
        self._ble.gatts_write(self._model, bytes(_MODEL_NUMBER, 'utf8'))
        self._ble.gatts_write(self._firm, bytes(_FIRMWARE_REV, 'utf8'))
        self._ble.gatts_set_buffer(self._dfu_packet, 512, True)
        self.stop_timeout()
        # Timeout 60 s
        self.start_adv_timeout()
        # After 60 seconds resets

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            self.is_connected = True
            self.stop_timeout()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            # self.stop_timeout()
            self.is_connected = False
            self._connections.remove(conn_handle)
            if self._opcode == self._opcodes_dict['Activate Image and Reset']:
                pass
            else:
                if self.led:
                    for k in range(4):
                        self.led.value(not self.led.value())
                        time.sleep(0.2)
                # Start advertising again to allow a new connection.
                print('Advertising mode for 60 seconds...')
                self._advertise(interval_us=30000)
                self.start_adv_timeout(timeout=60000)
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle, = data
            # DFU CONTROL POINT
            if conn_handle in self._connections and value_handle == self._dfu_control_point:
                opcode = self._ble.gatts_read(self._dfu_control_point)[0]
                print('OPCODE: {}'.format(opcode))
                if opcode == self._opcodes_dict['START_DFU']:
                    self._received_image_len = 0
                    self._opcode, self._image_type = struct.unpack(
                        'BB', self._ble.gatts_read(self._dfu_control_point))
                    print('START_DFU (0x01) OPCODE RECEIVED')
                    print('IMAGE TYPE: {}'.format(
                        self._dfu_image_type_codes[self._image_type]))
                elif opcode == self._opcodes_dict['Initialize DFU Parameters']:
                    self._opcode, init_code = struct.unpack(
                        'BB', self._ble.gatts_read(self._dfu_control_point))
                    print('Initialize DFU Parameters (0x02) OPCODE RECEIVED')
                    print('{}'.format(self._init_packet_codes[init_code]))
                    # DFU Control Point – OpCode = 16 ReqOpCode = 2 RespValue = 1
                    if init_code == 0x01:  # Init Packet Complete
                        self._ble.gatts_write(self._dfu_control_point,
                                              struct.pack('BBB',
                                                          self._resp_opcode,
                                                          self._opcode,
                                                          self._response_values['Success']))
                        for conn_handle in self._connections:
                            self._ble.gatts_notify(conn_handle,
                                                   self._dfu_control_point)
                elif opcode == self._opcodes_dict['Receive Firmware Image']:
                    self._opcode, = struct.unpack(
                        'B', self._ble.gatts_read(self._dfu_control_point))
                    print('Receive Firmware Image (0x03) OPCODE RECEIVED')

                elif opcode == self._opcodes_dict['Validate Firmware']:
                    self._opcode, = struct.unpack(
                        'B', self._ble.gatts_read(self._dfu_control_point))
                    print('Validate Firmware (0x04) OPCODE RECEIVED')

                    hashdata = hexlify(self.sha.digest())
                    # hashdatab = hexlify(self.shab.digest())
                    checksum = crc16xmodem(hashdata)
                    print(f'Firmware size: {self._received_image_len}')
                    # print(f'BLOCKS: {self.block}')
                    print(f'Firmware SHA-256: {hashdata.decode()}')
                    # print(f'Firmware SHA-256 B: {hashdatab.decode()}')
                    print(f'CRC CHECKSUM: {checksum}')
                    print('indicated Checksum: {} | Received Checksum: {}'.format(
                        self._image_checksum, checksum))
                    if self._image_checksum == checksum:
                        resp_val = self._response_values['Success']
                        try:
                            self.part.set_boot()
                        except OSError as e:
                            print(e)
                            resp_val = self._response_values['Operation Failed']
                        self._ble.gatts_write(self._dfu_control_point,
                                              struct.pack('BBB',
                                                          self._resp_opcode,
                                                          self._opcode,
                                                          resp_val))
                        for conn_handle in self._connections:
                            self._ble.gatts_notify(conn_handle,
                                                   self._dfu_control_point)
                    else:
                        self._ble.gatts_write(self._dfu_control_point,
                                              struct.pack('BBB',
                                                          self._resp_opcode,
                                                          self._opcode,
                                                          self._response_values['CRC Error']))
                        for conn_handle in self._connections:
                            self._ble.gatts_notify(conn_handle,
                                                   self._dfu_control_point)
                elif opcode == self._opcodes_dict['Activate Image and Reset']:
                    self._opcode, = struct.unpack(
                        'B', self._ble.gatts_read(self._dfu_control_point))
                    print('Activate Image and Reset (0x05) OPCODE RECEIVED')
                    print('Activating Application Mode')
                    set_ble_flag(True)
                    print('Rebooting in 3s...')
                    self.start_adv_timeout(3000)

            # DFU PACKET
            elif conn_handle in self._connections and value_handle == self._dfu_packet:
                if self._opcode == self._opcodes_dict['START_DFU']:
                    len_sofd, len_bootl, len_app = struct.unpack(
                        'III', self._ble.gatts_read(self._dfu_packet))
                    print('IMAGE SIZE (bytes): SOFTDEVICE: {}, BOOTLOADER: {}, APPLICATION: {}'.format(
                        len_sofd, len_bootl, len_app))
                    self._total_image_size = len_sofd + len_bootl + len_app
                    # DFU Control Point – OpCode = 16 ReqOpCode = 1 RespValue = 1
                    self._total_blocks = (self._total_image_size // BLOCKLEN) + 1
                    self._ble.gatts_write(self._dfu_control_point,
                                          struct.pack('BBB',
                                                      self._resp_opcode,
                                                      self._opcode,
                                                      self._response_values['Success']))
                    for conn_handle in self._connections:
                        self._ble.gatts_notify(conn_handle,
                                               self._dfu_control_point)
                elif self._opcode == self._opcodes_dict['Initialize DFU Parameters']:
                    init_packet = self._ble.gatts_read(self._dfu_packet)
                    n_soflen = struct.unpack(
                        'HHIH', init_packet[:struct.calcsize('HHIH')])[-1]
                    init_packet_format = 'HHIH' + n_soflen * 'H' + 'H'
                    self._init_packet = struct.unpack(init_packet_format, init_packet)
                    self._image_checksum = self._init_packet[-1]
                    print('INIT PACKET RECEIVED:')
                    print(
                        'Device type | Device Rev | App Version | Softdevice len | Softdevice | Checksum (CRC-16-CCITT)')
                    print('{} | {} | {} | {} | {} | {}'.format(
                        *self._init_packet))  # FIXME: ++softdevices
                    self.buf = b''
                elif self._opcode == self._opcodes_dict['Receive Firmware Image']:
                    data_packet = self._ble.gatts_read(self._dfu_packet)
                    self._n_packet += 1
                    self._received_image_len += len(data_packet)
                    # TODO: Check image type and softdevice / bootloader /application sizes
                    if self._name_file_packet:
                        if b'\n' in data_packet:
                            self._filename = data_packet.split(b'\n')[0]
                            data = data_packet[len(self._filename)+1:]
                            with open(self._filename, 'wb') as fwfile:
                                fwfile.write(data)
                            self._name_file_packet = False
                    else:
                        # FILL BLOCK, then write to partition
                        self.buf += data_packet
                        self.sha.update(data_packet)
                        self.buflen = len(self.buf)
                        if self.buflen >= BLOCKLEN:
                            rest = self.buf[BLOCKLEN:]
                            wb = self.buf[:BLOCKLEN]
                            assert len(wb) == BLOCKLEN, "BLOCK LEN ERROR"
                            # self.shab.update(wb)
                            self.part.writeblocks(self.block, wb)
                            self.buf = rest
                            self.block += 1

                    if self._received_image_len < self._total_image_size:
                        print('[{:80}] {} %\r'.format(int((self._received_image_len/self._total_image_size)*80)*'#',
                                                      int((self._received_image_len/self._total_image_size)*100)), end='')
                        if self._received_image_len % 512 == 0:
                            self._ble.gatts_write(self._dfu_control_point,
                                                  struct.pack('BB',
                                                              self._opcodes_dict['Packet Receipt Notification'],
                                                              int((self._received_image_len/self._total_image_size)*100)))
                            for conn_handle in self._connections:
                                self._ble.gatts_notify(conn_handle,
                                                       self._dfu_control_point)

                    if self._received_image_len == self._total_image_size:
                        print('[{:80}] {} %\r'.format(int((self._received_image_len/self._total_image_size)*80)*'#',
                                                      int((self._received_image_len/self._total_image_size)*100)))

                        self._ble.gatts_write(self._dfu_control_point,
                                              struct.pack('BB',
                                                          self._opcodes_dict['Packet Receipt Notification'],
                                                          int((self._received_image_len/self._total_image_size)*100)))
                        for conn_handle in self._connections:
                            self._ble.gatts_notify(conn_handle,
                                                   self._dfu_control_point)
                        # :DFU Control Point – OpCode = 16 ReqOpCode = 3 RespValue = 1
                        time.sleep(0.2)
                        self._ble.gatts_write(self._dfu_control_point,
                                              struct.pack('BBB',
                                                          self._resp_opcode,
                                                          self._opcode,
                                                          self._response_values['Success']))
                        for conn_handle in self._connections:
                            self._ble.gatts_notify(conn_handle,
                                                   self._dfu_control_point)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def check_if_connected(self, x):
        if self.irq_busy:
            return
        else:
            if self._is_connected:
                return
            else:
                set_ble_flag(True)
                print('No connections received after 60 s, rebooting now into Application Mode...')
                if self.led:
                    for k in range(10):
                        self.led.value(not self.led.value())
                        time.sleep(0.2)
                self.stop_timeout()
                reset()

    def start_adv_timeout(self, timeout=30000):
        self.irq_busy = False
        self.timer.init(period=timeout, mode=Timer.ONE_SHOT,
                        callback=self.check_if_connected)

    def stop_timeout(self):
        self.timer.deinit()
        self.irq_busy = False
