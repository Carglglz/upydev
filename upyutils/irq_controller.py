#!/usr/bin/env python3

from machine import Pin, PWM
import time
from array import array
import socket


class IRQ_MG:
    def __init__(self, signal_pin, irq_pin, buzz_pin=None, led_pin=None,
                 timeout=1000, driver_pin=None, sensor=None, n_vars=3,
                 p_format='f'):
        self.sig_pin = signal_pin
        self.irq_pin = irq_pin
        self.driver_pin = driver_pin
        self.sig_button = None
        self.irq_detect = None
        self.fq = 4000
        self.duty = 512
        self.irq_busy = False
        if buzz_pin is not None:
            self.buzz = PWM(Pin(buzz_pin), freq=self.fq, duty=self.duty)
            self.buzz.deinit()
        if led_pin is not None:
            self.led = Pin(led_pin, Pin.OUT)
        self.irq_count = 0
        self.irq_message = "INTERRUPT DETECTED"
        self.irq_detflag = False
        self.irq_timeout = timeout  # ms
        self.sensor = sensor
        self.sensor_vals = array(p_format, (0 for _ in range(n_vars)))
        self.cli_soc = None

    def reset_flag(self):
        self.irq_detflag = False

    def reset_flag_counter(self):
        self.irq_count = 0

    def set_irq_msg(self, msg):
        self.irq_message = msg

    def irq_state(self):
        state = {'IRQ_DETECTED': self.irq_detflag,
                 'IRQ_COUNT': self.irq_count,
                 'SENSOR_DATA': list(self.sensor_vals)}
        self.reset_flag()
        return(state)

    def wait_irq(self, reset=True):
        if reset:
            self.reset_flag()
        while not self.irq_detflag:
            pass
        time.sleep_ms(10)
        return self.irq_state()

    def wait_async_irq(self, reset=True):
        if reset:
            self.reset_flag()
        while not self.irq_detflag:
            pass
        time.sleep_ms(10)
        return self.irq_state()

    def check_irq(self):
        return self.irq_state()

    def connect_SOC(self, host, port):
        self.irq_busy = True
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, port)[0][-1]
        self.cli_soc.connect(soc_addr)
        self.irq_busy = False

    def disconnect_SOC(self):
        self.irq_busy = True
        self.cli_soc.close()
        self.irq_busy = False

    def buzz_beep(self, sleeptime, ntimes, ntimespaced, fq):
        self.buzz.freq(fq)
        for i in range(ntimes):
            self.buzz.init()
            time.sleep_ms(sleeptime)
            self.buzz.deinit()
            time.sleep_ms(ntimespaced)

    def led_blink(self, sleeptime, ntimes, ntimespaced):
        for i in range(ntimes):
            self.led.on()
            time.sleep_ms(sleeptime)
            self.led.off()
            time.sleep_ms(ntimespaced)

    def active_button(self, callback):
        self.sig_button = Pin(self.sig_pin, Pin.OUT)
        self.irq_detect = Pin(self.irq_pin, Pin.IN)
        self.sig_button.on()
        self.irq_detect.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def active_button_rev(self, callback):
        self.sig_button = Pin(self.sig_pin, Pin.OUT)
        self.irq_detect = Pin(self.irq_pin, Pin.IN)
        self.sig_button.on()
        self.irq_detect.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    def buzzer_callback(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 1:  # reverse op == 0
                self.buzz_beep(150, 3, 100, self.fq)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(0)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def buzzer_callback_rev(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 0:  # reverse op == 0
                self.buzz_beep(150, 3, 100, self.fq)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(1)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def led_callback(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 1:  # reverse op == 0
                self.led_blink(150, 3, 100)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(0)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def led_callback_rev(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 0:  # reverse op == 0
                self.led_blink(150, 3, 100)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(1)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def msg_callback(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 1:  # reverse op == 0
                print(self.irq_message)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(0)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def msg_callback_rev(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 0:  # reverse op == 0
                print(self.irq_message)
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(1)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def sensor_callback(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 1:  # reverse op == 0
                print(self.irq_message)
                # returns array()
                self.sensor_vals[:] = self.sensor.read_data()
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(0)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False

    def sensor_soc_callback(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            if self.irq_detect.value() == 1:  # reverse op == 0
                print(self.irq_message)
                self.cli_soc.sendall(self.sensor.read_data())
                self.irq_detect.init(Pin.OUT)
                time.sleep_ms(self.irq_timeout)
                self.irq_detect.value(0)  # reverse op == 1
                self.irq_detect.init(Pin.IN)
                self.irq_count += 1
                self.irq_detflag = True
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy = False
