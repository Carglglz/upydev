#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:25:14+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-09-23T01:29:38+01:00


from machine import Timer, PWM, Pin
import time


class BUZZER:

    def __init__(self, PIN, fq=4000, duty=512, sleept=150, ntimes=2, ntspace=50):
        self.duty = duty
        self.fq = fq
        self.buff = bytearray(3)
        self.tim = Timer(-1)
        self.tim2 = Timer(2)
        self.irq_busy = False
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.alarm = False
        self.buzz = PWM(Pin(PIN), freq=self.fq, duty=self.duty)
        self.buzz.deinit()
        self.buzz_button = Pin(12, Pin.OUT)
        self.buzz_detect = Pin(32, Pin.IN)
        self.buzz_button.on()
        self.irq_busy_buzz = False
        self.sleeptime = sleept
        self.ntimes = ntimes
        self.ntspace = ntspace

    def time_print(self):
        return ('{}:{}:{}'.format(time.localtime()[3],
                                  time.localtime()[4],
                                  time.localtime()[5]))

    def buzz_beep(self, sleeptime, ntimes, ntimespaced, fq):
        self.buzz.freq(fq)
        for i in range(ntimes):
            self.buzz.init()
            time.sleep_ms(sleeptime)
            self.buzz.deinit()
            time.sleep_ms(ntimespaced)

    def set_alarm_at(self, h, m, s):
        self.alarm = True
        self.hour = h
        self.minute = m
        self.second = s
        self.start_alarm()

    def check_alarm(self):
        self.buff[0], self.buff[1], self.buff[2] = time.localtime()[3], time.localtime()[4], time.localtime()[5]
        if (self.buff[0] == self.hour) and (self.buff[1] == self.minute) and (self.buff[2] == self.second):
            return True

    def beep_alarm(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            # print(self.time_print())
            if self.alarm is True:
                if self.check_alarm():
                    for i in range(3):
                        self.buzz_beep(150, 3, 100, self.fq)
                        time.sleep_ms(500)
                    self.tim.deinit()
                    self.alarm = False
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start_alarm(self, timeout=1000):
        self.irq_busy = False
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=self.beep_alarm)

    def stop(self):
        self.tim.deinit()
        self.irq_busy = False

    def buzzer_callback(self, x):
        if self.irq_busy_buzz:
            return
        else:
            if self.buzz_detect.value() == 1:  # reverse op == 0
                self.buzz_beep(150, 3, 100, self.fq)
                self.buzz_detect.init(Pin.OUT)
                time.sleep_ms(1000)
                self.buzz_detect.value(0)  # reverse op == 1
                self.buzz_detect.init(Pin.IN)
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy_buzz = False

    def active_button(self, PIN1, PIN2):
        self.buzz_button = Pin(PIN1, Pin.OUT)
        self.buzz_detect = Pin(PIN2, Pin.IN)
        self.buzz_button.on()
        self.buzz_detect.irq(trigger=Pin.IRQ_RISING, handler=self.buzzer_callback)

    def buzzer_callback_rev(self, x):
        if self.irq_busy_buzz:
            return
        else:
            if self.buzz_detect.value() == 0:  # reverse op == 0
                self.buzz_beep(150, 3, 100, self.fq)
                self.buzz_detect.init(Pin.OUT)
                time.sleep_ms(1000)
                self.buzz_detect.value(1)  # reverse op == 1
                self.buzz_detect.init(Pin.IN)
            # butpress.init(Pin.IN, Pin.PULL_UP)
            self.irq_busy_buzz = False

    def active_button_rev(self, PIN1, PIN2):
        self.buzz_button = Pin(PIN1, Pin.OUT)
        self.buzz_detect = Pin(PIN2, Pin.IN)
        self.buzz_button.on()
        self.buzz_detect.irq(trigger=Pin.IRQ_FALLING, handler=self.buzzer_callback_rev)

    def buzz_beep_callback(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.buzz_beep(self.sleeptime, self.ntimes, self.ntspace, self.fq)
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def beep_interrupt(self):
        self.irq_busy = False
        self.tim2.init(period=1, mode=Timer.ONE_SHOT,
                      callback=self.buzz_beep_callback)
