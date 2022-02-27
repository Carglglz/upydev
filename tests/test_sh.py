from upydevice import Device
from functools import partial
import logging
import sys
import upydev
import json
import os


_SSL = False
CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'

FS_COMMANDS = ['ls', 'cat', 'head', 'rm', 'rmdir', 'mkdir', 'cd', 'pwd']

SHELL_CMD_TEST = ['info', 'mem', 'df', 'ls', 'cat', 'tree', 'du', 'run -r',
                  'id', 'uhelp', 'modules', 'set rtc', 'datetime', 'shasum', 'put',
                  'get']

NEEDS_FILE = ['cat', 'shasum', 'put', 'get', 'run -r']

RAW_COMMANDS = {'toggle_led': "import time;led.on();time.sleep(1);led.off()"}

DUMMY_FILE = 'dummy.py'

# Logging Setup

log_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
              'warning': logging.WARNING, 'error': logging.ERROR,
              'critical': logging.CRITICAL}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels['info'])
logging.basicConfig(
    level=log_levels['debug'],
    format="%(asctime)s [%(name)s] [%(threadName)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler])
formatter = logging.Formatter(
    '%(asctime)s [%(name)s] [%(dev)s] [%(devp)s] : %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('pytest')

# INIT DEV


def test_wss(use_ssl):
    global _SSL
    _SSL = use_ssl


def test_devname(devname):
    global dev, log, sh
    group_file = 'UPY_G'
    # print(group_file)
    if '{}.config'.format(group_file) not in os.listdir():
        group_file = '{}/{}'.format(upydev.__path__[0], group_file)
    with open('{}.config'.format(group_file), 'r', encoding='utf-8') as group:
        devices = json.loads(group.read())
        # print(devices)
    devs = devices.keys()
    # NAME ENTRY POINT
    if devname in devs:
        dev_addr = devices[devname][0]
        dev_pass = devices[devname][1]
    else:
        if devname != 'default':
            # load upydev_.config
            file_conf = 'upydev_.config'
            if file_conf not in os.listdir():
                file_conf = os.path.join(upydev.__path__[0], 'upydev_.config')

            with open(file_conf, 'r') as config_file:
                upy_conf = json.loads(config_file.read())
                dev_addr = upy_conf['addr']
                dev_pass = upy_conf['passwd']

    dev = Device(dev_addr, dev_pass, init=True, ssl=_SSL,
                 autodetect=True)

    extra = {'dev': devname, 'devp': dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)

    if dev.dev_class == 'SerialDevice':
        from upydev.shell.shserial import ShellSrCmds
        sh = ShellSrCmds(dev)
    elif dev.dev_class == 'WebSocketDevice':
        from upydev.shell.shws import ShellWsCmds
        sh = ShellWsCmds(dev)
    elif dev.dev_class == 'BleDevice':
        from upydev.shell.shble import ShellBleCmds
        sh = ShellBleCmds(dev)

    sh.dev_name = devname
    sh.dsyncio.dev_name = devname


def do_pass(test_name):
    log.info('{} TEST: {}'.format(test_name, CHECK))


def do_fail(test_name):
    log.error('{} TEST: {}'.format(test_name, XF))


def test_platform():
    TEST_NAME = 'DEV PLATFORM'
    try:
        log.info(f'Running {dev.dev_class} test...')
        log.info('DEV PLATFORM: {}'.format(dev.dev_platform))
        # print(dev)
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


for command in SHELL_CMD_TEST[:] + list(RAW_COMMANDS.keys()):
    def add_command(cmd=command):
        TEST_NAME = f'COMMAND: {cmd}'
        try:
            log.info(f'Running command [{cmd}] test...')
            if cmd in FS_COMMANDS:
                dev.wr_cmd("from upysh import *", silent=True)
            if cmd in NEEDS_FILE:
                cmd = f'{cmd} {DUMMY_FILE}'
            if cmd not in list(RAW_COMMANDS.keys()):
                sh.cmd(cmd)
            else:
                dev.wr_cmd(RAW_COMMANDS[cmd], follow=True)
            do_pass(TEST_NAME)
            print('Test Result: ', end='')
        except Exception as e:
            do_fail(TEST_NAME)
            print('Test Result: ', end='')
            raise e

    globals()[f'test_command_{command}'] = add_command


# def test_blink_led():
#     TEST_NAME = 'BLINK LED'
#     if dev.dev_platform == 'esp8266':
#         _ESP_LED = 2
#     elif dev.dev_platform == 'esp32':
#         _ESP_LED = 13
#     _led = dev.cmd("'led' in globals()", silent=True, rtn_resp=True)
#     if not _led:
#         dev.cmd('from machine import Pin; led = Pin({}, Pin.OUT)'.format(_ESP_LED))
#     for i in range(2):
#         dev.cmd('led.on();print("LED: ON")')
#         time.sleep(0.2)
#         dev.cmd('led.off();print("LED: OFF")')
#         time.sleep(0.2)
#     try:
#         assert dev.cmd('not led.value()', silent=True,
#                        rtn_resp=True), 'LED is on, should be off'
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e
#
#
# def test_run_script():
#     TEST_NAME = 'RUN SCRIPT'
#     log.info('{} TEST: test_code.py'.format(TEST_NAME))
#     dev.wr_cmd('import test_code', follow=True)
#     try:
#         assert dev.cmd('test_code.RESULT', silent=True,
#                        rtn_resp=True) is True, 'Script did NOT RUN'
#         dev.cmd("import sys,gc;del(sys.modules['test_code']);gc.collect()")
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e
#
#
# def test_raise_device_exception():
#     TEST_NAME = 'DEVICE EXCEPTION'
#     log.info('{} TEST: b = 1/0'.format(TEST_NAME))
#     try:
#         assert not dev.cmd(
#             'b = 1/0', rtn_resp=True), 'Device Exception: ZeroDivisionError'
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e
#
#
# def test_reset():
#     TEST_NAME = 'DEVICE RESET'
#     log.info('{} TEST'.format(TEST_NAME))
#     dev.reset()
#     try:
#         assert dev.connected, 'Device Not Connected'
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e
#
#
# def test_disconnect():
#     TEST_NAME = 'DEVICE DISCONNECT'
#     log.info('{} TEST'.format(TEST_NAME))
#     try:
#         dev.disconnect()
#         assert not dev.connected, 'Device Still Connected'
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e
