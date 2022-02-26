import json
import network
from machine import unique_id
from binascii import hexlify
import time
try:
    from hostname import NAME
except Exception:
    NAME = 'upydevice_{}'.format(hexlify(unique_id()))


def setup_network(timeout=10):
    n = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    scan = network.WLAN(network.STA_IF).scan()
    scan_tuples = [(x[0].decode(), x[3]) for x in scan]
    # Sort by dBm
    scan_tuples.sort(key=lambda x: x[1], reverse=True)
    # Set device hostname
    wlan.config(dhcp_hostname=NAME)
    with open('wpa_supplicant.config', 'r') as wpa_conf:
        wifi_config = json.load(wpa_conf)
    _APs_in_range = [x[0] for x in scan_tuples if x[0] in wifi_config.keys()]
    if _APs_in_range:
        _ssid = _APs_in_range[0]
        if not wlan.isconnected():
            print('Connecting to network...')
            wlan.connect(_ssid, wifi_config[_ssid])
            while not wlan.isconnected():
                n += 1
                time.sleep(1)
                if n > timeout:
                    return False
        print('Connected to {}'.format(_ssid))
        print('Network Config:', wlan.ifconfig())

        return True
