# This example demonstrates a peripheral implementing the Nordic UART Service (NUS).

import bluetooth
from ble_advertising import advertising_payload
import time
from micropython import const

try:
    from localname import NAME as LOCALNAME
except Exception:
    LOCALNAME = None
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
_UART_TX = (bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'),
            bluetooth.FLAG_NOTIFY,)
_UART_RX = (bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'),
            bluetooth.FLAG_WRITE,)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX,),)

_DEVICE_FILEIO_SERV_UUID = bluetooth.UUID(
    "e0b9145a-d949-49e4-9dc1-54236e02206a")

# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.sdk5.v11.0.0%2Fbledfu_transport_bleservice.html&anchor=ota_spec_control_state
_FILEIO_CONTROL_AND_PACKET_CHAR = (
    bluetooth.UUID("55574ada-552e-48fa-afc0-d81ce0d6efb0"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY
)

_DEVICE_FILEIO_SERVICE = (
    _DEVICE_FILEIO_SERV_UUID,
    (_FILEIO_CONTROL_AND_PACKET_CHAR),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)


class BLEUART:
    def __init__(self, ble, name='mpy-uart', rxbuf=512, uuid=''):
        self._ble = ble
        self._ble.active(True)
        if LOCALNAME:
            _gap_name = LOCALNAME
            name = LOCALNAME
        else:
            _gap_name = 'ESP32@{}'.format(uuid)
        self._ble.config(gap_name=_gap_name, mtu=515, rxbuf=512)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle,), (self._fileio_handle,)
         ) = self._ble.gatts_register_services((_UART_SERVICE, _DEVICE_FILEIO_SERVICE))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._ble.gatts_set_buffer(self._tx_handle, rxbuf)
        self._ble.gatts_set_buffer(self._fileio_handle, rxbuf)
        self._filename = ''
        self._connections = set()
        self._rx_buffer = bytearray()
        self._tx_available = True
        self._handler = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(
            name=name, services=[_UART_UUID])
        self._advertise(interval_us=30000)

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    def any(self):
        return len(self._rx_buffer)

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    def write(self, data):
        for conn_handle in self._connections:
            while True:
                try:
                    # self._ble.gatts_notify(conn_handle, self._tx_handle, data)
                    self._ble.gatts_write(self._tx_handle, data)
                    self._ble.gatts_indicate(conn_handle, self._tx_handle)
                    self._tx_available = True
                    break
                except Exception as e:
                    # self._ble.gatts_read(self._tx_handle)
                    self._tx_available = False
                    time.sleep_ms(50)
            # self._ble.gatts_write(self._tx_handle, data)
            # self._ble.gatts_indicate(conn_handle, self._tx_handle)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def init_file(self, filename):
        self._filename = filename


def demo():
    import time

    ble = bluetooth.BLE()
    uart = BLEUART(ble)

    def on_rx():
        print('rx: ', uart.read().decode().strip())

    uart.irq(handler=on_rx)
    nums = [4, 8, 15, 16, 23, 42]
    i = 0

    try:
        while True:
            uart.write(str(nums[i]) + '\n')
            i = (i + 1) % len(nums)
            time.sleep_ms(1000)
    except KeyboardInterrupt:
        pass

    uart.close()


if __name__ == '__main__':
    demo()
