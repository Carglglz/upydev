import time


def fib(n):
    a, b = 0, 1
    while a < n:
        print(f"fib_{n}: {a}")
        a, b = b, a + b
        time.sleep_ms(1)
    return a


def do_serial_test():
    for i in range(20, 2500, 100):
        fib(i)
