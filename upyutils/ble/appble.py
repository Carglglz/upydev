import bluetooth
#from ble_temp_amb import BLE_Battery_Temp
import ble_uart_repl


ble = bluetooth.BLE()


def main(**kargs):
    # ble_temp_batt = BLE_Battery_Temp(ble, **kargs)
    # return ble_temp_batt
    ble_uart_repl.start()


DFU = 'DFU'


def set_ble_flag(flag):
    with open('ble_flag.py', 'wb') as bleconfig:
        if isinstance(flag, str):
            bleconfig.write(b'BLE = "{}"'.format(flag))
        else:
            bleconfig.write(b'BLE = {}'.format(flag))
