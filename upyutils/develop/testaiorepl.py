import uasyncio as asyncio
import aiorepl
from machine import Pin

led = Pin(13, Pin.OUT)


async def demo():
    await asyncio.sleep_ms(10000)
    print("async demo")


state = 20

tasks = []


async def task_led(n, t):
    try:
        while state:
            # print("task 1")
            led.value(not led.value())
            await asyncio.sleep_ms(t)
    except asyncio.CancelledError:
        pass


async def main():
    global tasks
    print("starting tasks...")

    # start other program tasks.
    t1 = asyncio.create_task(task_led(1, 500))
    t2 = asyncio.create_task(demo())
    # t2 = asyncio.create_task(task_led(2, 400))
    # t3 = asyncio.create_task(task_led(3, 300))
    # t4 = asyncio.create_task(task_led(4, 200))
    # start the aiorepl task.
    repl = asyncio.create_task(aiorepl.task(prompt=">>> "))
    tasks += [t1, t2]

    await asyncio.gather(t1, t2, repl)


asyncio.run(main())
