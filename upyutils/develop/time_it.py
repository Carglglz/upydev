#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:24:19+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T18:28:23+01:00


import utime


def tzero():
    return utime.ticks_us()


def tdiff(t0):
    return utime.ticks_diff(utime.ticks_us(), t0)


def result(module_name, delta, cmd=False):
    if cmd:
        print('Command {} Time = {:6.3f}ms'.format(module_name, delta/1000))
    else:
        print('Script {} Time = {:6.3f}ms'.format(module_name, delta/1000))
