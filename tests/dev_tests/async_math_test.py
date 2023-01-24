import uasyncio as asyncio
import aioctl


@aioctl.aiotask
async def fib(n):
    a, b = 0, 1
    while a < n:
        print(f"fib_{n}: {a}")
        a, b = b, a + b
        asyncio.sleep_ms(1)
    return a


for i in range(20, 2500, 100):
    aioctl.add(fib, i, name=f"fib_{i}")


def do_async_test():
    aioctl.run()
