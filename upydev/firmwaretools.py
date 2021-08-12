from upydevice import Device
import sys
from upydev.helpinfo import see_help
from upydevice import check_device_type
import os
from datetime import datetime, timedelta
import requests
import shlex
import subprocess
import upydev
import re
import time

UPYDEV_PATH = upydev.__path__[0]

FIRMWARE_HELP = """
> FIRMWARE: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - fwr: to list or get available firmware versions, use -md option to indicate operation:
                to list do: "upydev fwr -md list -b [BOARD]" board can be e.g. 'esp32','esp8266' or 'PYBD'
                            "upydev fwr -md list latest -b [BOARD]" to see the latest firmware available
                to get do: "upydev fwr -md get [firmware file]" or "upydev fwr -md get latest -b[BOARD]"
                * for list or get modes the -n option will filter the results further: e.g. -n ota
                to see available serial ports do: "upydev fwr -md list serial_ports"

        - flash: to flash a firmware file to the upydevice, a serial port must be indicated
                    to flash do: "upydev flash -port [serial port] -f [firmware file]"

        - mpyx : To froze a module/script , and save some RAM, it uses mpy-cross tool
                 (mpy-cross must be available in $PATH) e.g. $ upydev mpyx [FILE].py,
                 $ upydev mpyx [FILE].py [FILE2].py, $ upydev mpyx *.py"""


def get_fw_versions(keyword):
    fw_list = []
    fw_links = []
    r = requests.get('https://micropython.org/download/all/')
    fw_text = [line for line in r.text.split(
        '\n') if keyword in line and any(x in line for x in ['bin', 'dfu', 'zip']) and 'firmware' in line]
    if not fw_text:
        keyword = keyword[:3]
        fw_text = [line for line in r.text.split(
            '\n') if keyword in line and any(x in line for x in ['bin', 'dfu', 'zip']) and 'firmware' in line]
    for line in fw_text:
        for element in re.split(r"[=<>]+", line):
            if 'firmware' in element:
                fw_links.append('www.micropython.org{}'.format(element[1:-1]))
                fw_list.append(element[1:-1].split('/')[3])
    if not fw_text:
        keyword = keyword[:3]
    fw_dict = dict(zip(fw_list, fw_links))
    return fw_dict, fw_list


def firmwaretools_action(args, **kargs):

    # MPYX

    if args.m == 'mpyx':
        if not args.f:
            print('File name required indicate with -f option.')
            see_help(args.m)
        else:
            if args.f not in os.listdir():
                print('File not found, indicate a valid file')
            else:
                print('Frozing {} to bytecode with mpy-cross'.format(args.f))
                mpy_cmd_str = 'python -m mpy_cross {}'.format(args.f)
                mpy_cmd = shlex.split(mpy_cmd_str)
                try:
                    mpy_tool = subprocess.call(mpy_cmd)
                    if mpy_tool == 0:
                        print('Process successful, bytecode in : {}'.format(
                                                args.f.replace('py', 'mpy')))
                    else:
                        print('Process failed.')
                except KeyboardInterrupt:
                    pass

        sys.exit()

    # FW
    elif args.m == 'fwr':
        if not args.md:
            print('Argument mode required (list, or get), indicate with -md')
            see_help(args.m)
            sys.exit()
        else:
            if args.md[0] == 'list':
                if not args.b:  # Autodetect
                    try:
                        dev = Device(args.t, args.p, init=True, autodetect=True,
                                     ssl=args.wss, auth=args.wss)
                        args.b = dev.dev_platform
                        if dev.dev_platform == 'pyboard':
                            machine = dev.cmd('import os;os.uname().machine',
                                              silent=True, rtn_resp=True)
                            machine, version = machine.split()[0].split('v')
                            version_str = version.replace('.', '')
                            machine = machine.lower()
                            args.b = "{}v{}".format(machine, version_str)
                        dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Indicate a device platform with -b option')
                        sys.exit()
                if len(args.md) > 1:
                    if args.md[1] == 'latest':
                        today = datetime.strftime(datetime.now(), "%Y%m%d")
                        fw_v = get_fw_versions(args.b)
                        if fw_v[1]:
                            print('Latest Firmware versions found for {}:'.format(args.b))
                            fw_v_latest = [v for v in fw_v[1] if today in v]
                            days_before = 0
                            while len(fw_v_latest) == 0:
                                if len(fw_v[1]) == 0:
                                    break
                                days_before += 1
                                latest_fw = datetime.strftime(
                                    datetime.now()-timedelta(days=days_before), "%Y%m%d")
                                fw_v_latest = [v for v in fw_v[1] if latest_fw in v]
                            if args.n is not None:
                                if args.n != 'def':
                                    fw_v_latest_opt = [
                                        v for v in fw_v_latest if args.n in v]
                                    for v in fw_v_latest_opt:
                                        print('- {}'.format(v))
                                else:
                                    print('- {}'.format(fw_v_latest[0]))
                            else:
                                for v in fw_v_latest:
                                    print('- {}'.format(v))
                        else:
                            print('No firmware available that match: {}'.format(args.b))
                        # fw_v_latest_link = fw_v[0][fw_v_latest]

                else:
                    fw_v = get_fw_versions(args.b)[1]
                    if not fw_v:
                        print('No firmware available that match: {}'.format(args.b))
                    else:
                        if args.n is not None:
                            print('Firmware versions found for {}-{}:'.format(args.b, args.n))
                            if args.n != 'def':
                                fw_v_opt = [v for v in fw_v if args.n in v]
                                for v in fw_v_opt:
                                    print('- {}'.format(v))
                            else:
                                print('- {}'.format(fw_v[0]))
                        else:
                            print('Firmware versions found for {}:'.format(args.b))
                            for version in fw_v:
                                print('- {}'.format(version))
            elif args.md[0] == 'get':
                if len(args.md) > 1:
                    if args.md[1] == 'latest':
                        if not args.b:  # Autodetect
                            try:
                                dev = Device(args.t, args.p, init=True, autodetect=True,
                                             ssl=args.wss, auth=args.wss)
                                args.b = dev.dev_platform
                                if dev.dev_platform == 'pyboard':
                                    machine = dev.cmd('import os;os.uname().machine',
                                                      silent=True, rtn_resp=True)
                                    machine, version = machine.split()[0].split('v')
                                    version_str = version.replace('.', '')
                                    machine = machine.lower()
                                    args.b = "{}v{}".format(machine, version_str)
                                dev.disconnect()
                            except Exception as e:
                                print(e)
                                print('Indicate a device platform with -b option')
                                sys.exit()
                        today = datetime.strftime(datetime.now(), "%Y%m%d")
                        fw_v = get_fw_versions(args.b)

                        if fw_v[1]:
                            print('Latest version found for {}:'.format(args.b))
                            fw_v_latest = [v for v in fw_v[1] if today in v]
                            days_before = 0
                            while len(fw_v_latest) == 0:
                                if len(fw_v[1]) == 0:
                                    break
                                days_before += 1
                                latest_fw = datetime.strftime(
                                    datetime.now()-timedelta(days=days_before), "%Y%m%d")
                                fw_v_latest = [v for v in fw_v[1] if latest_fw in v]
                            if args.n is not None:
                                if args.n != 'def':
                                    fw_v_latest = [
                                        v for v in fw_v_latest if args.n in v]
                                    for v in fw_v_latest:
                                        print('- {}'.format(v))
                            else:
                                print('- {}'.format(fw_v_latest[0]))
                            if len(fw_v_latest) >= 1:
                                fw_v_latest = fw_v_latest[0]
                                print('Firmware selected: {}'.format(fw_v_latest))
                                fw_v_latest_link = fw_v[0][fw_v_latest]
                                print('Downloading {} ...'.format(fw_v_latest))
                                curl_cmd_str = "curl -O '{}'".format(fw_v_latest_link)
                                curl_cmd = shlex.split(curl_cmd_str)
                                try:
                                    proc = subprocess.call(curl_cmd)
                                    print('Done!')
                                except KeyboardInterrupt:
                                    print('Operation cancelled')
                        else:
                            print('No firmware available that match: {}'.format(args.b))
                    else:
                        fw_v_link = get_fw_versions(args.md[1])[0][args.md[1]]
                        print('Downloading {} ...'.format(args.md[1]))
                        curl_cmd_str = "curl -O '{}'".format(fw_v_link)
                        curl_cmd = shlex.split(curl_cmd_str)
                        try:
                            proc = subprocess.call(curl_cmd)
                            print('Done!')
                        except KeyboardInterrupt:
                            print('Operation cancelled')
                else:
                    if not args.b:  # Autodetect
                        try:
                            dev = Device(args.t, args.p, init=True, autodetect=True,
                                         ssl=args.wss, auth=args.wss)
                            args.b = dev.dev_platform
                            if dev.dev_platform == 'pyboard':
                                machine = dev.cmd('import os;os.uname().machine',
                                                  silent=True, rtn_resp=True)
                                machine, version = machine.split()[0].split('v')
                                version_str = version.replace('.', '')
                                machine = machine.lower()
                                args.b = "{}v{}".format(machine, version_str)
                            dev.disconnect()
                        except Exception as e:
                            print(e)
                            print('Indicate a device platform with -b option')
                            sys.exit()
                    fw_v_dict, fw_v = get_fw_versions(args.b)
                    if not fw_v:
                        print('No firmware available that match: {}'.format(args.b))
                    else:
                        fw_v_opt = []
                        if args.n is not None:
                            print('Firmware versions found for {}-{}:'.format(args.b, args.n))
                            if args.n != 'def':
                                fw_v_opt = [v for v in fw_v if args.n in v]
                                for v in fw_v_opt:
                                    print('- {}'.format(v))
                            else:
                                print('- {}'.format(fw_v[0]))
                        else:
                            print('Firmware versions found for {}:'.format(args.b))
                            for version in fw_v:
                                print('- {}'.format(version))
                        if fw_v_opt:
                            fw_v = fw_v_opt[0]
                        else:
                            fw_v = fw_v[0]
                        print('Firmware selected: {}'.format(fw_v))
                        fw_v_link = fw_v_dict[fw_v]
                        print('Downloading {} ...'.format(fw_v))
                        curl_cmd_str = "curl -O '{}'".format(fw_v_link)
                        curl_cmd = shlex.split(curl_cmd_str)
                        try:
                            proc = subprocess.call(curl_cmd)
                            print('Done!')
                        except KeyboardInterrupt:
                            print('Operation cancelled')

    elif args.m == 'flash':
        devname = kargs.get('device')
        if not args.f:
            print('Firmware file name required, indicate with -f option')
            see_help(args.m)
            sys.exit()
        else:
            dt = check_device_type(args.t)
            if not args.port and dt != 'SerialDevice':
                print(
                    'Indicate a serial port with -port option, {} is NOT a SerialDevice'.format(devname))
                sys.exit()
            else:
                if not args.port:
                    args.port = args.t
                if 'esp32' in args.f:
                    if args.i:
                        print('Checking firmware and device platform match')
                        try:
                            dev = Device(args.t, args.p, init=True, autodetect=True,
                                         ssl=args.wss, auth=args.wss)
                            platform = dev.dev_platform
                            dev.disconnect()
                        except Exception as e:
                            print(e)
                            print('Device not reachable, connect the device and try again.')
                            sys.exit()
                        if platform in args.f:
                            print(
                                'Firmware {} and {} device platform [{}] match, flashing firmware now...'.format(args.f, devname, platform))
                        else:
                            print('Firmware {} and {} device platform [{}] do NOT match, operation aborted.'.format(args.f, devname, platform))
                            sys.exit()
                    print('Flashing firmware {} with esptool.py to {} @ {}...'.format(
                        args.f, devname, args.port))
                    esptool_cmd_str = "esptool.py --chip esp32 --port {} write_flash -z 0x1000 {}".format(
                        args.port, args.f)
                    print(esptool_cmd_str)
                    esptool_cmd = shlex.split(esptool_cmd_str)
                    try:
                        proc = subprocess.call(esptool_cmd)
                        print('Done!')
                    except KeyboardInterrupt:
                        print('Operation cancelled')
                elif 'esp8266' in args.f:
                    if args.i:
                        print('Checking firmware and device platform match')
                        try:
                            dev = Device(args.t, args.p, init=True, autodetect=True,
                                         ssl=args.wss, auth=args.wss)
                            platform = dev.dev_platform
                            dev.disconnect()
                        except Exception as e:
                            print(e)
                            print('Device not reachable, connect the device and try again.')
                            sys.exit()
                        if platform in args.f:
                            print(
                                'Firmware {} and {} device platform [{}] match, flashing firmware now...'.format(args.f, devname, platform))
                        else:
                            print('Firmware {} and {} device platform [{}] do NOT match, operation aborted.'.format(args.f, devname, platform))
                            sys.exit()
                    print('Flashing firmware {} with esptool.py to {} @ {}...'.format(
                        args.f, devname, args.port))
                    esptool_cmd_str = "esptool.py --port {} --baud 460800 write_flash --flash_size=detect 0 {}".format(
                        args.port, args.f)
                    print(esptool_cmd_str)
                    esptool_cmd = shlex.split(esptool_cmd_str)
                    try:
                        proc = subprocess.call(esptool_cmd)
                        print('Done!')
                    except KeyboardInterrupt:
                        print('Operation cancelled')

                elif 'pyb' in args.f:
                    if args.i:
                        print('Checking firmware and device platform match')
                        try:
                            dev = Device(args.t, args.p, init=True, autodetect=True,
                                         ssl=args.wss, auth=args.wss)
                            machine = dev.cmd('import os;os.uname().machine', silent=True,
                                              rtn_resp=True)
                            dev.disconnect()
                        except Exception as e:
                            print(e)
                            print('Device not reachable, connect the device and try again.')
                            sys.exit()
                        platform = dev.dev_platform
                        if platform in args.f or platform[:3] in args.f:
                            machine, version = machine.split()[0].split('v')
                            version_str = version.replace('.', '')
                            machine = machine.lower()
                            fw_string = "{}v{}".format(machine, version_str)

                            if fw_string == args.f.split('-')[0]:
                                print(
                                    'Firmware {} and {} device platform [{}] machine [{}], verison [{}] match, flashing firmware now...'.format(args.f, devname, platform, machine, version))
                            else:
                                print('Firmware {} and {} device platform [{}] machine [{}], verison [{}] do NOT match, operation aborted.'.format(args.f, devname, platform, machine, version))
                                sys.exit()
                        else:
                            print('Firmware {} and {} device platform [{}] do NOT match, operation aborted.'.format(args.f, devname, platform))
                            sys.exit()

                    print('Enabling DFU mode in pyboard, DO NOT DISCONNECT...')
                    dev.connect()
                    bs = dev.serial.write(bytes('import pyb;pyb.bootloader()\r', 'utf-8'))
                    time.sleep(0.2)
                    bin_file = args.f
                    flash_tool = input('Select a tool to flash pydfu.py/dfu-util: (0/1) ')
                    if flash_tool == '0':
                        print('Using pydfu.py...')
                        pydfu_fw_cmd = 'pydfu -u {}'.format(bin_file)
                        # print(upy_fw_cmd)
                        flash_fw_cmd = shlex.split(pydfu_fw_cmd)

                        try:
                            fw_flash = subprocess.call(flash_fw_cmd)
                        except Exception as e:
                            # shr_cp.enable_wrepl_io()
                            print(e)
                        print('Flashing firmware finished successfully!')
                        time.sleep(1)
                        print('Done!')
                    else:
                        print('Using dfu-util...')
                        dfu_fw_cmd = 'sudo dfu-util --alt 0 -D {}'.format(bin_file)
                        # print(upy_fw_cmd)
                        flash_fw_cmd = shlex.split(dfu_fw_cmd)

                        try:
                            fw_flash = subprocess.call(flash_fw_cmd)
                        except Exception as e:
                            # shr_cp.enable_wrepl_io()
                            print(e)
                        print('Flashing firmware finished successfully, RESET the pyboard now.')
                        time.sleep(1)

        sys.exit()
