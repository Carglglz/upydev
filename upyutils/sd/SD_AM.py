#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-05T20:19:56+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-10T00:55:01+01:00


from machine import SPI, Pin
import sdcard
import os
import time
# sd detect pin (15)
sd_detect = Pin(15, Pin.IN, pull=None)
sd_detect.value()

# sd sig (A5)
sd_sig = Pin(4, Pin.OUT)
sd_sig.value()
sd_sig.on()
sd_sig.value()
sd_detect.value()
# Callback
# LED
led = Pin(13, Pin.OUT)

sd_out = True
spi = SPI(1, baudrate=10000000, sck=Pin(5), mosi=Pin(18), miso=Pin(19))
cs = Pin(21, Pin.OUT)
# sd = sdcard.SDCard(spi, cs)
sd = None
irq_busy_sd = False


def pd_txtfiles(path, tabs=0):
    print("txt Files on filesystem:")
    print("====================")
    files = [filename for filename in os.listdir(
        path) if filename[-3:] == 'txt']
    for file in files:
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        _kB = 1000
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f kB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # # recursively print directory contents
        # if isdir:
        #     print_directory(path + "/" + file, tabs + 1)


def toggle_led_sd(x, butpress=sd_detect, light=led, sd_spi=spi, sd_cs=cs, getinfo=pd_txtfiles):
    global irq_busy_sd, sd_out, sd
    if irq_busy_sd:
        return
    else:
        irq_busy_sd = True
        if butpress.value() == 1:  # reverse op == 0
            if sd_out is True:
                print('SD card detected')
                for i in range(4):
                    led.value(not led.value())
                    time.sleep_ms(250)
                butpress.init(Pin.OUT)
                sd = sdcard.SDCard(sd_spi, sd_cs)
                time.sleep_ms(1000)
                os.mount(sd, '/sd')
                print(os.listdir('/'))
                # butpress.value(0)  # reverse op == 1
                butpress.init(Pin.IN)
                getinfo("/sd")
                sd_out = False
        # butpress.init(Pin.IN, Pin.PULL_UP)
        elif butpress.value() == 0:
            if sd_out is False:
                print('SD card removed')
                for i in range(4):
                    led.value(not led.value())
                    time.sleep_ms(250)
                time.sleep_ms(1000)
                butpress.init(Pin.OUT)
                os.umount('/sd')
                time.sleep_ms(1000)
                sd_out = True
        irq_busy_sd = False


sd_detect.irq(trigger=3, handler=toggle_led_sd)

if sd_detect.value() == 1:
    print('SD card detected')
    for i in range(4):
        led.value(not led.value())
        time.sleep_ms(250)
    sd_detect.init(Pin.OUT)
    sd = sdcard.SDCard(spi, cs)
    time.sleep_ms(1000)
    os.mount(sd, '/sd')
    print(os.listdir('/'))
    # butpress.value(0)  # reverse op == 1
    sd_detect.init(Pin.IN)
    pd_txtfiles("/sd")
    sd_out = False
else:
    print('SD card not detected')
