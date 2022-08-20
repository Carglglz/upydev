from machine import Timer, reset, WDT
import time


class WatchDog:
    """Network watchdog"""

    def __init__(self, wlan, tim=1, tw=40000, tc=30000):
        self.wlan = wlan
        self.tim = Timer(tim)
        self.wdt = WDT(timeout=tw)
        self.irq_busy = False
        self.tc = tc
        self.tw = tw
        assert (self.tw - self.tc) >= 10, "Timeout too short"

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
                # reset()
        except Exception:
            self.irq_busy = False

    def start(self, timeout=None):
        if not timeout:
            timeout = self.tc
        self.irq_busy = False
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=self.check_network)

    def stop(self):
        self.tim.deinit()
        self.irq_busy = False
