from upydev.shell.nanoglob import glob as nglob
from upydevice import DeviceNotFound
from upydev.otatool import OTAServer
from upydev.otabletool import OTABleController, dfufy_file
from datetime import datetime, timedelta
import requests
import shlex
import subprocess
import os
import re
import time
import traceback


OFFSET_BOOTLOADER_DEFAULT = 0x1000
OFFSET_APPLICATION_DEFAULT = 0x10000
MICROPYTHON_BIN_OFFSET = OFFSET_APPLICATION_DEFAULT - OFFSET_BOOTLOADER_DEFAULT


def get_fw_versions(keyword):
    fw_list = []
    fw_links = []
    r = requests.get(f'https://micropython.org/download/{keyword}/')
    fw_text = [line for line in r.text.split('\n')
               if keyword in line and any(x in line for x in ['bin', 'dfu', 'zip'])
               and 'firmware' in line]
    if not fw_text:
        keyword = keyword[:3]
        fw_text = [line for line in r.text.split('\n')
                   if keyword in line and any(x in line for x in ['bin', 'dfu', 'zip'])
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


class ShfwIO:
    def __init__(self, dev, dev_name, shell=None):
        self.dev = dev
        self.dev_name = dev_name
        self.shell = shell

    def fwop(self, args, rest_args):
        dev_p = self.dev.wr_cmd('import sys; sys.platform', silent=True, rtn_resp=True)
        self.dev.dev_platform = dev_p
        if not rest_args:  # set list as default
            print('Argument mode required {list, get}')

        else:
            if rest_args[0] == 'list':
                if not args.b:  # Autodetect
                    try:
                        args.b = dev_p
                        if self.dev.dev_platform == 'pyboard':
                            machine = self.dev.wr_cmd('import os;os.uname().machine',
                                                      silent=True, rtn_resp=True)
                            machine, version = machine.split()[0].split('v')
                            version_str = version.replace('.', '')
                            machine = machine.lower()
                            args.b = f"{machine}v{version_str}"

                    except Exception as e:
                        print(e)
                        print('indicate a device platform with -b option')

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
                                    datetime.now()-timedelta(days=days_before),
                                    "%Y%m%d")
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

                                args.b = dev_p
                                if dev_p == 'pyboard':
                                    machine = self.dev.wr_cmd('import '
                                                              'os;os.uname().machine',
                                                              silent=True,
                                                              rtn_resp=True)
                                    machine, version = machine.split()[0].split('v')
                                    version_str = version.replace('.', '')
                                    machine = machine.lower()
                                    args.b = f"{machine}v{version_str}"

                            except Exception as e:
                                print(e)
                                print('indicate a device platform with -b option')

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
                                    datetime.now()-timedelta(days=days_before),
                                    "%Y%m%d")
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
                                curl_cmd_str = f"curl -O '{fw_v_latest_link}'"
                                curl_cmd = shlex.split(curl_cmd_str)
                                try:
                                    subprocess.call(curl_cmd)
                                    print('Done!')
                                except KeyboardInterrupt:
                                    print('Operation Canceled')
                        else:
                            print(f'No firmware available that match: {args.b}')
                    else:
                        fw_v_link = get_fw_versions(args.b)[0][rest_args[1]]
                        print(f'Downloading {rest_args[1]} ...')
                        curl_cmd_str = f"curl -O '{fw_v_link}'"
                        curl_cmd = shlex.split(curl_cmd_str)
                        try:
                            subprocess.call(curl_cmd)
                            print('Done!')
                        except KeyboardInterrupt:
                            print('Operation Canceled')
                else:
                    if not args.b:  # Autodetect
                        try:
                            args.b = self.dev.dev_platform
                            if self.dev.dev_platform == 'pyboard':
                                machine = self.dev.wr_cmd('import os;os.uname().machine',
                                                          silent=True, rtn_resp=True)
                                machine, version = machine.split()[0].split('v')
                                version_str = version.replace('.', '')
                                machine = machine.lower()
                                args.b = f"{machine}v{version_str}"

                        except Exception as e:
                            print(e)
                            print('indicate a device platform with -b option')

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
                            subprocess.call(curl_cmd)
                            print('Done!')
                        except KeyboardInterrupt:
                            print('Operation Canceled')

    def flash(self, args, rest_args):
        dev_p = self.dev.wr_cmd('import sys; sys.platform', silent=True, rtn_resp=True)
        self.dev.dev_platform = dev_p
        devname = self.dev_name
        if not rest_args:
            print('Firmware file name required')
            return
        else:
            if 'esp32' in dev_p:
                if args.i:
                    print('Checking firmware and device platform match')
                    if not self.dev.dev_platform:
                        dev_p = self.dev.wr_cmd('import sys; sys.platform',
                                                silent=True, rtn_resp=True)
                    self.dev.dev_platform = dev_p
                    if self.dev.dev_platform in rest_args:
                        print(f'Firmware {rest_args} and {self.dev_name} '
                              f'device platform [{self.dev.dev_platform}] '
                              'match, flashing firmware now...')
                    else:
                        print(f'Firmware {rest_args} and {self.dev_name} '
                              f'device platform [{dev_p}] do NOT match, operation'
                              ' aborted.')
                        return
                print(f'Flashing firmware {rest_args} '
                      f'with esptool.py to {self.dev_name} @ {self.dev.serial_port}...')
                esptool_cmd_str = ("esptool.py --chip esp32 "
                                   f"--port {self.dev.serial_port} write_flash "
                                   f"-z 0x1000 {rest_args}")
                print(esptool_cmd_str)
                esptool_cmd = shlex.split(esptool_cmd_str)
                try:
                    subprocess.call(esptool_cmd)
                    print('Done!')
                except KeyboardInterrupt:
                    print('Operation Canceled')
            elif 'esp8266' in dev_p:
                if args.i:
                    print('Checking firmware and device platform match')
                    if not self.dev.dev_platform:
                        dev_p = self.dev.wr_cmd('import sys; sys.platform',
                                                silent=True, rtn_resp=True)
                    self.dev.dev_platform = dev_p

                    if self.dev.dev_platform in rest_args:
                        print(f'Firmware {rest_args} and {self.dev_name} '
                              f'device platform [{self.dev.dev_platform}] '
                              'match, flashing firmware now...')
                    else:
                        print(f'Firmware {rest_args} and {self.dev_name} '
                              f'device platform [{dev_p}] do NOT match, operation'
                              ' aborted.')
                        return
                print(f'Flashing firmware {rest_args} '
                      f'with esptool.py to {self.dev_name} @ {self.dev.serial_port}...')
                esptool_cmd_str = (f"esptool.py --port {self.dev.serial_port} "
                                   f"--baud 460800 write_flash "
                                   f"--flash_size=detect 0 {rest_args}")
                print(esptool_cmd_str)
                esptool_cmd = shlex.split(esptool_cmd_str)
                try:
                    subprocess.call(esptool_cmd)
                    print('Done!')
                except KeyboardInterrupt:
                    print('Operation Canceled')

            elif 'pyb' in dev_p:
                if args.i:
                    print('Checking firmware and device platform match')
                    try:
                        machine = self.dev.wr_cmd('import os;os.uname().machine',
                                                  silent=True,
                                                  rtn_resp=True)
                    except Exception as e:
                        print(e)
                        return
                    if not self.dev.dev_platform:
                        dev_p = self.dev.wr_cmd('import sys; sys.platform',
                                                silent=True, rtn_resp=True)
                    self.dev.dev_platform = dev_p
                    platform = dev_p
                    if platform in rest_args or platform[:3] in rest_args:
                        machine, version = machine.split()[0].split('v')
                        version_str = version.replace('.', '')
                        machine = machine.lower()
                        fw_string = f"{machine}v{version_str}"

                        if fw_string == rest_args.split('-')[0]:
                            print(f'Firmware {rest_args} and {devname} device platform '
                                  f'[{platform}] machine [{machine}], '
                                  f'verison [{version}] match, '
                                  'flashing firmware now...')
                        else:
                            print(f'Firmware {rest_args} and {devname} device platform '
                                  f'[{platform}] machine [{machine}], '
                                  f'verison [{version}] do NOT match, '
                                  'operation aborted.')
                            return
                    else:
                        print(f'Firmware {rest_args} and {devname} device platform '
                              f'[{platform}] do NOT match, '
                              'operation aborted.')
                        return

                print('Enabling DFU mode in pyboard, DO NOT DISCONNECT...')
                # dev.connect()
                self.dev.serial.write(bytes('import pyb;pyb.bootloader()\r', 'utf-8'))
                time.sleep(0.2)
                bin_file = rest_args
                flash_tool = input('Select a tool to flash pydfu.py/dfu-util: (0/1) ')
                if flash_tool == '0':
                    print('Using pydfu.py...')
                    pydfu_fw_cmd = f'pydfu -u {bin_file}'
                    # print(upy_fw_cmd)
                    flash_fw_cmd = shlex.split(pydfu_fw_cmd)

                    try:
                        subprocess.call(flash_fw_cmd)
                    except Exception as e:
                        # shr_cp.enable_wrepl_io()
                        print(e)
                    print('Flashing firmware finished successfully!')
                    time.sleep(1)
                    print('Done!')
                    self.dev.disconnect()
                    self.dev.connect()
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
                          'rebooting the pyboard now.')
                    time.sleep(1)
                    self.dev.disconnect()
                    self.dev.connect()
                    self.dev.reset()

    # MPYX

    def mpycross(self, args, rest_args):
        rest_args = nglob(*rest_args)
        for file in rest_args:
            print('Frozing {} to bytecode with mpy-cross'.format(file))
            mpy_cmd_str = 'mpy-cross {}'.format(file)
            mpy_cmd = shlex.split(mpy_cmd_str)
            try:
                mpy_tool = subprocess.call(mpy_cmd)
                if mpy_tool == 0:
                    print('Process successful, bytecode in : {}'.format(
                                            file.replace('py', 'mpy')))
                else:
                    print('Process failed.')
            except KeyboardInterrupt:
                pass

    # OTA

    def ota(self, args, fwfile):

        if self.dev.dev_class not in ['WebSocketDevice', 'BleDevice']:
            print(f'OTA not available, {self.dev_name} is NOT a OTA capable device')
            return

        if 'esp32' in fwfile:
            # Extract micropython.bin from firmware.bin
            with open(fwfile, 'rb') as fw:
                fw.read(MICROPYTHON_BIN_OFFSET)
                app = fw.read()
            with open(f"ota-{fwfile}", 'wb') as fw_app:
                fw_app.write(app)

            fwfile = f"ota-{fwfile}"
            if args.i:
                if not self.dev.dev_platform:
                    dev_p = self.dev.wr_cmd('import sys; sys.platform',
                                            silent=True, rtn_resp=True)
                    self.dev.dev_platform = dev_p
                if self.dev.dev_platform in fwfile:
                    print(f'Firmware {fwfile} and {self.dev_name} device platform '
                          f'[{self.dev.dev_platform}] match, starting OTA now...')
                else:
                    print(f'Firmware {fwfile} and {self.dev_name} device platform '
                          f'[{self.dev.dev_platform}] do NOT match, '
                          'operation aborted.')
                    return

            if self.dev.dev_class == 'WebSocketDevice':

                OTA_server = OTAServer(self.dev, port=8014, firmware=fwfile,
                                       tls=args.sec, zt=args.zt)
                OTA_server.start_ota()
                time.sleep(1)
                self.dev.cmd_nb('import machine;machine.reset()', block_dev=False)
                time.sleep(2)
                self.dev.disconnect()
                time.sleep(1)
                while not self.dev.connected:
                    try:
                        self.dev.connect()
                    except Exception as e:
                        print(e)
                        time.sleep(1)
                        print('Trying to reconnect again...')
                    except KeyboardInterrupt:
                        return
                os.remove(fwfile)
                self.dev.wr_cmd("import gc;from upysh import *", silent=True)
                print('Done!')
            elif self.dev.dev_class == 'BleDevice':
                # Enable dfu mode
                print('ota: enabling DFU Mode...')
                self.dev.wr_cmd("set_ble_flag('DFU')")
                self.dev.reset(hr=True, reconnect=False)
                local_name = self.dev.name
                # self.dev.disconnect()
                print('ota: checking if DFU Mode is available...')
                time.sleep(2)
                dev = OTABleController(self.dev.address, init=True, packet_size=512,
                                       debug=False)
                if dev.connected:
                    # ASSERT DFU MODE
                    try:
                        assert 'Device Firmware Update Service' in dev.services_rsum, (
                               'DFU Mode not available')
                        fwu_services = dev.services_rsum['Device Firmware '
                                                         'Update Service']
                        assert 'DFU Control Point' in fwu_services, ('Missing DFU '
                                                                     'Control Point')
                        assert 'DFU Packet' in fwu_services, 'Missing DFU Packet'
                        print('ota: DFU Mode available, starting ota firmware flashing')
                        if fwfile:
                            assert fwfile.endswith(
                                '.bin'), 'Incorrect file format, create the proper file'
                            ota_file = dfufy_file(fwfile)
                            dev.do_dfu(ota_file)
                            os.remove(ota_file)
                    except Exception as e:
                        print(f'ota: operation failed, reason: {e}')
                        show_tb = input('Do you want to see full traceback?[y/n]')
                        if show_tb == 'y':
                            print(traceback.format_exc())
                        print('ota: trying to reconnect now ...')
                if dev.connected:
                    dev.disconnect()
                time.sleep(5)
                print(f'ota: waiting for {self.dev_name} to be available again...')
                while True:
                    try:
                        if not self.dev.is_connected():
                            self.dev.connect(show_servs=False)
                            if self.dev.name.endswith('-DFU'):
                                self.dev.name = local_name
                            break
                    except DeviceNotFound:
                        time.sleep(1)
                        print(f'ota: waiting for {self.dev_name} to '
                              'be available again...')
                time.sleep(1)
                self.dev.wr_cmd('import gc;from upysh import *', silent=True)
                print('Done!')
