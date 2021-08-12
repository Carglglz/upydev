import json
import network
import webrepl
from machine import Pin
import machine
import time


class WIFI_UTIL:
    def __init__(self, AP_FLAG=27, SIGNAL=33, LED=13, silent=True):
        self.AP_flag = Pin(AP_FLAG, Pin.IN)
        time.sleep(2)
        self.button = None
        self.butpin = AP_FLAG
        self.ap = network.WLAN(network.AP_IF)
        # LED
        self.led = Pin(LED, Pin.OUT)
        # SIGNAL
        self.sig = Pin(33, Pin.OUT)
        self.sig.value(0)
        # AP interrupt config
        self.irq_busy = False
        # STA CONFIG FILE
        self.STA_FILE = 'wifi_.config'
        # AP CONFIG FILE
        self.AP_FILE = 'ap_.config'
        self.silent = silent
        if not self.silent:
            print('WLAN UTIL INITIATED')

    def toggle_AP_usb(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.AP_flag.value() == 0:  # reverse op == 0
                for i in range(4):
                    self.led.value(not self.led.value())
                    time.sleep_ms(250)
                if self.ap.active() is False:
                    for i in range(4):
                        self.led.value(not self.led.value())
                        time.sleep_ms(250)
                    self.AP_flag.init(Pin.OUT)
                    time.sleep_ms(1000)
                    self.AP_flag.value(0)  # reverse op == 1
                    self.AP_flag.init(Pin.IN, Pin.PULL_UP)
                    print('Enabling AP...')
                    machine.reset()
                else:
                    self.ap.active(False)
                    self.AP_flag.init(Pin.OUT)
                    time.sleep_ms(1000)
                    self.AP_flag.value(0)  # reverse op == 1
                    self.AP_flag.init(Pin.IN, Pin.PULL_DOWN)
                    print(self.AP_flag.value())
                    print('Disabling AP...')
                    time.sleep(1)
                    machine.reset()
            self.irq_busy = False

    def ap_enable_int(self):
        # AP Interrupt config
        self.button = Pin(self.butpin, Pin.OUT)
        self.button.init(Pin.IN, Pin.PULL_UP)
        print(self.button.value())
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.toggle_AP_usb)

    def STA_conn(self):
        # LOAD WIFI_.CONFIG
        with open(self.STA_FILE, 'r') as wifi_file:
            wifi_config = json.load(wifi_file)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(wifi_config['ssid'], wifi_config['password'])
            while not wlan.isconnected():
                pass
        print('Connected to {}'.format(wifi_config['ssid']))
        print('Network Config:', wlan.ifconfig())

        webrepl.start()
        for i in range(10):
            self.led.value(not self.led.value())
            time.sleep(0.2)
        self.led.value(False)

    def AP_conn(self):
        with open(self.AP_FILE, 'r') as ap_file:
            ap_config = json.load(ap_file)  # be aware load upy, loads py
        self.ap.active(True)
        self.ap.config(essid=ap_config['ssid'],
                       authmode=network.AUTH_WPA_WPA2_PSK,
                       password=ap_config['password'])
        print('access point configured: {}'.format(ap_config['ssid']))
        print(self.ap.ifconfig())
        webrepl.start()
        for i in range(10):
            self.led.value(not self.led.value())
            time.sleep(0.2)
        self.led.value(False)

    def ap_config(self, ssid, passw):
        ap_conf = dict(ssid=ssid, password=passw)
        with open(self.AP_FILE, 'w') as ap_file:
            ap_file.write(json.dumps(ap_conf))
        if not self.silent:
            print('AP: {} configured'.format(ssid))

    def sta_config(self, ssid, passw):
        sta_conf = dict(ssid=ssid, password=passw)
        with open(self.STA_FILE, 'w') as sta_file:
            sta_file.write(json.dumps(sta_conf))
        if not self.silent:
            print('DEFAULT WLAN: {} configured'.format(ssid))
