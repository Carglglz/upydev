#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:25:14+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-09-23T01:29:38+01:00


from machine import Timer, PWM, Pin
import time
import urandom

B0 = 31
C1 = 33
CS1 = 35
D1 = 37
DS1 = 39
E1 = 41
F1 = 44
FS1 = 46
G1 = 49
GS1 = 52
A1 = 55
AS1 = 58
B1 = 62
C2 = 65
CS2 = 69
D2 = 73
DS2 = 78
E2 = 82
F2 = 87
FS2 = 93
G2 = 98
GS2 = 104
A2 = 110
AS2 = 117
B2 = 123
C3 = 131
CS3 = 139
D3 = 147
DS3 = 156
E3 = 165
F3 = 175
FS3 = 185
G3 = 196
GS3 = 208
A3 = 220
AS3 = 233
B3 = 247
C4 = 262
CS4 = 277
D4 = 294
DS4 = 311
E4 = 330
F4 = 349
FS4 = 370
G4 = 392
GS4 = 415
A4 = 440
AS4 = 466
B4 = 494
C5 = 523
CS5 = 554
D5 = 587
DS5 = 622
E5 = 659
F5 = 698
FS5 = 740
G5 = 784
GS5 = 831
A5 = 880
AS5 = 932
B5 = 988
C6 = 1047
CS6 = 1109
D6 = 1175
DS6 = 1245
E6 = 1319
F6 = 1397
FS6 = 1480
G6 = 1568
GS6 = 1661
A6 = 1760
AS6 = 1865
B6 = 1976
C7 = 2093
CS7 = 2217
D7 = 2349
DS7 = 2489
E7 = 2637
F7 = 2794
FS7 = 2960
G7 = 3136
GS7 = 3322
A7 = 3520
AS7 = 3729
B7 = 3951
C8 = 4186
CS8 = 4435
D8 = 4699
DS8 = 4978


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
        self.mario = [E7, E7, 0, E7, 0, C7, E7, 0, G7, 0, 0, 0, G6, 0, 0, 0,
                      C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0,
                      G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0, C7, D7, B6, 0, 0,
                      C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0,
                      G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0, C7, D7, B6, 0, 0,
                      G7, FS7, F7, DS7, 0, E7, 0, GS6, A6, C7, 0, 0, A6, C7, D7,
                      G7, FS7, F7, DS7, 0, E7, 0, 0, C8, 0, C8, C8, 0, 0, 0,
                      G7, FS7, F7, DS7, 0, E7, 0, GS6, A6, C7, 0, 0, A6, C7, D7,
                      0, 0, DS7, 0, D7, 0, 0, C7, 0, 0, 0, C7, C7, 0, C7, 0, C7,
                      D7, 0, E7, C7, 0, A6, G6, 0, 0, C7, C7, 0, C7, 0, C7, D7,
                      E7, 0, 0, C7, C7, 0, C7, 0, C7, D7, 0, E7, C7, 0, A6, G6,
                      0, E7, E7, E7, 0, C7, E7, 0, G7, 0, 0, 0, 0, G6,
                      E7, C7, 0, G6, 0, GS6, 0, 0, A6, 0, F7, 0, F7, A6, 0, B6,
                      A7, 0, A7, 0, A7, 0, G7, 0, F7, 0, E7, C7, 0, A6, G6, 0,
                      0, E7, C7, 0, G6, 0, GS6, 0, 0, A6, F7, 0, F7, A6, 0, 0,
                      B6, 0, F7, 0, F7, 0, F7, 0, E7, 0, D7, 0, C7, 0, 0, 0,
                      C7, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, A6, 0, 0, GS6,
                      0, AS6, 0, GS6, 0, 0, E6, D6, E6]

    def time_print(self):
        return ('{}:{}:{}'.format(time.localtime()[3],
                                  time.localtime()[4],
                                  time.localtime()[5]))

    def buzz_beep(self, sleeptime, ntimes, ntimespaced, fq):
        for i in range(ntimes):
            self.buzz.init()
            self.buzz.freq(fq)
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
        self.buff[0], self.buff[1], self.buff[2] = time.localtime()[3], time.localtime()[
            4], time.localtime()[5]
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
        self.buzz_detect.irq(trigger=Pin.IRQ_RISING,
                             handler=self.buzzer_callback)

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
        self.buzz_detect.irq(trigger=Pin.IRQ_FALLING,
                             handler=self.buzzer_callback_rev)

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

    def sound_effect_up_down(self, fi, ff, fst, ts):
        fq_range = [i for i in range(fi, ff, fst)]
        self.buzz.init()
        for f in fq_range:
            self.buzz.freq(f)
            time.sleep_ms(ts)
        fq_range.reverse()
        for f in fq_range:
            self.buzz.freq(f)
            time.sleep_ms(ts)
        self.buzz.deinit()

    def sound_effect_random(self, fi, ff, fst, ts):
        fq_range = [urandom.randint(fi, ff) for i in range(fi, ff, fst)]
        self.buzz.init()
        for f in fq_range:
            self.buzz.freq(f)
            time.sleep_ms(ts)
        fq_range.reverse()
        for f in fq_range:
            self.buzz.freq(f)
            time.sleep_ms(ts)
        self.buzz.deinit()

    def sec_alarm(self, ntimes=10):
        for i in range(ntimes):
            self.sound_effect_up_down(1250, 6250, 200, 5)

    def _warning(self, fl, fh, ts=100, ntimes=10):
        self.buzz.init()
        for i in range(ntimes):
            self.buzz.freq(fl)
            time.sleep_ms(ts)
            self.buzz.freq(fh)
            time.sleep_ms(ts)
        self.buzz.deinit()

    def warning_call(self, ntimes=1):
        for i in range(ntimes):
            self._warning(4000, 800, 180, 3)

    def phone_call(self, ntimes=1):
        for i in range(ntimes):
            self._warning(4000, 800, 80, 10)

    def door_bell(self):
        self._warning(1000, 800, 600, 1)

    def error(self):
        self.buzz_beep(350, 2, 50, 100)

    def play_tone(self, ts, scale=0, tone=None):
        if tone is None:
            tone = self.mario
        self.buzz.init()
        for f in tone:
            if f != 0:
                self.buzz.freq(f+scale)
            else:
                self.buzz.freq(f)
            time.sleep_ms(ts)
        self.buzz.deinit()
