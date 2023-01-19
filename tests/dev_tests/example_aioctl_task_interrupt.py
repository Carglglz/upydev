from aiolog import streamlog
import pyb
import random
import upylog
import aiorepl
import uasyncio as asyncio
import aioctl
import sys

upylog.basicConfig(level="INFO", format="TIME_LVL_MSG", stream=streamlog)
log = upylog.getLogger(
    "device", log_to_file=False, rotate=1000
)  # This log to file 'error.log';


state = 20
aioctl.set_log(streamlog)
sw = pyb.Switch()
_TOGGLE_AIOREPL = False


def start_aiorepl_cb(x=None):
    global _TOGGLE_AIOREPL

    _TOGGLE_AIOREPL = not _TOGGLE_AIOREPL


sw.callback(start_aiorepl_cb)


def toggle_sysprint():
    upylog._stream = sys.stderr


@aioctl.aiotask
async def dbg_repl():
    await aiorepl.task(prompt=">>> ", shutdown_on_exit=False, exit_cb=toggle_sysprint)


@aioctl.aiotask
async def start_aiorepl():
    global _TOGGLE_AIOREPL
    while True:
        if _TOGGLE_AIOREPL:
            _TOGGLE_AIOREPL = not _TOGGLE_AIOREPL

            if "repl" not in aioctl.group().tasks:
                aioctl.add(dbg_repl, name="repl")
            else:
                if aioctl.group().tasks["repl"].task.done():
                    upylog._stream = streamlog
                    aioctl.start("repl")
                else:
                    print("aiorepl is running...")
        await asyncio.sleep_ms(200)


async def task_led(n, t, alog=log):
    try:
        i = 10 - n
        while state:
            # print("task 1")
            await asyncio.sleep_ms(t)
            pyb.LED(n).toggle()
            await asyncio.sleep_ms(50)
            pyb.LED(n).toggle()
            alog.info(f"[task_led_{n}] toggled LED {n}")
            if n > 3:
                i = round(i / (i - 1))
        pyb.LED(n).off()
        return random.random()
    except asyncio.CancelledError:
        pyb.LED(n).off()
        return random.random()
    except Exception as e:
        log.error(
            f"[task_led_{n}]" + f" {e.__class__.__name__}: {e.errno}",
        )
        pyb.LED(n).off()
        return e


async def main():
    print("starting tasks...")

    # start other program tasks.

    aioctl.add(task_led, 1, 10500, name="task_led_1")
    aioctl.add(task_led, 2, 10400, name="task_led_2")
    aioctl.add(task_led, 3, 10300, name="task_led_3")
    aioctl.add(task_led, 4, 10200, name="task_led_4")
    # start the aiorepl task.
    # aioctl.add(aiorepl.task, name="repl", prompt=">>> ")
    # start the aiorepl toggle task
    aioctl.add(start_aiorepl, name="aiotoggle")

    await asyncio.gather(*aioctl.tasks())


asyncio.run(main())
