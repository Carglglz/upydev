# Example program to enable WebREPL + aioREPL --> WebaioREPL

import network
import wss_repl
from machine import Pin
import time
from ssl_config import SSL
import json
from wpa_supplicant import setup_network
import ntptime
import aiorepl
import uasyncio as asyncio

# LED
led = Pin(13, Pin.OUT)

# Connect to an AP or setup device AP
if setup_network():
    # Set time
    try:
        ntptime.settime()
    except Exception as e:
        print(e)
else:
    ap = network.WLAN(network.AP_IF)
    print("AP ENABLED")
    with open("ap_.config", "r") as ap_file:
        ap_config = json.load(ap_file)
    ap.active(True)
    ap.config(
        essid=ap_config["ssid"],
        authmode=network.AUTH_WPA_WPA2_PSK,
        password=ap_config["password"],
    )
    print("Acces point configurated: {}".format(ap_config["ssid"]))
    print(ap.ifconfig())


# Start WebREPL
wss_repl.start(ssl=SSL.ssl)

for i in range(10):
    led.value(not led.value())
    time.sleep(0.2)
led.value(False)

# Enable aioREPL

# where to save tasks so they can be cancelled at REPL with tasks[0].cancel()
# it could be a dict too.
tasks = []

# example task for toggling a led


async def task_led(n, t):
    try:
        while True:
            # print("task 1")
            led.value(not led.value())
            await asyncio.sleep_ms(t)
    except asyncio.CancelledError:
        # Or print a message/clean state
        # This error must be catched otherwise propagates and stops the event
        # loop
        pass


# Main task that will run sample tasks + aiorepl task
async def main():
    global tasks
    print("starting tasks...")

    # start other program tasks.
    t1 = asyncio.create_task(task_led(1, 500))
    # t2 = asyncio.create_task(task_led(2, 400))
    # t3 = asyncio.create_task(task_led(3, 300))
    # t4 = asyncio.create_task(task_led(4, 200))

    # start the aiorepl task.
    repl = asyncio.create_task(aiorepl.task(prompt=">>> "))
    tasks += [t1, repl]

    await asyncio.gather(t1, repl)


asyncio.run(main())

# Now aioREPL is shown,
# Here you can cancel current running tasks
# or create new tasks with
# new_task = asyncio.create_task(task_led(5, 1200))
# Then this task will be executed in current event loop.
