from upydevice import Device, DeviceGroup
import os
import upydev
import json
import yaml
import shlex
import time

UPYDEV_PATH = upydev.__path__[0]

CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'


class DevConfig:
    def __init__(self, name, addr, pwd):
        self.name = name
        self.addr = addr
        self.pwd = pwd


def get_tsize():
    columns, rows = os.get_terminal_size(0)
    return columns


def parse_task_file(task_file):
    with open(task_file, 'r') as tf:
        task_doc = tf.read()
    task = yaml.safe_load(task_doc)
    # print(task)
    return task


def gather_devices(devices):
    devs = []
    group_file = os.path.join(UPYDEV_PATH, "UPY_G")
    with open(f'{group_file}.config', 'r', encoding='utf-8') as group:
        all_devices = json.loads(group.read())
        # print(devices)
    for name, conf in all_devices.items():
        if name in devices:
            devs.append(DevConfig(name, conf[0], conf[1]))

    return devs


def _play_task_file(task_file):
    play_book = parse_task_file(task_file)[0]
    play_book_name = play_book["name"]
    # PLAY
    print(f"PLAY [{play_book_name}]")
    print("*"*get_tsize(), end='\n\n')
    hosts = [dev.strip() for dev in play_book["hosts"].split(',')]
    devs = gather_devices(hosts)

    # TASK GATHERING FACTS #
    print("TASK [Gathering Facts]")
    print("*"*get_tsize(), end='\n\n')
    connected_devs = {}
    for dev in devs:
        try:
            _dev = Device(dev.addr, dev.pwd, init=True)
            print(f"\u001b[32;1mok\x1b[0m {CHECK}: [{dev.name}]")
            connected_devs[dev.name] = _dev
        except Exception:
            print(f"\u001b[31;1mfatal\u001b[0m {XF}: [{dev.name}]: UNREACHABLE!")

    shells = {}
    devgroup = DeviceGroup(connected_devs.values())
    for name, dev in connected_devs.items():
        if dev.dev_class == 'SerialDevice':
            from upydev.shell.shserial import ShellSrCmds
            sh = ShellSrCmds(dev)
            shells[name] = sh
        elif dev.dev_class == 'WebSocketDevice':
            from upydev.shell.shws import ShellWsCmds
            sh = ShellWsCmds(dev)
            shells[name] = sh
        elif dev.dev_class == 'BleDevice':
            from upydev.shell.shble import ShellBleCmds
            sh = ShellBleCmds(dev)
            shells[name] = sh
        sh.dev_name = name
        sh.dsyncio.dev_name = name

    # RUNNING CUSTOM TASKS #
    custom_tasks = play_book["tasks"]

    for tsk in custom_tasks:
        print(f"\nTASK [{tsk['name']}]")
        print("*"*get_tsize(), end='\n\n')
        if 'command' in tsk.keys():
            for name, sh in shells.items():
                if 'include' in tsk.keys():
                    if name not in tsk['include']:
                        continue
                if 'ignore' in tsk.keys():
                    if name in tsk['ignore']:
                        continue
                print(f"[{name}]: {tsk['command']}", end='\n\n')
                # check if shell cmd, if not use wr_cmd
                cmd = shlex.split(tsk["command"])
                if cmd[0] not in sh._shkw:
                    sh.dev.wr_cmd(tsk["command"])
                else:
                    sh.cmd(tsk["command"])
                print("-"*get_tsize())
        if 'command_nb' in tsk.keys():
            for name, sh in shells.items():
                if 'include' in tsk.keys():
                    if name not in tsk['include']:
                        continue
                if 'ignore' in tsk.keys():
                    if name in tsk['ignore']:
                        continue
                print(f"[{name}]: {tsk['command_nb']}", end='\n\n')
                cmd = shlex.split(tsk["command_nb"])
                if cmd[0] not in sh._shkw:
                    sh.dev.cmd_nb(tsk["command_nb"], block_dev=False)

                print("-"*get_tsize())

        print("*"*get_tsize(), end='\n\n')

    for name, dev in connected_devs.items():
        dev.disconnect()

    return


def play(args, rst_args):
    for tsk_file in args.subcmd:
        _play_task_file(tsk_file)
        time.sleep(2)
