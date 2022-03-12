from upydevice import Device
import sys
from upydev.otatool import OTAServer
from upydev.otabletool import OTABleController, dfufy_file
from upydevice import check_device_type
import os
from datetime import datetime, timedelta
import requests
import shlex
import subprocess
import upydev
import re
import time
import argparse
rawfmt = argparse.RawTextHelpFormatter


arg_options = ['t', 'p', 'wss', 'b', 'n', 'f', 'fre']
dict_arg_options = {'mpyx': ['f', 'fre'],
                    'fwr': ['t', 'p', 'wss', 'b', 'n', 'md'],
                    'flash': ['t', 'p', 'f', 'i'],
                    'ota': ['t', 'p', 'wss', 'f', 'sec', 'i']}

MPYX = dict(help="freeze .py files using mpy-cross. (must be available in $PATH)",
            subcmd=dict(help='indicate a file/pattern to '
                             'compile',
                        default=[],
                        metavar='file/pattern',
                        nargs='+'),
            options={})

FW = dict(help="list or get available firmware from micropython.org",
          subcmd=dict(help=('{list, get, update}'
                            '; default: list'),
                      default=['list'],
                      metavar='action', nargs='*'),
          options={"-b": dict(help='to indicate device platform',
                              required=False),
                   "-n": dict(help='to indicate keyword for filter search',
                              required=False),
                   "-t": dict(help="device target address",
                              required=True),
                   "-p": dict(help='device password or baudrate',
                              required=True),
                   "-wss": dict(help='use WebSocket Secure',
                                required=False,
                                default=False,
                                action='store_true')},
          alt_ops=['list', 'get', 'update', 'latest'])

FLASH = dict(help="to flash a firmware file using available serial tools "
             "(esptool.py, pydfu.py)",
             subcmd=dict(help=('indicate a firmware file to flash'),
                         metavar='firmware file'),
             options={"-i": dict(help='to check wether device platform and '
                                 'firmware file name match',
                                 required=False,
                                 action='store_true'),
                      "-t": dict(help="device target address",
                                 required=True),
                      "-p": dict(help='device baudrate',
                                 required=True),
                      })

OTA = dict(help="to flash a firmware file using OTA system (ota.py, otable.py)",
           subcmd=dict(help=('indicate a firmware file to flash'),
                       metavar='firmware file'),
           options={"-i": dict(help='to check wether device platform and '
                               'firmware file name match',
                               required=False,
                               action='store_true'),
                    "-sec": dict(help='to enable OTA TLS',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-zt": dict(help='zerotierone host IP',
                                required=False,
                                default=False)})


FW_CMD_DICT_PARSER = {"mpyx": MPYX, "fwr": FW, "flash": FLASH, "ota": OTA}


usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('firmware tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in FW_CMD_DICT_PARSER.items():
    _subparser = subparser_cmd.add_parser(command, help=subcmd['help'],
                                          description=subcmd['help'])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)

UPYDEV_PATH = upydev.__path__[0]


def parseap(command_args):
    try:
        return parser.parse_known_args(command_args)
    except SystemExit:  # argparse throws these because it assumes you only want
        # to do the command line
        return None  # should be a default one


def sh_cmd(cmd_inp):
    # parse args
    command_line = shlex.split(cmd_inp)

    all_args = parseap(command_line)

    if not all_args:
        return
    else:
        args, unknown_args = all_args

    return args, unknown_args


def filter_bool_opt(k, v):
    if v and isinstance(v, bool):
        return f"{k}"
    else:
        return ""


def expand_margs(v):
    if isinstance(v, list):
        return ' '.join(v)
    else:
        return v


def get_fw_versions(keyword):
    fw_list = []
    fw_links = []
    r = requests.get(f'https://micropython.org/download/{keyword}/')
    fw_text = [line for line in r.text.split('\n') if keyword in line
               and any(x in line for x in ['bin', 'dfu', 'zip']) and 'firmware' in line]
    if not fw_text:
        keyword = keyword[:3]
        fw_text = [line for line in r.text.split('\n') if keyword in line
                   and any(x in line for x in ['bin', 'dfu', 'zip'])
                   and 'firmware' in line]
    for line in fw_text:
        for element in re.split(r"[=<>]+", line):
            if 'firmware' in element:
                fw_links.append('www.micropython.org{}'.format(element[1:-1]))
                fw_list.append(element[1:-1].split('/')[3])
    if not fw_text:
        keyword = keyword[:3]
    fw_dict = dict(zip(fw_list, fw_links))
    return fw_dict, fw_list


def firmwaretools_action(args, unkwargs, **kargs):
    # dev_name = kargs.get('device')
    # get top args and make command line filtering
    args_dict = {f"-{k}": v for k, v in vars(args).items()
                 if k in dict_arg_options[args.m]}
    args_list = [f"{k} {expand_margs(v)}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    cmd_inp = f"{args.m} {' '.join(unkwargs)} {' '.join(args_list)}"
    # print(cmd_inp)
    # sys.exit()
    # debug command:
    if cmd_inp.startswith('!'):
        args = parseap(shlex.split(cmd_inp[1:]))
        print(args)
        return
    if '-h' in unkwargs:
        sh_cmd(f"{args.m} -h")
        sys.exit()

    result = sh_cmd(cmd_inp)
    if not result:
        sys.exit()
    else:
        args, unknown_args = result
    if hasattr(args, 'subcmd'):
        command, rest_args = args.m, args.subcmd
        if rest_args is None:
            rest_args = []
    else:
        command, rest_args = args.m, []
    # MPYX
    # print(f"{command}: {args} {rest_args} {unknown_args}")
    if command == 'mpyx':
        if rest_args:
            for frfile in rest_args:
                if frfile not in os.listdir():
                    print('File not found, indicate a valid file')
                else:
                    print(f'Frozing {frfile} to bytecode with mpy-cross')
                    mpy_cmd_str = f'mpy-cross {frfile}'
                    mpy_cmd = shlex.split(mpy_cmd_str)
                    try:
                        mpy_tool = subprocess.call(mpy_cmd)
                        if mpy_tool == 0:
                            print(f"Process successful, bytecode in : "
                                  f"{frfile.replace('py', 'mpy')}")
                        else:
                            print('Process failed.')
                    except KeyboardInterrupt:
                        pass

        sys.exit()

    # FW
    elif command == 'fwr':

        if rest_args[0] == 'list':
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
                        args.b = f"{machine}v{version_str}"
                    dev.disconnect()
                except Exception as e:
                    print(e)
                    print('indicate a device platform with -b option')
                    sys.exit()
            if len(rest_args) > 1:
                if rest_args[1] == 'latest':
                    today = datetime.strftime(datetime.now(), "%Y%m%d")
                    fw_v = get_fw_versions(args.b)
                    if fw_v[1]:
                        print(f'Latest Firmware versions found for {args.b}:')
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
                                    print(f'- {v}')
                            else:
                                print(f'- {fw_v_latest[0]}')
                        else:
                            for v in fw_v_latest:
                                print(f'- {v}')
                    else:
                        print(f'No firmware available that match: {args.b}')
                    # fw_v_latest_link = fw_v[0][fw_v_latest]

            else:
                fw_v = get_fw_versions(args.b)[1]
                if not fw_v:
                    print(f'No firmware available that match: {args.b}')
                else:
                    if args.n is not None:
                        print(f'Firmware versions found for {args.b}-{args.n}:')
                        if args.n != 'def':
                            fw_v_opt = [v for v in fw_v if args.n in v]
                            for v in fw_v_opt:
                                print(f'- {v}')
                        else:
                            print(f'- {fw_v[0]}')
                    else:
                        print(f'Firmware versions found for {args.b}:')
                        for version in fw_v:
                            print(f'- {version}')
        elif rest_args[0] == 'get':
            if len(rest_args) > 1:
                if rest_args[1] == 'latest':
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
                                args.b = f"{machine}v{version_str}"
                            dev.disconnect()
                        except Exception as e:
                            print(e)
                            print('indicate a device platform with -b option')
                            sys.exit()
                    today = datetime.strftime(datetime.now(), "%Y%m%d")
                    fw_v = get_fw_versions(args.b)

                    if fw_v[1]:
                        print(f'Latest version found for {args.b}:')
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
                                    print(f'- {v}')
                        else:
                            print(f'- {fw_v_latest[0]}')
                        if len(fw_v_latest) >= 1:
                            fw_v_latest = fw_v_latest[0]
                            print(f'Firmware selected: {fw_v_latest}')
                            fw_v_latest_link = fw_v[0][fw_v_latest]
                            print(f'Downloading {fw_v_latest} ...')
                            curl_cmd_str = "curl -O '{}'".format(fw_v_latest_link)
                            curl_cmd = shlex.split(curl_cmd_str)
                            try:
                                proc = subprocess.call(curl_cmd)
                                print('Done!')
                            except KeyboardInterrupt:
                                print('Operation Canceled')
                    else:
                        print(f'No firmware available that match: {args.b}')
                else:
                    fw_v_link = get_fw_versions(rest_args[1])[0][rest_args[1]]
                    print(f'Downloading {rest_args[1]} ...')
                    curl_cmd_str = f"curl -O '{fw_v_link}'"
                    curl_cmd = shlex.split(curl_cmd_str)
                    try:
                        proc = subprocess.call(curl_cmd)
                        print('Done!')
                    except KeyboardInterrupt:
                        print('Operation Canceled')
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
                            args.b = f"{machine}v{version_str}"
                        dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('indicate a device platform with -b option')
                        sys.exit()
                fw_v_dict, fw_v = get_fw_versions(args.b)
                if not fw_v:
                    print(f'No firmware available that match: {args.b}')
                else:
                    fw_v_opt = []
                    if args.n is not None:
                        print(f'Firmware versions found for {args.b}-{args.n}:')
                        if args.n != 'def':
                            fw_v_opt = [v for v in fw_v if args.n in v]
                            for v in fw_v_opt:
                                print(f'- {v}')
                        else:
                            print(f'- {fw_v[0]}')
                    else:
                        print(f'Firmware versions found for {args.b}:')
                        for version in fw_v:
                            print(f'- {version}')
                    if fw_v_opt:
                        fw_v = fw_v_opt[0]
                    else:
                        fw_v = fw_v[0]
                    print(f'Firmware selected: {fw_v}')
                    fw_v_link = fw_v_dict[fw_v]
                    print(f'Downloading {fw_v} ...')
                    curl_cmd_str = f"curl -O '{fw_v_link}'"
                    curl_cmd = shlex.split(curl_cmd_str)
                    try:
                        proc = subprocess.call(curl_cmd)
                        print('Done!')
                    except KeyboardInterrupt:
                        print('Operation Canceled')

    elif command == 'flash':
        devname = kargs.get('device')
        fwfile = rest_args
        dt = check_device_type(args.t)
        if dt != 'SerialDevice':
            print(f'indicate a serial port with -t option, {devname} is NOT a '
                  'SerialDevice')
            sys.exit()
        else:
            if 'esp32' in fwfile:
                if args.i:
                    print('Checking firmware and device platform match')
                    try:
                        dev = Device(args.t, args.p, init=True, autodetect=True)
                        platform = dev.dev_platform
                        dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Device not reachable, connect the device and try again.')
                        sys.exit()
                    if platform in fwfile:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] match, flashing firmware now...')
                    else:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] do NOT match, operation aborted.')
                        sys.exit()
                print(f'Flashing firmware {fwfile} with esptool.py '
                      f'to {devname} @ {args.t}...')
                esptool_cmd_str = (f"esptool.py --chip esp32 --port {args.t} "
                                   f"write_flash -z 0x1000 {fwfile}")
                print(esptool_cmd_str)
                esptool_cmd = shlex.split(esptool_cmd_str)
                try:
                    proc = subprocess.call(esptool_cmd)
                    print('Done!')
                except KeyboardInterrupt:
                    print('Operation Canceled')
            elif 'esp8266' in fwfile:
                if args.i:
                    print('Checking firmware and device platform match')
                    try:
                        dev = Device(args.t, args.p, init=True, autodetect=True)
                        platform = dev.dev_platform
                        dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Device not reachable, connect the device and try again.')
                        sys.exit()
                    if platform in fwfile:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] match, flashing firmware now...')
                    else:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] do NOT match, operation aborted.')
                        sys.exit()
                print(f'Flashing firmware {fwfile} with esptool.py '
                      f'to {devname} @ {args.t}...')
                esptool_cmd_str = (f"esptool.py --port {args.t} --baud 460800 "
                                   f"write_flash --flash_size=detect 0 {fwfile}")
                print(esptool_cmd_str)
                esptool_cmd = shlex.split(esptool_cmd_str)
                try:
                    subprocess.call(esptool_cmd)
                    print('Done!')
                except KeyboardInterrupt:
                    print('Operation Canceled')

            elif 'pyb' in fwfile:
                dev = Device(args.t, args.p, init=True, autodetect=True)
                if args.i:
                    print('Checking firmware and device platform match')
                    try:
                        machine = dev.cmd('import os;os.uname().machine', silent=True,
                                          rtn_resp=True)
                        dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Device not reachable, connect the device and try again.')
                        sys.exit()
                    platform = dev.dev_platform
                    if platform in fwfile or platform[:3] in fwfile:
                        machine, version = machine.split()[0].split('v')
                        version_str = version.replace('.', '')
                        machine = machine.lower()
                        fw_string = f"{machine}v{version_str}"

                        if fw_string == fwfile.split('-')[0]:
                            print(f'Firmware {fwfile} and {devname} device platform '
                                  f'[{platform}] machine [{machine}], '
                                  f'verison [{version}] match, '
                                  'flashing firmware now...')
                        else:
                            print(f'Firmware {fwfile} and {devname} device platform '
                                  f'[{platform}] machine [{machine}], '
                                  f'verison [{version}] do NOT match, '
                                  'operation aborted.')
                            sys.exit()
                    else:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] do NOT match, operation aborted.')
                        sys.exit()

                print('Enabling DFU mode in pyboard, DO NOT DISCONNECT...')
                dev.connect()
                dev.serial.write(bytes('import pyb;pyb.bootloader()\r', 'utf-8'))
                time.sleep(0.2)
                bin_file = fwfile
                flash_tool = input('Select a tool to flash pydfu.py/dfu-util: (0/1) ')
                if flash_tool == '0':
                    print('Using pydfu.py...')
                    pydfu_fw_cmd = f'pydfu -u {bin_file}'
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
                    dfu_fw_cmd = f'sudo dfu-util --alt 0 -D {bin_file}'
                    # print(upy_fw_cmd)
                    flash_fw_cmd = shlex.split(dfu_fw_cmd)

                    try:
                        subprocess.call(flash_fw_cmd)
                    except Exception as e:
                        # shr_cp.enable_wrepl_io()
                        print(e)
                    print('Flashing firmware finished successfully, '
                          'RESET the pyboard now.')
                    time.sleep(1)

        sys.exit()

    elif command == 'ota':
        OFFSET_BOOTLOADER_DEFAULT = 0x1000
        OFFSET_APPLICATION_DEFAULT = 0x10000
        MICROPYTHON_BIN_OFFSET = OFFSET_APPLICATION_DEFAULT - OFFSET_BOOTLOADER_DEFAULT
        devname = kargs.get('device')
        fwfile = rest_args

        dt = check_device_type(args.t)
        if dt not in ['WebSocketDevice', 'BleDevice']:
            print(f'OTA not available, {devname} is NOT a OTA capable device')
            sys.exit()

        if 'esp32' in fwfile:
            dev = None
            # Extract micropython.bin from firmware.bin
            with open(fwfile, 'rb') as fw:
                offset = fw.read(MICROPYTHON_BIN_OFFSET)
                app = fw.read()
            with open(f"ota-{fwfile}", 'wb') as fw_app:
                fw_app.write(app)

            fwfile = f"ota-{fwfile}"

            if dt == 'WebSocketDevice':
                if args.i:
                    print('Checking firmware and device platform match')
                    try:
                        dev = Device(args.t, args.p, init=True, autodetect=True,
                                     ssl=args.wss, auth=args.wss)
                        platform = dev.dev_platform
                        # dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Device not reachable, connect the device and try again.')
                        sys.exit()
                    if platform in fwfile:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] match, starting OTA now...')
                    else:
                        print(f'Firmware {fwfile} and {devname} device platform '
                              f'[{platform}] do NOT match, operation aborted.')
                        sys.exit()
                if not dev:
                    try:
                        dev = Device(args.t, args.p, init=True, autodetect=True,
                                     ssl=args.wss, auth=args.wss)
                        platform = dev.dev_platform
                        # dev.disconnect()
                    except Exception as e:
                        print(e)
                        print('Device not reachable, connect the device and try again.')
                        sys.exit()
                OTA_server = OTAServer(
                    dev, port=8014, firmware=fwfile, tls=args.sec, zt=args.zt)
                OTA_server.start_ota()
                # print('Rebooting device...')
                time.sleep(1)
                dev.cmd_nb('import machine;machine.reset()', block_dev=False)
                time.sleep(2)
                dev.disconnect()
                os.remove(fwfile)
                # print('Done!')
            elif dt == 'BleDevice':

                dev = OTABleController(args.t, init=True, packet_size=512,
                                       debug=False)
                if dev.connected:
                    # ASSERT DFU MODE
                    _dmna = 'DFU Mode not available'
                    assert 'Device Firmware Update Service' in dev.services_rsum, _dmna
                    assert 'DFU Control Point' in dev.services_rsum[
                        'Device Firmware Update Service'], 'Missing DFU Control Point'
                    assert 'DFU Packet' in dev.services_rsum[
                           'Device Firmware Update Service'], 'Missing DFU Packet'
                    if fwfile:
                        assert fwfile.endswith(
                            '.bin'), 'Incorrect file format, create the proper file'
                        ota_file = dfufy_file(fwfile)
                        dev.do_dfu(ota_file)
                        os.remove(ota_file)

        sys.exit()
