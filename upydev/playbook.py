from upydevice import Device, DeviceGroup
import os
import upydev
import json
import yaml
import shlex
import time
import multiprocessing

UPYDEV_PATH = upydev.__path__[0]
_playbook_dir = os.path.expanduser("~/.upydev_playbooks")

CHECK = "[\033[92m\u2714\x1b[0m]"
XF = "[\u001b[31;1m\u2718\u001b[0m]"


class DevConfig:
    def __init__(self, name, addr, pwd):
        self.name = name
        self.addr = addr
        self.pwd = pwd


def get_tsize():
    columns, rows = os.get_terminal_size(0)
    return columns


def parse_task_file(task_file):
    with open(task_file, "r") as tf:
        task_doc = tf.read()
    task = yaml.safe_load(task_doc)
    # print(task)
    return task


def gather_devices(devices):
    devs = []
    group_file = os.path.join(UPYDEV_PATH, "UPY_G")
    with open(f"{group_file}.config", "r", encoding="utf-8") as group:
        all_devices = json.loads(group.read())
        # print(devices)
    for name, conf in all_devices.items():
        if name in devices:
            devs.append(DevConfig(name, conf[0], conf[1]))

    return devs


def _play_task_file(task_file, args, dev_name):
    play_book = parse_task_file(task_file)[0]
    play_book_name = play_book["name"]
    # PLAY
    print(f"PLAY [{play_book_name}]")
    print("*" * get_tsize(), end="\n\n")
    if "hosts" in play_book:
        hosts = [dev.strip() for dev in play_book["hosts"].split(",")]
    else:
        hosts = [dev_name]
        if hasattr(args, 'devs'):
            if args.devs:
                hosts = args.devs
    print(f"HOSTS TARGET: [{', '.join(hosts)}]")
    devs = gather_devices(hosts)
    print(f"HOSTS FOUND : [{', '.join([dev.name for dev in devs])}]")
    print("*" * get_tsize(), end="\n\n")
    # TASK GATHERING FACTS #
    print("TASK [Gathering Facts]")
    print("*" * get_tsize(), end="\n\n")
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
    devgroup.devs = connected_devs
    devgroup.output_queue = {
            name: multiprocessing.Queue(maxsize=1) for name in connected_devs}
    for name, dev in connected_devs.items():
        if dev.dev_class == "SerialDevice":
            from upydev.shell.shserial import ShellSrCmds

            sh = ShellSrCmds(dev)
            shells[name] = sh
        elif dev.dev_class == "WebSocketDevice":
            from upydev.shell.shws import ShellWsCmds

            sh = ShellWsCmds(dev)
            shells[name] = sh
        elif dev.dev_class == "BleDevice":
            from upydev.shell.shble import ShellBleCmds

            sh = ShellBleCmds(dev)
            shells[name] = sh
        sh.dev_name = name
        sh.dsyncio.dev_name = name

    # RUNNING CUSTOM TASKS #
    custom_tasks = play_book["tasks"]

    for tsk in custom_tasks:
        print(f"\nTASK [{tsk['name']}]")
        print("*" * get_tsize(), end="\n\n")
        # RESET
        if "reset" in tsk.keys():
            for name, dev in connected_devs.items():
                print(f"[{name}]: {tsk['reset']}", end="\n\n")
                dev.reset()
                print("-" * get_tsize())
            print("RESET: DONE")
            print("-" * get_tsize())
        # WAIT
        if "wait" in tsk.keys():
            for i in range(tsk["wait"]):
                print(f"WAIT: {tsk['wait']-i}", end="\r")
                time.sleep(1)
            print("WAIT: DONE")
            print("-" * get_tsize())
        # LOAD
        if "load" in tsk.keys():
            script_to_load = tsk['load']
            if script_to_load not in os.listdir():
                if script_to_load.endswith(".py"):
                    script_to_load = os.path.join(os.path.dirname(task_file),
                                                  script_to_load)
            for name, sh in shells.items():
                if "include" in tsk.keys():
                    if name not in tsk["include"]:
                        continue
                if "ignore" in tsk.keys():
                    if name in tsk["ignore"]:
                        continue
                print(f"[{name}]: loading {script_to_load}", end="\n\n")
                if os.path.exists(script_to_load):
                    sh.dev.load(script_to_load)
                else:
                    sh.dev.paste_buff(script_to_load)
                    sh.dev.wr_cmd("\x04", follow=True)
                print("Done!")
                print("-" * get_tsize())
        # LOAD_PL
        if "load_pl" in tsk.keys():
            script_to_load = tsk['load_pl']
            if script_to_load not in os.listdir():
                script_to_load = os.path.join(os.path.dirname(task_file),
                                              script_to_load)
            pl_devs = [name for name in list(shells.keys())]
            for name, sh in shells.items():
                if "include" in tsk.keys():
                    if name not in tsk["include"]:
                        if name in pl_devs:
                            pl_devs.remove(name)
                if "ignore" in tsk.keys():
                    if name in tsk["ignore"]:
                        if name in pl_devs:
                            pl_devs.remove(name)

            print(f"[{', '.join(pl_devs)}]: loading {script_to_load}", end="\n\n")
            process_devices = {name: multiprocessing.Process(
                target=sh.dev.load, args=(script_to_load,)) for name,
                              sh in shells.items() if name in pl_devs}

            for dev in pl_devs:
                process_devices[dev].start()

            while True:
                try:
                    dev_proc_state = [process_devices[dev].is_alive(
                    ) for dev in pl_devs]
                    if all(state is False for state in dev_proc_state):
                        time.sleep(0.1)
                        break
                except KeyboardInterrupt:
                    while True:
                        dev_proc_state = [process_devices[dev].is_alive()
                                          for dev in pl_devs]
                        if all(state is False for state in dev_proc_state):
                            time.sleep(1)
                            for dev in pl_devs:
                                process_devices[dev].terminate()
                            break
            for dev in pl_devs:
                if shells[dev].dev.dev_class in ["WebSocketDevice"]:
                    if shells[dev].dev._uriprotocol == 'wss':
                        shells[dev].dev.flush()
                        shells[dev].dev.disconnect()
                        time.sleep(0.5)
                        shells[dev].dev.connect()
            print("Done!")
            print("-" * get_tsize())

        # COMMAND
        if "command" in tsk.keys():
            cmd = shlex.split(tsk["command"])
            if not cmd[0].startswith("%"):
                for name, sh in shells.items():
                    if "include" in tsk.keys():
                        if name not in tsk["include"]:
                            continue
                    if "ignore" in tsk.keys():
                        if name in tsk["ignore"]:
                            continue
                    print(f"[{name}]: {tsk['command']}", end="\n\n")
                    # check if shell cmd, if not use wr_cmd
                    if cmd[0] not in sh._shkw:
                        sh.dev.wr_cmd(tsk["command"], follow=True)
                    else:
                        sh.cmd(tsk["command"])
                    print("-" * get_tsize())
            else:
                print(f"[local]: {tsk['command']}", end="\n\n")
                sh.cmd(tsk["command"])
                print("-" * get_tsize())
        # COMMAND_NB
        if "command_nb" in tsk.keys():
            for name, sh in shells.items():
                if "include" in tsk.keys():
                    if name not in tsk["include"]:
                        continue
                if "ignore" in tsk.keys():
                    if name in tsk["ignore"]:
                        continue
                print(f"[{name}]: {tsk['command_nb']}", end="\n\n")
                cmd = shlex.split(tsk["command_nb"])
                if cmd[0] not in sh._shkw:
                    sh.dev.cmd_nb(tsk["command_nb"], block_dev=False)

                print("-" * get_tsize())
        # COMMAND_PL
        if "command_pl" in tsk.keys():
            pl_devs = [name for name in list(shells.keys())]
            for name, sh in shells.items():
                if "include" in tsk.keys():
                    if name not in tsk["include"]:
                        if name in pl_devs:
                            pl_devs.remove(name)
                if "ignore" in tsk.keys():
                    if name in tsk["ignore"]:
                        if name in pl_devs:
                            pl_devs.remove(name)

            cmd = shlex.split(tsk["command_pl"])
            if cmd[0] not in sh._shkw:
                print(f"[{', '.join(pl_devs)}]: {tsk['command_pl']}", end="\n\n")
                devgroup.cmd_p(tsk["command_pl"], include=pl_devs, follow=True)
                for dev in pl_devs:
                    if shells[dev].dev.dev_class in ["WebSocketDevice"]:
                        if shells[dev].dev._uriprotocol == 'wss':
                            shells[dev].dev.flush()
                            shells[dev].dev.disconnect()
                            time.sleep(0.5)
                            shells[dev].dev.connect()
            else:
                if "pytest" in tsk['command_pl']:
                    for dev in pl_devs:
                        if shells[dev].dev.dev_class in ["WebSocketDevice", "BleDevice"]:
                            shells[dev].dev.flush()
                            shells[dev].dev.disconnect()

                    time.sleep(0.5)

                process_devices = {name: multiprocessing.Process(
                    target=sh.cmd, args=(tsk["command_pl"],)) for name,
                                  sh in shells.items() if name in pl_devs}

                for dev in pl_devs:
                    print(f"[{dev}]: {tsk['command_pl']}", end="\n\n")
                    process_devices[dev].start()

                while True:
                    try:
                        dev_proc_state = [process_devices[dev].is_alive(
                        ) for dev in pl_devs]
                        if all(state is False for state in dev_proc_state):
                            time.sleep(0.1)
                            break
                    except KeyboardInterrupt:
                        while True:
                            dev_proc_state = [process_devices[dev].is_alive()
                                              for dev in pl_devs]
                            if all(state is False for state in dev_proc_state):
                                time.sleep(1)
                                for dev in pl_devs:
                                    process_devices[dev].terminate()
                                break

                if "pytest" in tsk['command_pl']:
                    for dev in pl_devs:
                        if shells[dev].dev.dev_class in ["WebSocketDevice", "BleDevice"]:
                            shells[dev].dev.connect()
                else:
                    for dev in pl_devs:
                        if shells[dev].dev.dev_class in ["WebSocketDevice"]:
                            if shells[dev].dev._uriprotocol == 'wss':
                                shells[dev].dev.flush()
                                shells[dev].dev.disconnect()
                                time.sleep(0.5)
                                shells[dev].dev.connect()

        print("*" * get_tsize(), end="\n\n")

    for name, dev in connected_devs.items():
        dev.disconnect()

    return


def play(args, rst_args, dev_name):
    for tsk_file in args.subcmd:
        if not tsk_file.endswith('.yaml'):
            tsk_file = os.path.join(_playbook_dir, f"{tsk_file}.yaml")
        if os.path.exists(tsk_file):
            _play_task_file(tsk_file, args, dev_name)
        else:
            print(f"play: No such task file: {tsk_file}")
        time.sleep(2)
