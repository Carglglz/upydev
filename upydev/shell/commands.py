import os
import argparse
import shlex
from upydev import name as uname, version as uversion
from upydev.shell.constants import (AUTHMODE_DICT,
                                    shell_commands, custom_sh_cmd_kw, shell_message)
from upydev.shell.common import (du, _ft_datetime, SHELL_ALIASES, ls, FileArgs)
from upydev.shell.parser import shparser
from binascii import hexlify
from upydev.commandlib import _CMDDICT_
from upydev import upip_host
from upydevice import DeviceException
from braceexpand import braceexpand
import ast
from datetime import datetime, date
import signal
import subprocess
import webbrowser

# SHELL COMMAND PARSER
rawfmt = argparse.RawTextHelpFormatter

_SHELL_CMDS = custom_sh_cmd_kw + shell_commands

_LOCAL_SHELL_CMDS = ['ldu', 'lsl', 'lpwd', 'lcd']

_SPECIAL_SHELL_CMDS = ['wrepl', 'jupyterc', 'get', 'put', 'fget'
                       'fw', 'flash', 'dsync',
                       'srepl', 'pytest', 'getcert', 'git', 'update_upyutils',
                       'uping', 'upy-config', 'wss', 'exit']


class ShellFlags:
    def __init__(self):
        self.mem_show_rp = {'show': False, 'call': False, 'used': '?',
                            'free': '?', 'percent': 0}
        self.dev_path = {'p': ' '}
        self.local_path = {'p': ''}
        self.show_local_path = {'s': False}
        # self.status_encryp_msg = {'S': False, 'Toggle': True}
        self.exit = {'exit': False}
        # encrypted_flag = {'sec': True}
        self.prompt = {'p': '>>> '}
        self.paste = {'p': False}
        self.paste_buffer = {'B': []}
        self.reset = {'R': False}
        self.autosuggest = {'A': False}
        self.shell_mode = {'S': False}
        self.frozen_modules = {'FM': [], 'SUB': []}
        self.edit_mode = {'E': False, 'File': ''}
        self.shell_mode_run = {'R': False}
        self.script_is_running = {'R': False, 'script': 'test_code'}
        self.shell_prompt = {'s': shell_message}


_SHELL_FLAGS = ShellFlags()


class ShellCmds:
    def __init__(self, dev, flags=_SHELL_FLAGS, topargs=None):
        self.dev = dev
        self.flags = flags
        self.topargs = topargs
        # Setup shell commands parser
        self.parser = shparser

    def print_filesys_info(self, filesize):
        _kB = 1000
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f kB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)
        return sizestr

    def brace_exp(self, explist):
        files_to_create = []
        for file_or_bexp in explist:
            if '{' in file_or_bexp and '}' in file_or_bexp:
                files_to_create += list(braceexpand(file_or_bexp))
            else:
                files_to_create.append(file_or_bexp)
        return files_to_create

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        return

    def escape_sh_cmd(self, cmd_inp):
        # SHELL ESCAPE:
        if cmd_inp.startswith('%') or cmd_inp.split()[0] not in _SHELL_CMDS + ['-h']:
            if cmd_inp.split()[0] != 'ping':
                try:
                    if cmd_inp.startswith('%'):
                        cmd_inp = cmd_inp[1:]
                    shell_cmd_str = shlex.split(cmd_inp)
                    if shell_cmd_str[0] in SHELL_ALIASES:
                        shell_cmd_str = SHELL_ALIASES[shell_cmd_str[0]
                                                      ].split() + shell_cmd_str[1:]
                    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

                    def preexec_function(action=old_action):
                        signal.signal(signal.SIGINT, action)
                    try:
                        subprocess.call(shell_cmd_str, preexec_fn=preexec_function)
                        signal.signal(signal.SIGINT, old_action)
                    except Exception as e:
                        print(e)
                except Exception as e:
                    print(e)
                    pass
            else:
                try:  # TODO fix for zt
                    if len(cmd_inp.split()) > 1:
                        ping_cmd = shlex.split(cmd_inp)
                    elif hasattr(self.dev, 'ip'):
                        if self.dev.hostname.endswith('.local'):
                            ping_dir = self.dev.hostname
                        else:
                            ping_dir = self.dev.ip
                        ping_cmd_str = 'ping {}'.format(ping_dir)
                        ping_cmd = shlex.split(ping_cmd_str)

                    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

                    def preexec_function(action=old_action):
                        signal.signal(signal.SIGINT, action)
                    try:
                        subprocess.call(ping_cmd, preexec_fn=preexec_function)
                        signal.signal(signal.SIGINT, old_action)
                    except Exception as e:
                        print(e)
                except Exception:
                    print("Indicate a host to ping, e.g google.com")

            return True

    def send_cmd(self, cmd, capture_output=False, sh_silent=True,
                 collect=False, follow=False, raise_devexcept=False):
        if not capture_output:
            self.dev.wr_cmd(cmd, silent=sh_silent, follow=follow)
        else:
            self.dev.wr_cmd(cmd, silent=sh_silent, long_string=True, follow=follow)

        if raise_devexcept:
            if self.dev._traceback.decode() in self.dev.response:
                try:
                    raise DeviceException(self.dev.response)
                except Exception as e:
                    print(e)
        return self.dev.output

    def parseap(self, command_args):
        try:
            return self.parser.parse_known_args(command_args)[0]
        except SystemExit:  # argparse throws these because it assumes you only want
            # to do the command line
            return None  # should be a default one

    def cmd(self, cmdline):
        try:
            self.sh_cmd(cmdline)
        except KeyboardInterrupt as e:
            print(e)

    def sh_cmd(self, cmd_inp):

        # SHELL ESCAPE:
        if self.escape_sh_cmd(cmd_inp):
            return

        # PARSE ARGS
        command_line = shlex.split(cmd_inp)
        args = self.parseap(command_line)
        if not args:
            return
        if hasattr(args, 'subcmd'):
            command, rest_args = args.m, args.subcmd
        else:
            command, rest_args = args.m, []

        # LOCAL COMMANDS
        if command in _LOCAL_SHELL_CMDS:
            self.local_sh_cmds(command, args, rest_args)
            return

        # INFO :
        if command == 'info':
            try:
                print(self.dev)
            except Exception as e:
                print(e)
            return

        # ID:
        if command == 'id':
            uid = self.send_cmd(_CMDDICT_['UID'], raise_devexcept=True)
            print('ID: {}'.format(uid.decode()))
            return

        # UHELP:

        if command == 'uhelp':
            self.send_cmd(_CMDDICT_['HELP'], sh_silent=False, follow=True)
            return

        # UMODULES

        if command == 'modules':
            self.send_cmd(_CMDDICT_['MOD'], sh_silent=False, follow=True)
            return

        # MEM_INFO

        if command == 'mem':
            if rest_args == 'info':
                RAM = self.send_cmd(_CMDDICT_['MEM'], raise_devexcept=True,
                                    capture_output=True)

                mem_info = RAM.splitlines()[1]
                mem = {elem.strip().split(':')[0]: int(elem.strip().split(':')[
                                  1]) for elem in mem_info[4:].split(',')}
                print(f"{'Memory':12}{'Size':^12}{'Used':^12}{'Avail':^12}{'Use%':^12}")
                total_mem = mem['total']/1000
                used_mem = mem['used']/1000
                free_mem = mem['free']/1000
                total_mem_s = f"{total_mem:.3f} kB"
                used_mem_s = f"{used_mem:.3f} kB"
                free_mem_s = f"{free_mem:.3f} kB"
                percent_mem = f"{(used_mem/total_mem)*100:.1f} %"

                print(f"{'RAM':12}{total_mem_s:^12}{used_mem_s:^12}{free_mem_s:^12}"
                      f"{percent_mem:>8}")
            else:
                if rest_args == 'dump':
                    self.send_cmd('from micropython import mem_info;'
                                  'mem_info(1)', sh_silent=False, follow=True)

            return
        # DISPLAY FREE DISK SPACE
        if command == 'df':
            resp = self.send_cmd("os.statvfs('')")
            size_info = resp
            total_b = size_info[0] * size_info[2]
            used_b = (size_info[0] * size_info[2]) - (size_info[0] * size_info[3])
            total_mem = self.print_filesys_info(total_b)
            free_mem = self.print_filesys_info(size_info[0] * size_info[3])
            used_mem = self.print_filesys_info(used_b)
            percent_used = (used_b / total_b) * 100
            print(f"{'Filesystem':12}{'Size':^12}{'Used':^12}{'Avail':^12}{'Use%':^12}"
                  f"{'Mounted on':^12}")
            print(f"{'Flash':12}{total_mem:^12}{used_mem:^12}{free_mem:^12}"
                  f"{percent_used:>8.1f}{' ':>5}{'/':12}")

            vfs_resp = self.send_cmd(
                "{dir:os.statvfs(dir) for dir in os.listdir() if os.stat(dir)[0] "
                "& 0x4000 and os.statvfs('') != os.statvfs(dir)}")
            for vfs in vfs_resp.keys():
                if vfs_resp[vfs] != resp:
                    size_info_sd = vfs_resp[vfs]
                    total_b_sd = size_info_sd[0] * size_info_sd[2]
                    used_b_sd = (size_info_sd[0] * size_info_sd[2]) - \
                                (size_info_sd[0] * size_info_sd[3])
                    total_mem_sd = self.print_filesys_info(total_b_sd)
                    free_mem_sd = self.print_filesys_info(size_info_sd[0]
                                                          * size_info_sd[3])
                    used_mem_sd = self.print_filesys_info(used_b_sd)
                    percent_used_sd = (used_b_sd / total_b_sd) * 100
                    mounted = f'/{vfs}'
                    print(f"{vfs:12}{total_mem_sd:^12}{used_mem_sd:^12}"
                          f"{free_mem_sd:^12}"
                          f"{percent_used_sd:>8.1f}{' ':>5}{mounted:12}")
            return

        # DISK USAGE STATISTICS
        if command == 'du':
            if not rest_args:
                self.send_cmd(f'from upysh2 import du;'
                              f'du(max_dlev={args.d});gc.collect()',
                              sh_silent=False, follow=True)

            else:
                du_dir = rest_args
                self.send_cmd(f"from upysh2 import du;du(path='./{du_dir}',"
                              f"max_dlev={args.d});gc.collect()",
                              sh_silent=False, follow=True)
            return

        # TREE
        if command == 'tree':
            if not rest_args:
                self.send_cmd('from upysh2 import tree;'
                              f'tree(hidden={args.a});gc.collect()',
                              sh_silent=False, follow=True)

            else:
                tree_dir = rest_args
                self.send_cmd(f"from upysh2 import tree;tree('{tree_dir}', "
                              f"hidden={args.a})"
                              f";gc.collect()",
                              sh_silent=False, follow=True)
            return

        # IFCONFIG
        if command == 'ifconfig':
            sta_isconnected = self.send_cmd(
                "import network;network.WLAN(network.STA_IF).isconnected()")
            if sta_isconnected:
                ifconf = self.send_cmd(
                    "network.WLAN(network.STA_IF).ifconfig()")
                if not args.t:
                    print(ifconf)
                else:
                    essid = self.send_cmd(
                        "network.WLAN(network.STA_IF).config('essid')")
                    signal_rssi = self.send_cmd(
                        "network.WLAN(network.STA_IF).status('rssi')")
                    print(f"┏{'━'*15}━┳━{'━'*15}━┳━{'━'*15}━┳━{'━'*15}"
                          f"━┳━{'━'*15}━┳━{'━'*10}━┓")
                    print(f"┃{'IP':^15} ┃ {'SUBNET':^15} ┃ {'GATEAWAY':^15} "
                          f"┃ {'DNS':^15} ┃ {'SSID':^15} ┃ {'RSSI':^10} ┃")
                    print(f"┣{'━'*15}━╋━{'━'*15}━╋━{'━'*15}━╋━{'━'*15}"
                          f"━╋━{'━'*15}━╋━{'━'*10}━┫")
                    try:
                        print('┃{0:^15} ┃ {1:^15} ┃ {2:^15} ┃ {3:^15} ┃ {4:^15} ┃ '
                              '{5:^10} ┃'.format(*ifconf, essid, signal_rssi))
                        print(f"┗{'━'*15}━┻━{'━'*15}━┻━{'━'*15}━┻━{'━'*15}━┻━"
                              f"{'━'*15}━┻━{'━'*10}━┛")
                    except Exception as e:
                        print(e)

            else:
                print('STA interface not connected')
            return

        # RSSI
        if command == 'rssi':
            if hasattr(self.dev, 'get_RSSI') and self.dev.connected:
                resp = self.dev.get_RSSI()
            print(f'{resp} dBm')
            return

        # NET: STATION INTERFACE (STA_IF)

        if command == 'net':
            if not rest_args:
                netstat = self.send_cmd(_CMDDICT_['NET_STAT'],
                                        raise_devexcept=True)
                if netstat:
                    print('Station Enabled')
                else:
                    print('Station Disabled')
            else:
                if rest_args[0] == 'on':
                    stat_on = self.send_cmd(_CMDDICT_['NET_STAT_ON'],
                                            raise_devexcept=True)
                    if stat_on:
                        print('Station Enabled')
                elif rest_args[0] == 'off':
                    stat_on = self.send_cmd(_CMDDICT_['NET_STAT_OFF']+'\r'*5,
                                            raise_devexcept=True)
                    if stat_on:
                        print('Station Disabled')

                elif rest_args[0] == 'conn':
                    if not args.wp:
                        print('arg -wp required, see help.')
                        return
                    ssid, passwd = args.wp
                    print(f'Connecting to {ssid}...')
                    connect_to = _CMDDICT_['NET_STAT_CONN'].format(ssid, passwd)
                    self.send_cmd(connect_to)
                elif rest_args[0] == 'scan':
                    if self.dev.dev_platform == 'esp8266':
                        enable_sta = self.send_cmd(
                            "import network;network.WLAN(network.STA_IF).active()")
                    else:
                        enable_sta = self.send_cmd(
                            "import network;network.WLAN(network.STA_IF).active(1)")
                    if enable_sta:
                        scan = self.send_cmd(_CMDDICT_['NET_SCAN'])
                        # FIX FOR SERIAL ESP DEBUGGING INFO
                        if isinstance(scan, str):
                            try:
                                scan = ast.literal_eval(scan.split('[0m')[1])
                            except Exception:
                                scan = []
                        print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┳━{4}━┳━{5}━┓'.format(
                                        '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))
                        print('┃{0:^20} ┃ {1:^25} ┃ {2:^10} '
                              '┃ {3:^15} ┃ {4:^15} ┃ {5:^10} ┃'.format('SSID', 'BSSID',
                                                                       'CHANNEL',
                                                                       'RSSI',
                                                                       'AUTHMODE',
                                                                       'HIDDEN'))
                        print('┣{0}━╋━{1}━╋━{2}━╋━{3}━╋━{4}━╋━{5}━┫'.format(
                                        '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))
                        for net in scan:
                            netscan = net
                            auth = AUTHMODE_DICT[netscan[4]]
                            vals = hexlify(netscan[1]).decode()
                            ap_name = netscan[0].decode()
                            if len(ap_name) > 20:
                                ap_name = ap_name[:17] + '...'
                            bssid = ':'.join([vals[i:i+2]
                                              for i in range(0, len(vals), 2)])
                            print('┃{0:^20} ┃ {1:^25} ┃ {2:^10} ┃ {3:^15} ┃'
                                  ' {4:^15} ┃ {5:^10} ┃'.format(ap_name, bssid,
                                                                netscan[2],
                                                                netscan[3],
                                                                auth, str(netscan[5])))
                        print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┻━{4}━┻━{5}━┛'.format(
                                    '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))

                    else:
                        print("Can't enable STA interface")

                elif rest_args[0] == 'rssi':
                    self.sh_cmd('rssi')
            return

        # AP (ACCES POINT INTERFACE (AP_IF))
        if command == 'ap':

            if not rest_args:
                apconfig = self.send_cmd(_CMDDICT_['APSTAT'],
                                         raise_devexcept=True)
                if not args.t:
                    print(apconfig)

                else:
                    if len(apconfig) > 0:
                        auth = AUTHMODE_DICT[int(apconfig[-2])]
                        print('AP INFO:')
                        print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┓'.format(
                                        '━'*20, '━'*20, '━'*20, '━'*20))
                        print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                            'AP ENABLED', 'ESSID', 'CHANNEL', 'AUTHMODE'))
                        print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                            *apconfig[:-2], auth))
                        print('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                                        '━'*20, '━'*20, '━'*20, '━'*20))
                        print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                            'IP', 'SUBNET', 'GATEAWAY', 'DNS'))
                        try:
                            print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                                *apconfig[-1]))
                            print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┛'.format(
                                        '━'*20, '━'*20, '━'*20, '━'*20))
                        except Exception as e:
                            print(e)
                            pass
            else:
                if rest_args[0] == 'on':
                    ap_on = self.send_cmd(_CMDDICT_['AP_ON'],
                                          raise_devexcept=True)
                    if ap_on:
                        print('Access Point Enabled')
                    else:
                        print('Access Point Disabled')

                elif rest_args[0] == 'off':
                    ap_off = self.send_cmd(_CMDDICT_['AP_OFF'],
                                           raise_devexcept=True)
                    if ap_off:
                        print('Access Point Disabled')

                    else:
                        print('Access Point Enabled')
                elif rest_args[0] == 'scan':
                    if self.dev.dev_platform == 'esp8266':
                        enable_sta = self.send_cmd(
                            "import network;network.WLAN(network.AP_IF).active()")
                    else:
                        enable_sta = self.send_cmd(
                            "import network;network.WLAN(network.AP_IF).active(1)")
                    ap_scan_list = self.send_cmd(_CMDDICT_['AP_SCAN'],
                                                 raise_devexcept=True)
                    if enable_sta:
                        if len(ap_scan_list) > 0:
                            ap_devices = ap_scan_list
                            print(f'Found {len(ap_devices)} devices:')
                            for cdev in ap_devices:
                                bytdev = hexlify(cdev[0]).decode()
                                mac_ad = ':'.join([bytdev[i:i+2]
                                                   for i in range(0, len(bytdev), 2)])
                                print(f'MAC: {mac_ad}')
                        else:
                            print('No device found')
                    else:
                        print("Can't enable AP interface")

                elif rest_args[0] == 'config':
                    if not args.ap:
                        print('arg -ap required, see help.')
                        return
                    ssid, passwd = args.ap
                    print(f'Configuring {ssid} Access Point ...')
                    apconfig = _CMDDICT_['AP_CONFIG'].format(ssid, passwd)
                    if len(passwd) < 8:
                        print('[WARNING]: Password too short (less than 8 characters)')
                        return
                    else:
                        self.send_cmd(apconfig, raise_devexcept=True)
                        print(f'{ssid} Access Point Configured')
                return

        # I2C
        if command == 'i2c':
            if not rest_args:
                print('scan   config')
            else:
                if rest_args[0] == 'config':
                    if not args.i2c:
                        print('arg -i2c required, see help.')
                        return
                    scl, sda = args.i2c
                    if self.dev.dev_platform == 'pyboard':
                        self.send_cmd(_CMDDICT_['I2C_CONFIG_PYB'].format(scl, sda),
                                      raise_devexcept=True)
                    else:
                        self.send_cmd(_CMDDICT_['I2C_CONFIG'].format(
                            scl, sda), raise_devexcept=True)

                    print(f'I2C configured:\nSCL = Pin({scl}), SDA = Pin({sda})')
                elif rest_args[0] == 'scan':
                    i2c_scan_list = self.send_cmd(_CMDDICT_['I2C_SCAN'],
                                                  raise_devexcept=True)

                    if len(i2c_scan_list) > 0:
                        i2c_devices = i2c_scan_list
                        print(f'Found {len(i2c_devices)} devices:')
                        print(i2c_devices)
                        print('Hex:')
                        print([hex(i2c_dev) for i2c_dev in i2c_devices])
                    else:
                        print('No device found')
            return

        # SET
        if command == 'set':
            if not rest_args:
                print('localtime    ntptime    hostname    localname')
            else:
                #  * RTC *

                # SET LOCAL TIME
                if rest_args[0] == 'localtime':
                    print('Setting local time: {}'.format(
                        datetime.now().strftime("%Y-%m-%d T %H:%M:%S")))
                    wkoy = date.today().isocalendar()[1]
                    datetime_local = [val for val in datetime.now().timetuple()[:-3]]
                    datetime_tuple = datetime_local[:3]
                    datetime_tuple.append(wkoy)
                    datetime_final = datetime_tuple + datetime_local[3:] + [0]
                    self.send_cmd(_CMDDICT_['SET_RTC_LT'].format(*datetime_final),
                                  raise_devexcept=True)

                    print('Done!')
                # SET NTP TIME
                elif rest_args[0] == 'ntptime':
                    utc = args.utc
                    print(f'Setting time UTC+{utc} from NTP Server')
                    for ntp_cmd in _CMDDICT_['SET_RTC_NT'].format(utc).split(';'):
                        self.send_cmd(ntp_cmd, raise_devexcept=True)
                    print('Done!')

                # SET HOSTNAME
                elif rest_args[0] == 'hostname':
                    if len(rest_args) < 2:
                        print('Indicate a name to set')
                    else:
                        hostname = rest_args[1]
                        print(f"Setting hostname: {hostname}")
                        self.send_cmd(
                            _CMDDICT_['SET_HOSTNAME'].format(f'NAME="{hostname}"'),
                            raise_devexcept=True)
                        print('Done!')

                # SET LOCALNAME
                elif rest_args[0] == 'localname':
                    if len(rest_args) < 2:
                        print('Indicate a name to set')
                    else:
                        localname = rest_args[1]
                        print(f"Setting localname: {localname}")
                        self.send_cmd(
                            _CMDDICT_['SET_LOCALNAME'].format(f'NAME="{localname}"'),
                            raise_devexcept=True)
                        print('Done!')
            return

        # DATETIME
        if command == 'datetime':
            resp = self.send_cmd("import time;tnow=time.localtime();tnow[:6]")
            print("{}-{}-{}T{}:{}:{}".format(*_ft_datetime(resp)))

        # SHASUM_CHECK
        if command == 'shasum':
            if args.c:
                # print(f"Checking shasum file: {file_name}")
                self.send_cmd(_CMDDICT_['SHASUM_CHECK'].format(args.c),
                              sh_silent=False, follow=True, raise_devexcept=True)
                return
            if not rest_args:
                print('Shasum HASH SHA256, indicate a file to hash')
            else:
                files_to_hash = f"*{rest_args}"
                self.send_cmd(_CMDDICT_['SHASUM'].format(files_to_hash),
                              sh_silent=False, follow=True)

            return

        # MKDIR
        if command == 'mkdir':
            if not rest_args:
                print('Indicate a directory to make')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                for dir in rest_args:
                    self.dev.wr_cmd(f'mkdir("{dir}")', follow=True)
            return
        # RM  --> TODO: pattrn match and -rf
        if command == 'rm':
            if not rest_args and not args.rf:
                print('Indicate a file to remove')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                if not args.rf:
                    for file in rest_args:
                        self.dev.wr_cmd(f'rm("{file}")', follow=True)
                else:
                    self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                    rest_args = self.brace_exp(rest_args)
                    for file in rest_args:
                        self.dev.wr_cmd(f'rmrf("{file}")', follow=True)
            return

        # RMDIR --> TODO: pattrn match and -rf
        if command == 'rmdir':
            if not rest_args:
                print('Indicate a dir to remove')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                for dir in rest_args:
                    self.dev.wr_cmd(f'rmdir("{dir}")', follow=True)
            return

        # PWD
        if command == 'pwd':
            self.dev.wr_cmd('pwd', follow=True)

        # CD
        if command == 'cd':
            if not rest_args:
                rest_args = '/'
            self.dev.wr_cmd(f"cd('{rest_args}')", silent=False, follow=True)
            self.dev.output = None
            cwd = self.dev.wr_cmd('pwd', silent=True, rtn_resp=True)

            if cwd is not None:
                devpath = cwd
                self.flags.dev_path['p'] = devpath
                if devpath == '/':
                    devpath = ' '
                    self.flags.dev_path['p'] = ' '
                self.flags.shell_prompt['s'][0] = ('class:userpath',
                                                   self.flags.local_path['p'])
                self.flags.shell_prompt['s'][5] = ('class:path', f'~{devpath}')
                self.flags.prompt['p'] = self.flags.shell_prompt['s']
            return

        # LS

        if command == 'ls':
            if not rest_args:
                rest_args = ['']
            rest_args = self.brace_exp(rest_args)
            files_to_list = f"*{rest_args}"
            term_size = tuple(os.get_terminal_size(0))
            self.send_cmd(_CMDDICT_['LS'].format(files_to_list, term_size, args.a),
                          sh_silent=False, follow=True)
            return

        # CAT
        if command == 'cat':
            if not rest_args:
                print('Indicate a file/s or a matching pattrn to see')
            else:
                rest_args = self.brace_exp(rest_args)
                files_to_see = f"*{rest_args}"
                self.send_cmd(_CMDDICT_['CAT'].format(files_to_see),
                              sh_silent=False, follow=True)

            return

        # head
        if command == 'head':
            if not rest_args:
                print('Indicate a file/s or a matching pattrn to see')
            else:
                rest_args = self.brace_exp(rest_args)
                files_to_see = f"*{rest_args}"
                self.send_cmd(_CMDDICT_['HEAD'].format(files_to_see, args.n),
                              sh_silent=False, follow=True)

            return

        # TOUCH
        if command == 'touch':
            # brace expansion
            if not rest_args:
                print('Indicate a file/s to create')
            else:
                rest_args = self.brace_exp(rest_args)
                files_to_create = f"*{rest_args}"
                self.send_cmd(_CMDDICT_['TOUCH'].format(files_to_create),
                              sh_silent=False, follow=True)

        # UPIP
        if command == 'upip':
            if not rest_args:
                print('install    info    find')
            else:
                sbcmd, _rest_args = rest_args[0], rest_args[1:]
                if sbcmd == 'install':
                    if not _rest_args:
                        print('Indicate a library to install with upip')
                    else:
                        for lib in _rest_args:
                            self.send_cmd(f"import upip;upip.install('{lib}')",
                                          sh_silent=False)
                elif sbcmd == 'info':
                    if not _rest_args:
                        print('Indicate a library to see info about')
                    else:
                        for lib in _rest_args:
                            upip_host.install_pkg(lib, ".", read_pkg_info=True)
                elif sbcmd == 'find':
                    if not _rest_args:
                        print('Available MicroPython libs (just a random subset):')
                        list_upylibs = shlex.split('pip search micropython')
                        subprocess.call(list_upylibs)
                    else:
                        for lib in _rest_args:
                            print(f"Available MicroPython libs that match {lib}:")
                            list_upylibs = shlex.split(f"pip search {lib}")
                            subprocess.call(list_upylibs)

        # TIMEIT
        if command == 'timeit':
            if not rest_args:
                print("Indicate a script/command to measure execution time")
            else:
                try:
                    for script in rest_args:
                        if script.endswith('.py') or script.endswith('.mpy'):
                            print(f'Timing script: {script}')
                            script_to_time = script.replace(
                                '.py', '').replace('.mpy', '')
                            inp = (f"from time_it import tzero, tdiff, result;t_0 = "
                                   f"tzero();import {script_to_time};diff=tdiff(t_0);"
                                   f"result('{script_to_time}',diff);")
                        else:
                            cmd_to_time = script
                            inp = (f"from time_it import tzero, tdiff, result;t_0 = "
                                   f"tzero();{cmd_to_time};diff=tdiff(t_0);"
                                   f"result('{cmd_to_time}',diff, cmd=True);")

                        self.dev.wr_cmd(inp, follow=True)

                except Exception as e:
                    print(e)

        # RUN
        if command == 'run':
            if not rest_args:
                print('Indicate a script to run')
                return
            else:
                script_name = rest_args[0].split('.')[0]
                reload = f"del(sys.modules['{script_name}'])"
                run_cmd = f"import {script_name}"
                # print(run_cmd)
                # if args.s is not None:
                #     dir = args.s
                #     sd_path = "import sys;sys.path.append('/{}')".format(dir)
                #     run_cmd = "{};import {}".format(sd_path, script_name)
                print(f'Running {rest_args[0]}...')
                self.dev.wr_cmd(run_cmd, follow=True)
                if args.r:
                    print(f'Reloading {rest_args[0]}...')
                    reload_cmd = (f"import sys;{reload};"
                                  f"gc.collect()")
                    self.dev.wr_cmd(reload_cmd)
                    print('Done!')

        # RELOAD
        if command == 'reload':
            if not rest_args:
                print('Indicate a module/s to reload')
            else:
                for module in rest_args:
                    module = module.replace('.py', '')
                    reload_cmd = f"import sys;del(sys.modules['{module}']);gc.collect()"
                    self.dev.wr_cmd(reload_cmd)

        # DOCS
        if command == 'docs':
            if rest_args:
                key = rest_args[0]
                search = (f'http://docs.micropython.org/en/latest/search.html?q={key}&'
                          'check_keywords=yes&area=default')
                webbrowser.open(search)
            else:
                webbrowser.open('http://docs.micropython.org/en/latest/')

        # DVIM
        if command == 'vim':
            if not rest_args:
                print('Indicate a file to edit')
                return

            fileargs = FileArgs()

            file_to_edit = rest_args[0]
            self.dev.wr_cmd('from upysh import cat', silent=True)
            files_to_see = f"*{[file_to_edit]}"
            filedata = self.dev.wr_cmd(_CMDDICT_['VIM'].format(files_to_see),
                                       silent=True, rtn_resp=True, multiline=True,
                                       long_string=True)
            # print(filedata)
            if filedata == f'vim: {file_to_edit}: No such file in directory\n':
                filedata = ' '
            _file_to_edit = file_to_edit.rsplit('/')[-1]
            with open(_file_to_edit, 'w') as fte:
                fte.write(filedata)
            shell_cmd_str = shlex.split(f"vim {_file_to_edit}")

            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)
            try:
                subprocess.call(shell_cmd_str, preexec_fn=preexec_function)
                signal.signal(signal.SIGINT, old_action)
            except Exception as e:
                print(e)

            # Check if file changes:
            with open(_file_to_edit, 'r') as fte:
                filedata2 = fte.read()
            if filedata != filedata2:
                dest_file = file_to_edit
                if self.dev.dev_class == 'SerialDevice':
                    from upydev.serialio import SerialFileIO
                    fileio = SerialFileIO(self.dev,
                                          devname=self.flags.shell_prompt['s'][3][1])
                    fileio.put(_file_to_edit, dest_file, ppath=True)
                elif self.dev.dev_class == 'WebSocketDevice':
                    from upydev.wsio import WebSocketFileIO
                    fileargs.wss = self.dev._uriprotocol == 'wss'
                    fileio = WebSocketFileIO(self.dev, args=fileargs,
                                             devname=self.flags.shell_prompt['s'][3][1])
                    fileio.put(_file_to_edit, dest_file, ppath=True)
                elif self.dev.dev_class == 'BleDevice':
                    from upydev.bleio import BleFileIO
                    fileio = BleFileIO(self.dev,
                                       devname=self.flags.shell_prompt['s'][3][1])
                    fileio.put(_file_to_edit, dest_file, ppath=True)
            if args.r:
                os.remove(_file_to_edit)
            if args.e:
                script_name = file_to_edit.replace('.py', '')
                run_cmd = f"import {script_name}"
                print(f'Running {script_name}...')
                self.dev.wr_cmd(run_cmd, follow=True)
            return

        if command in _SPECIAL_SHELL_CMDS:
            self.custom_sh_cmd(command, rest_args, args, self.topargs)

    def local_sh_cmds(self, command, args, rest_args):
        # DISK USAGE STATISTICS
        if command == 'ldu':
            if not rest_args:
                du(max_dlev=args.d)

            else:
                du_dir = rest_args[0]
                du(path=f'./{du_dir}', max_dlev=args.d)
            return
        # PWD
        if command == 'lpwd':
            print(os.getcwd())

        if command == 'lcd':
            if not rest_args:
                os.chdir(os.environ['HOME'])
            else:
                dir = rest_args[0]
                try:
                    os.chdir(dir)
                except OSError:
                    print(f'lcd: {dir}: Not a directory')
                    return
            if os.getcwd() == os.environ['HOME']:
                self.flags.local_path['p'] = '~:/'
                if not self.flags.show_local_path['s']:
                    self.flags.local_path['p'] = ''
            elif not self.flags.show_local_path['s']:
                self.flags.local_path['p'] = ''
            else:
                self.flags.local_path['p'] = os.getcwd().split('/')[-1]+':/'

            self.flags.shell_prompt['s'][0] = ('class:userpath',
                                               self.flags.local_path['p'])
            self.flags.prompt['p'] = self.flags.shell_prompt['s']
            return

        if command == 'lsl':
            if not rest_args:
                rest_args = ['.']
            rest_args = self.brace_exp(rest_args)
            dir_names_or_pattrn = rest_args
            ls(*dir_names_or_pattrn, hidden=args.a)
            return
