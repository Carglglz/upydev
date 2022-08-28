import time
from pyb import Switch


def do_wait_for_push(t):
    n = 0
    sw = Switch()
    while not sw.value():
        print(f"Waiting for button press: [{t-n}]")
        time.sleep(1)
        n += 1
        if n > t:
            print("\n Timeout")
            return False
    print("\nButton pressed!")
    return True
