# !/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-11-10T19:52:25+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-14T22:39:25+00:00


from machine import Pin, PWM, Timer
import time


class NOTIFYER:
    def __init__(self, buzz_pin, led_pin, fq=4000, on_time=150, n_times=2,
                 off_time=50, timer=None, period=5000):

        self.led = Pin(led_pin, Pin.OUT)
        self.fq = fq
        self.duty = 512
        self.buzz = PWM(Pin(buzz_pin), freq=self.fq, duty=self.duty)
        self.buzz.deinit()
        self.on_time = on_time
        self.n_times = n_times
        self.off_time = off_time
        self.period = period
        self.irq_busy = False
        self.tim = timer
        self.blink = True
        self.use_dict = {'buzz': self.buzzer_call, 'led': self.blink_call}
        if timer is not None:
            self.tim = Timer(timer)

    def buzz_beep(self, beep_on_time, n_times, beep_off_time, fq, led=True):
        self.buzz.freq(fq)
        if led:
            for i in range(n_times):
                self.buzz.init()
                self.led.on()
                time.sleep_ms(beep_on_time)
                self.buzz.deinit()
                self.led.off()
                time.sleep_ms(beep_off_time)
        else:
            for i in range(n_times):
                self.buzz.init()
                time.sleep_ms(beep_on_time)
                self.buzz.deinit()
                time.sleep_ms(beep_off_time)

    def led_blink(self, led_on_time, n_times, led_off_time):
        for i in range(n_times):
            self.led.on()
            time.sleep_ms(led_on_time)
            self.led.off()
            time.sleep_ms(led_off_time)

    def buzzer_call(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            self.buzz_beep(self.on_time, self.n_times, self.off_time,
                           self.fq, self.blink)
            self.irq_busy = False

    def blink_call(self, x):
        if self.irq_busy:
            return
        else:
            self.irq_busy = True
            self.led_blink(self.on_time, self.n_times, self.off_time)
            self.irq_busy = False

    def notify(self, use='buzz', mode='SHOT', timeout=5000, on_init=None):
        self.irq_busy = False
        if on_init is not None:
            on_init()

        notify_call = self.use_dict[use]

        if mode == 'SHOT':
            self.tim.init(period=timeout, mode=Timer.ONE_SHOT,
                          callback=notify_call)
        elif mode == 'PERIODIC':
            self.tim.init(period=timeout, mode=Timer.PERIODIC,
                          callback=notify_call)

    def stop_notify(self):
        self.tim.deinit()
        self.irq_busy = False
