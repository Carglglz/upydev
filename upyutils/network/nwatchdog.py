from machine import Timer, reset, WDT
import time

class WatchDog:
    """Network watchdog"""
    def __init__(self, wlan, tim=1):
        self.wlan = wlan
        self.tim = Timer(tim)
        self.wdt = WDT(timeout=40000)
        self.irq_busy = False

    def check_network(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.wlan.isconnected():
                self.irq_busy = False
                self.wdt.feed()
            else:
                print('WLAN disconnected, rebooting...')
                time.sleep(1)
                #reset()
        except Exception as e:
            self.irq_busy = False

    def start(self, timeout=30000):
        self.irq_busy = False
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=self.check_network)

    def stop(self):
        self.tim.deinit()
        self.irq_busy = False

