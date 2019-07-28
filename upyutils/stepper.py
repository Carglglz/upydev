#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-23T00:26:27+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T18:28:00+01:00


from machine import Pin
import time


class STEPPER:
    """
    A simple class for controlling stepper motors with A4988.

    Args:
        direction pin (int): The pin where direction pin is connected. Must support PWM.
        step pin (int): The pin where step pin is connected. Must support PWM.

    """
    # vel_vals=[2000,2500,3000,3500,25000]

    def __init__(self, direction_pin, step_pin):
        self.direction_pin = Pin(direction_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.direction_pin.off()

    def move(self, direction, delay_vel):

        if direction == 1:
            self.direction_pin.on()
            self.step_pin.on()
            time.sleep_us(5)
            self.step_pin.off()
            time.sleep_us(delay_vel)
        elif direction == 0:
            self.direction_pin.off()
            self.step_pin.on()
            time.sleep_us(5)
            self.step_pin.off()
            time.sleep_us(delay_vel)
        else:
            pass

    def move_n_steps(self, direction, delay_vel, n, delay_step=1):
        for i in range(n):
            self.move(direction, delay_vel)
            time.sleep_ms(delay_step)
