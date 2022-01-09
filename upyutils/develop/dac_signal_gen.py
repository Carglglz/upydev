#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:25:01+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T18:24:56+01:00


import math
from machine import Timer
from micropython import const


class SIGNAL_GENERATOR:

    def __init__(self, dac, type, Amp, fq):
        self.fs = 1000
        self.BUFFERSIZE = const(1000)
        self.Amp = Amp
        self.fq = fq
        self.buff = bytearray(1000)
        self.tim = Timer(-1)
        self.irq_busy = False
        self.dac = dac
        self.index_put = 0
        self.type = type
        if type == 'sin':
            for i in range(self.fs):
                self.buff[i] = self.sin_signal(self.Amp, self.fq, i)
        elif type == 'sq':
            for i in range(self.fs):
                self.buff[i] = self.square_signal(self.Amp, self.fq, i)

    def sign(self, val):
        if val > 0:
            return 1
        else:
            return -1

    def sin_signal(self, Amp, fq, tn, DC=128):
        amp8b = int(((Amp)/3.3)*255)
        sig = amp8b*math.sin(2*math.pi*fq*tn/self.fs)+DC
        return int(sig)

    def square_signal(self, Amp, fq, tn, DC=128):
        amp8b = int(((Amp)/3.3)*255)
        sig = amp8b*self.sign(math.sin(2*math.pi*fq*tn/self.fs))+DC
        return int(sig)

    def modsig(self, Amp, fq):
        self.Amp = Amp
        self.fq = fq
        if self.type == 'sin':
            for i in range(self.fs):
                self.buff[i] = self.sin_signal(self.Amp, self.fq, i)
        elif self.type == 'sq':
            for i in range(self.fs):
                self.buff[i] = self.square_signal(self.Amp, self.fq, i)

    def sig_write(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE:
                self.dac.write(self.buff[self.index_put])
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE:
                self.index_put = 0
                self.dac.write(self.buff[self.index_put])
                self.index_put += 1
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start(self, timeout=1):
        self.irq_busy = False
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=self.sig_write)

    def stop(self):
        self.tim.deinit()
        self.irq_busy = False
