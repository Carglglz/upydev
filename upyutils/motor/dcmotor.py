#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:27:23+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T18:25:05+01:00


from machine import Pin, PWM


class DCMOTOR:
    """
    A simple class for controlling DC motors with a motor driver.

    Args:
        Direction turn pin (int): This pin must support PWM.
        Opposite direction turn pin (int): The pin must support PWM.

    """
    # vel_vals=[2000,2500,3000,3500,25000]

    def __init__(self, direction_pin, oppo_pin):
        self.direction_pin = PWM(Pin(direction_pin), freq=50, duty=0)
        self.direction_pin.deinit()
        self.oppo_pin = PWM(Pin(oppo_pin), freq=50, duty=0)
        self.oppo_pin.deinit()
        self.freq = 50

    def move(self, direction, delay_vel):
        self.direction_pin.deinit()
        self.oppo_pin.deinit()
        if direction == 1:
            self.direction_pin.init(duty=delay_vel)
        elif direction == 0:
            self.oppo_pin.init(duty=delay_vel)
        else:
            pass

    def stop(self):
        self.direction_pin.deinit()
        self.oppo_pin.deinit()
