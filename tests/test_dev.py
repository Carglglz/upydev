from upydevice import Device
from functools import partial
import logging
import sys
import upydev
import json
import os


_SSL = False
CHECK = "[\033[92m\u2714\x1b[0m]"
XF = "[\u001b[31;1m\u2718\u001b[0m]"


# Logging Setup


log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels["info"])
logging.basicConfig(
    level=log_levels["debug"],
    format="%(asctime)s [%(name)s] [%(threadName)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler],
)
formatter = logging.Formatter(
    "%(asctime)s [%(name)s] [%(dev)s] [%(devp)s] : %(message)s"
)
handler.setFormatter(formatter)
log = logging.getLogger("pytest")

# INIT DEV


def test_devname(devname):
    global dev, log
    group_file = "UPY_G"
    # print(group_file)
    if "{}.config".format(group_file) not in os.listdir():
        group_file = "{}/{}".format(upydev.__path__[0], group_file)
    with open("{}.config".format(group_file), "r", encoding="utf-8") as group:
        devices = json.loads(group.read())
        # print(devices)
    devs = devices.keys()
    # NAME ENTRY POINT
    if devname in devs:
        dev_addr = devices[devname][0]
        dev_pass = devices[devname][1]
    else:
        if devname != "default":
            # load upydev_.config
            file_conf = "upydev_.config"
            if file_conf not in os.listdir():
                file_conf = os.path.join(upydev.__path__[0], "upydev_.config")

            with open(file_conf, "r") as config_file:
                upy_conf = json.loads(config_file.read())
                dev_addr = upy_conf["addr"]
                dev_pass = upy_conf["passwd"]

    dev = Device(dev_addr, dev_pass, init=True, autodetect=True)

    extra = {"dev": devname, "devp": dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)


def do_pass(test_name):
    log.info("{} TEST: {}".format(test_name, CHECK))


def do_fail(test_name):
    log.error("{} TEST: {}".format(test_name, XF))


def test_platform():
    TEST_NAME = "DEV PLATFORM"
    try:
        log.info(f"Running {dev.dev_class} test...")
        log.info("DEV PLATFORM: {}".format(dev.dev_platform))
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e


def test_dev(cmd):
    TEST_NAME = cmd.get('name')
    LOAD = cmd.get('load')
    HINT = cmd.get('hint')
    ARGS = cmd.get('args')
    COMMAND = cmd.get('command')
    DEVICE_RESULT = cmd.get('result')
    ASSERT_RESULT = cmd.get('assert')
    RELOAD = cmd.get('reload')

    try:
        log.info(f"Running [{TEST_NAME}] test...")
        if LOAD:
            log.info(f"Loading {LOAD} file...")
            dev.load(LOAD)
        if HINT:
            log.info(f"Hint: {HINT}")
        if ARGS:
            COMMAND = f"{COMMAND}(*{ARGS})"
        if COMMAND:
            log.info(f"Command [{COMMAND}] ")
            dev.wr_cmd(COMMAND, follow=True)
        if DEVICE_RESULT:
            RESULT = dev.wr_cmd(DEVICE_RESULT, silent=True, rtn_resp=True)
            RESULT_MSG = f"expected: {ASSERT_RESULT} --> result: {RESULT}"
            assert RESULT == ASSERT_RESULT, f"Test {TEST_NAME} FAILED: {RESULT_MSG}"
            log.info(RESULT_MSG)
        if RELOAD:
            dev.cmd(
                f"import sys,gc;del(sys.modules['{RELOAD}']);"
                f"gc.collect()"
            )
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        if RELOAD:
            dev.cmd(
                f"import sys,gc;del(sys.modules['{RELOAD}']);"
                f"gc.collect()"
            )
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e


def test_disconnect():
    TEST_NAME = "DEVICE DISCONNECT"
    log.info("{} TEST".format(TEST_NAME))
    try:
        dev.disconnect()
        assert not dev.connected, "Device Still Connected"
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e
        raise e
