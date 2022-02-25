import os
import argparse
import shlex
from upydev.shell.constants import (AUTHMODE_DICT,
                                    shell_commands, custom_sh_cmd_kw, shell_message)
from upydev.shell.common import (du, _ft_datetime, SHELL_ALIASES, ls, FileArgs,
                                 find_localip, SHELL_FUNCTIONS, print_table)
from upydev.shell.parser import shparser
from prompt_toolkit.formatted_text import HTML
from binascii import hexlify
from upydev.commandlib import _CMDDICT_
from upydev import upip_host
from upydev import __path__ as _UPYDEVPATH
from upydevice import DeviceException
from braceexpand import braceexpand
from datetime import datetime, date, timedelta
from contextlib import redirect_stdout, closing
from upydev.shell.redirectsh import Tee
from upydev.shell.nanoglob import glob as nglob
from upydev.shell.shasum import _shasum_data, shasum
from upydev.shell.upyconfig import config_parser, param_parser
from upydev.sdcommands import sd_command
import traceback
import ast
import time
import signal
import subprocess
import webbrowser

# SHELL COMMAND PARSER
rawfmt = argparse.RawTextHelpFormatter

_SHELL_CMDS = custom_sh_cmd_kw + shell_commands

_LOCAL_SHELL_CMDS = ['ldu', 'lsl', 'lpwd', 'lcd']

_SPECIAL_SHELL_CMDS = ['jupyterc', 'get', 'put', 'fw', 'flash', 'dsync',
                       'repl', 'pytest', 'getcert', 'git', 'update_upyutils',
                       'upy-config', 'debugws', 'mpyx', 'ota', 'services', 'install']


class ShellFlags:
    def __init__(self):
        self.mem_show_rp = {'show': False, 'call': False, 'used': '?',
                            'free': '?', 'percent': 0}
        self.dev_path = {'p': ' '}
        self.local_path = {'p': ''}
        self.show_local_path = {'s': False}
        self.exit = {'exit': False}
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
        self._shkw = _SHELL_CMDS
        self.dev_name = self.flags.shell_prompt['s'][3][1]
        self._pipe_flags = ['>', '>>', '|']

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

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None,
                      ukw_args=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        return

    def escape_sh_cmd(self, cmd_inp):
        # SHELL ESCAPE:
        my_env = os.environ.copy()
        if cmd_inp.startswith('%') or cmd_inp.split()[0] not in self._shkw + ['-h',
                                                                              '-v']:
            if cmd_inp.split()[0] != 'ping':
                try:
                    if cmd_inp.startswith('%'):
                        cmd_inp = cmd_inp[1:]
                    # expand user
                    cmd_inp = cmd_inp.replace('~', os.path.expanduser('~'))
                    shell_cmd_str = shlex.split(cmd_inp)
                    # brace_expand
                    shell_cmd_str = self.brace_exp(shell_cmd_str)
                    # globals expand
                    _shell_cmd_str = [cmd if '*' not in cmd
                                      else nglob(cmd) for cmd in shell_cmd_str]
                    shell_cmd_str = []
                    for cmd in _shell_cmd_str:
                        if isinstance(cmd, list):
                            shell_cmd_str += cmd
                        else:
                            shell_cmd_str.append(cmd)
                    if shell_cmd_str[0] in SHELL_ALIASES:
                        shell_cmd_str = SHELL_ALIASES[shell_cmd_str[0]
                                                      ].split() + shell_cmd_str[1:]
                    if shell_cmd_str[0] in SHELL_FUNCTIONS:
                        shell_cmd_str = SHELL_FUNCTIONS[shell_cmd_str[0]
                                                        ].split() + shell_cmd_str[1:]
                    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

                    def preexec_function(action=old_action):
                        signal.signal(signal.SIGINT, action)
                    try:
                        subprocess.call(' '.join(shell_cmd_str), preexec_fn=preexec_function,
                                        env=my_env, shell=True,
                                        executable=my_env['SHELL'])
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
                    else:
                        ping_cmd_str = 'ping'
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
                    print("indicate a host to ping, e.g google.com")

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
            return self.parser.parse_known_args(command_args)
        except SystemExit:  # argparse throws these because it assumes you only want
            # to do the command line
            return None  # should be a default one

    def cmd(self, cmdline):
        try:
            # catch concatenated commands with &&
            if ' && ' in cmdline:
                for _cmdline in cmdline.split(' && '):
                    self.sh_cmd(_cmdline)
            else:
                self.sh_cmd(cmdline)
        except KeyboardInterrupt as e:
            print(e)

    def sh_cmd(self, cmd_inp):

        # debug command:
        if cmd_inp.startswith('!'):
            args = self.parseap(shlex.split(cmd_inp[1:]))
            print(args)
            return
        # SHELL ESCAPE:
        if self.escape_sh_cmd(cmd_inp):
            return

        # PARSE ARGS
        command_line = shlex.split(cmd_inp)

        all_args = self.parseap(command_line)

        if not all_args:
            return
        else:
            args, unknown_args = all_args
        if hasattr(args, 'subcmd'):
            command, rest_args = args.m, args.subcmd
            if rest_args is None:
                rest_args = []
        else:
            command, rest_args = args.m, []

        # LOCAL COMMANDS
        if command in _LOCAL_SHELL_CMDS:
            self.local_sh_cmds(command, args, rest_args)
            return

        # ENABLE PIPES >, >>, |
        if any([pipecmd in rest_args for pipecmd in self._pipe_flags]):
            if '>' in rest_args:
                pflag = '>'
                ix = rest_args.index(pflag)
            elif '>>' in rest_args:
                pflag = '>>'
                ix = rest_args.index(pflag)
            elif '|' in rest_args:
                pflag = '|'
                ix = rest_args.index(pflag)
            rest_args, filetopipe = rest_args[:ix], rest_args[ix:]
            cmd_to_pipe = f"{command} {' '.join(rest_args)}"
            try:
                if pflag == '>':
                    wmode = 'wb'
                elif pflag == '>>':
                    wmode = 'ab'
                elif pflag == '|':
                    wmode = 'ab'
                else:
                    return
                with open(filetopipe[-1], wmode[:-1]) as f:
                    pass
                if pflag in ['>', '>>']:
                    with open(filetopipe[-1], wmode[:-1]) as f:
                        with redirect_stdout(f):
                            self.sh_cmd(cmd_to_pipe)

                elif pflag == '|':
                    with closing(Tee(f"{filetopipe[-1]}",
                                     wmode[:-1], channel="stdout")) as outstream:
                        self.sh_cmd(cmd_to_pipe)

                if len(filetopipe) > 1:
                    with open(f"{filetopipe[-1]}.{self.dev_name}", wmode) as pipfile:
                        data = self.dev.buff.replace(b'\r',
                                                     b'').replace(b'\r\n>>> ',
                                                                  b'').replace(b'>>> ',
                                                                               b'')
                        pipfile.write(data)
            except Exception as e:
                print(e)
            return
            # save

        if any([pipecmd in unknown_args for pipecmd in self._pipe_flags]):
            if '>' in unknown_args:
                pflag = '>'
                ix = unknown_args.index(pflag)
            elif '>>' in unknown_args:
                pflag = '>>'
                ix = unknown_args.index(pflag)
            elif '|' in unknown_args:
                pflag = '|'
                ix = unknown_args.index(pflag)
            filetopipe = unknown_args[ix:]
            opt_args = [f'-{opt} {val}' for opt, val in vars(args).items()
                        if opt not in ['m', 'subcmd'] and opt in command_line]
            if not isinstance(rest_args, list):
                rest_args = [rest_args]
            cmd_to_pipe = (f"{command} {' '.join(rest_args)} "
                           f"{' '.join(opt_args)}")
            # print(cmd_to_pipe)
            try:
                if pflag == '>':
                    wmode = 'wb'
                elif pflag == '>>':
                    wmode = 'ab'
                elif pflag == '|':
                    wmode = 'ab'
                else:
                    return
                # SHELL LOG
                if pflag in ['>', '>>']:
                    with open(filetopipe[-1], wmode[:-1]) as f:
                        with redirect_stdout(f):
                            self.sh_cmd(cmd_to_pipe)
                elif pflag == '|':
                    with closing(Tee(f"{filetopipe[-1]}",
                                     wmode[:-1], channel="stdout")) as outstream:
                        self.sh_cmd(cmd_to_pipe)
                if len(filetopipe) > 1:
                    with open(f"{filetopipe[-1]}.{self.dev_name}", wmode) as pipfile:
                        data = self.dev.buff.replace(b'\r',
                                                     b'').replace(b'\r\n>>> ',
                                                                  b'').replace(b'>>> ',
                                                                               b'')
                        pipfile.write(data)
            except Exception as e:
                print(e)
            return
            # CTIME
        if command == 'ctime':
            start_time = time.time()
            if rest_args != 'ctime':
                cmd_profile = f"{rest_args} {' '.join(unknown_args)}"
                print(f"ctime: {cmd_profile}")
                try:
                    self.sh_cmd(cmd_profile)
                except Exception as e:
                    print(f"{cmd_profile}: failed, reason: {e}")
                    show_tb = input('Do you want to see full traceback?[y/n]')
                    if show_tb == 'y':
                        print(traceback.format_exc())

                end_time = time.time()
                print(f"command time: {timedelta(seconds=(end_time-start_time))}")
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
            resp = self.send_cmd("import os;os.statvfs('')")
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
                              f'du(max_dlev={args.d}, pattrn={args.p});gc.collect()',
                              sh_silent=False, follow=True)

            else:
                du_dir = rest_args
                self.send_cmd(f"from upysh2 import du;du(path='./{du_dir}',"
                              f"max_dlev={args.d}, pattrn={args.p});gc.collect()",
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

        # UPING
        if command == 'uping':
            ping_dir = rest_args
            if ping_dir == 'host':
                ping_dir = find_localip()
            inp = f"import uping;uping.ping('{ping_dir}', loop=True, rtn=False)"
            self.dev.wr_cmd(inp, follow=True, multiline=True, long_string=True)
            return

        # RSSI
        if command == 'rssi':
            if hasattr(self.dev, 'get_RSSI') and self.dev.connected:
                resp = self.dev.get_RSSI()
                print(f'{resp} dBm')
            return

        # NET: STATION INTERFACE (STA_IF)

        if command == 'net':

            if rest_args == 'status':
                netstat = self.send_cmd(_CMDDICT_['NET_STAT'],
                                        raise_devexcept=True)
                if netstat:
                    print('Station Enabled')
                else:
                    print('Station Disabled')
            else:
                if rest_args == 'on':
                    stat_on = self.send_cmd(_CMDDICT_['NET_STAT_ON'],
                                            raise_devexcept=True)
                    if stat_on:
                        print('Station Enabled')
                elif rest_args == 'off':
                    stat_on = self.send_cmd(_CMDDICT_['NET_STAT_OFF']+'\r'*5,
                                            raise_devexcept=True)
                    if stat_on:
                        print('Station Disabled')

                elif rest_args == 'config':
                    if not args.wp:
                        print('arg -wp required for config command, see help.')
                        return
                    ssid, passwd = args.wp
                    print(f'Connecting to {ssid}...')
                    connect_to = _CMDDICT_['NET_STAT_CONN'].format(ssid, passwd)
                    self.send_cmd(connect_to)
                elif rest_args == 'scan':
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

            return

        # AP (ACCES POINT INTERFACE (AP_IF))
        if command == 'ap':

            if rest_args == 'status':
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
                if rest_args == 'on':
                    ap_on = self.send_cmd(_CMDDICT_['AP_ON'],
                                          raise_devexcept=True)
                    if ap_on:
                        print('Access Point Enabled')
                    else:
                        print('Access Point Disabled')

                elif rest_args == 'off':
                    ap_off = self.send_cmd(_CMDDICT_['AP_OFF'],
                                           raise_devexcept=True)
                    if ap_off:
                        print('Access Point Disabled')

                    else:
                        print('Access Point Enabled')
                elif rest_args == 'scan':
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

                elif rest_args == 'config':
                    if not args.ap:
                        print('arg -ap required for config command, see help.')
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
            if rest_args == 'config':
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
            elif rest_args == 'scan':
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

#     # SPI CONFIG
#     elif cmd == 'spi_config':
#         spi_conf = kargs.pop('spi')
#         dev = Device(*args, **kargs)
#         dev.cmd(_CMDDICT_['SPI_CONFIG'].format(*spi_conf), silent=True)
#         if dev._traceback.decode() in dev.response:
#             try:
#                 raise DeviceException(dev.response)
#             except Exception as e:
#                 print(e)
#         else:
#             print('SPI configured:\nSCK = Pin({}), MISO = Pin({}), MOSI = Pin({}), CS = Pin({})'.format(
#                     *spi_conf))
#         dev.disconnect()
#         return

        # SET
        if command == 'set':
            #  * RTC *

            # SET LOCAL TIME
            if rest_args[0] == 'rtc':
                # SET LOCAL TIME
                if len(rest_args) == 1:
                    rest_args += ['localtime']
                if rest_args[1] == 'localtime':
                    print('Setting local time: {}'.format(
                        datetime.now().strftime("%Y-%m-%d T %H:%M:%S")))
                    wkoy = date.today().isoweekday()
                    datetime_local = [val for val in datetime.now().timetuple()[:-3]]
                    datetime_tuple = datetime_local[:3]
                    datetime_tuple.append(wkoy)
                    datetime_final = datetime_tuple + datetime_local[3:] + [0]
                    self.send_cmd(_CMDDICT_['SET_RTC_LT'].format(*datetime_final),
                                  raise_devexcept=True)

                    print('Done!')
                # SET NTP TIME
                elif rest_args[1] == 'ntptime':
                    utc = args.utc
                    print(f'Setting time UTC+{utc} from NTP Server')
                    for ntp_cmd in _CMDDICT_['SET_RTC_NT'].format(utc).split(';'):
                        self.send_cmd(ntp_cmd, raise_devexcept=True)
                    print('Done!')

            # SET HOSTNAME
            elif rest_args[0] == 'hostname':
                if len(rest_args) < 2:
                    print('indicate a name to set')
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
                    print('indicate a name to set')
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

        # CONFIG
        if command == 'config':
            if not rest_args:
                self.dev.wr_cmd('from nanoglob import glob', silent=True)
                dev_config = self.dev.wr_cmd("glob('*_config.py')",
                                             silent=True, rtn_resp=True)
                _params_config = [param.split('_')[0].rsplit('/')[-1]
                                  for param in dev_config]
                print_table(_params_config, wide=16, format_SH=False)
            else:
                if rest_args[0] != 'add':
                    if not rest_args[0].endswith(':'):  # check config
                        self.dev.wr_cmd('from nanoglob import glob', silent=True)
                        rest_args = [f"*{param}_config.py" for param in rest_args]
                        dev_config = self.dev.wr_cmd(f"glob(*{rest_args})",
                                                     silent=True, rtn_resp=True)
                        _params_config = [(param.split('_')[0].rsplit('/')[-1],
                                           param.replace('.py', '').rsplit('/')[-1])
                                          for param in dev_config]
                        params_config = {param: self.dev.wr_cmd(f"from {config} import "
                                                                f"{param.upper()}"
                                                                f"; {param.upper()}",
                                                                silent=True,
                                                                rtn_resp=True)
                                         for param, config in _params_config}
                        for conf in params_config.keys():
                            def_conf = {}
                            param_in_config = config_parser(self.dev, conf)
                            for param in param_in_config:
                                def_conf[param] = param_parser(params_config[conf],
                                                               param)
                            if args.y:
                                conf_str = '\n    '.join([f'{k}: {v}'
                                                          for k, v in def_conf.items()])
                                print(f"{conf}: \n    {conf_str}")
                            else:
                                conf_str = ', '.join([f'{k}={v}'
                                                      for k, v in def_conf.items()])
                                print(f"{conf} -> {conf_str}")
                    else:  # set config
                        param_option = rest_args[0].replace(':', '')
                        new_conf = rest_args[1:]
                        new_params_str = ', '.join(new_conf)
                        new_conf_str = (f"from config.params import set_{param_option}"
                                        f";set_{param_option}({new_params_str})")
                        self.dev.wr_cmd(new_conf_str, silent=True)
                        reload_cmd = (f"import sys;"
                                      f"del(sys.modules['{param_option}_config']);"
                                      f"gc.collect(); from {param_option}_config import"
                                      f" {param_option.upper()}")
                        self.dev.wr_cmd(reload_cmd, silent=True)
                        print(f"{param_option} -> {new_params_str}")

                else:
                    # new config
                    if len(rest_args) > 1:
                        new_confs = rest_args[1:]
                        for nc in new_confs:
                            self.dev.wr_cmd(f"from config import add_param; "
                                            f"add_param('{nc}')")
                        reload_cmd = ("import sys;del(sys.modules['config.params']);"
                                      "gc.collect()")
                        self.dev.wr_cmd(reload_cmd, silent=True)
                    else:
                        print('config: add: name of config required')

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
                # if '>' in unknown_args:  # create a file
                #     with open(unknown_args[-1], 'w') as shafile:
                #         shafile.write(self.dev.response.encode('utf-8'))

            return

        # MKDIR
        if command == 'mkdir':
            if not rest_args:
                print('indicate a directory to make')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                for dir in rest_args:
                    self.dev.wr_cmd(f'mkdir("{dir}")', follow=True)
            return
        # RM  --> TODO: pattrn match and -rf
        if command == 'rm':
            if not rest_args:
                print('indicate a file to remove')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                if args.d:
                    _rest_args = [[('*/' * i) + patt for i in range(args.d)] for patt in
                                  rest_args]
                    rest_args = []
                    for gpatt in _rest_args:
                        for dpatt in gpatt:
                            rest_args.append(dpatt)
                self.dev.wr_cmd('from nanoglob import glob', silent=True)
                if not args.rf:
                    self.dev.wr_cmd(f'rm(*glob(*{rest_args}))', follow=True)
                else:
                    self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                    self.dev.wr_cmd(f'rmrf(*glob(*{rest_args},dir_only={args.dd}))',
                                    follow=True)
            return

        if command == 'rmdir':
            if not rest_args:
                print('indicate a dir to remove')
                return
            else:
                rest_args = self.brace_exp(rest_args)
                self.dev.wr_cmd('from nanoglob import glob', silent=True)
                if args.d:
                    _rest_args = [[('*/' * i) + patt for i in range(args.d)] for patt in
                                  rest_args]
                    rest_args = []
                    for gpatt in _rest_args:
                        for dpatt in gpatt:
                            rest_args.append(dpatt)

                self.dev.wr_cmd(f'rmdir(*glob(*{rest_args}, dir_only=True))',
                                follow=True)
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
            if args.d:
                _rest_args = [[('*/' * i) + patt for i in range(args.d)] for patt in
                              rest_args]
                rest_args = []
                for gpatt in _rest_args:
                    for dpatt in gpatt:
                        rest_args.append(dpatt)
            files_to_list = f"*{rest_args}"
            term_size = tuple(os.get_terminal_size(0))
            self.send_cmd(_CMDDICT_['LS'].format(files_to_list, term_size, args.a),
                          sh_silent=False, follow=True)
            return

        # CAT
        if command == 'cat':
            if not rest_args:
                print('indicate a file/s or a matching pattrn to see')
            else:
                rest_args = self.brace_exp(rest_args)
                if args.d:
                    _rest_args = [[('*/' * i) + patt for i in range(args.d)] for patt in
                                  rest_args]
                    rest_args = []
                    for gpatt in _rest_args:
                        for dpatt in gpatt:
                            rest_args.append(dpatt)
                files_to_see = f"*{rest_args}"
                self.send_cmd(_CMDDICT_['CAT'].format(files_to_see),
                              sh_silent=False, follow=True)

            return

        # head
        if command == 'head':
            if not rest_args:
                print('indicate a file/s or a matching pattrn to see')
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
                print('indicate a file/s to create')
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
                        print('indicate a library to install with upip')
                    else:
                        for lib in _rest_args:
                            self.sh_cmd(f'install {lib}')
                            # self.send_cmd(f"import upip;upip.install('{lib}')",
                            #               sh_silent=False)
                elif sbcmd == 'info':
                    if not _rest_args:
                        print('indicate a library to see info about')
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
                print("indicate a script/command to measure execution time")
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
                print('indicate a script to run')
                return
            else:
                script_name = rest_args.split('.')[0]
                reload = f"del(sys.modules['{script_name}'])"
                run_cmd = f"import {script_name}"
                print(f'Running {rest_args}...')
                try:
                    self.dev.wr_cmd(run_cmd, follow=True)
                except KeyboardInterrupt:
                    self.dev.kbi()

                if args.r:
                    print(f'Reloading {rest_args}...')
                    reload_cmd = (f"import sys;{reload};"
                                  f"gc.collect()")
                    self.dev.wr_cmd(reload_cmd)
                    print('Done!')

        # RELOAD
        if command == 'reload':
            if not rest_args:
                print('indicate a module/s to reload')
            else:
                for module in rest_args:
                    module = module.replace('.py', '')
                    reload_cmd = f"import sys;del(sys.modules['{module}']);gc.collect()"
                    self.dev.wr_cmd(reload_cmd)

        # DOCS
        if command == 'docs':
            if rest_args:
                key = rest_args
                search = (f'https://upydev.readthedocs.io/en/latest/search.html?q={key}&'
                          'check_keywords=yes&area=default')
                webbrowser.open(search)
            else:
                webbrowser.open('https://upydev.readthedocs.io/en/latest/')

        # MDOCS
        if command == 'mdocs':
            if rest_args:
                key = rest_args
                search = (f'https://docs.micropython.org/en/latest/search.html?q={key}&'
                          'check_keywords=yes&area=default')
                webbrowser.open(search)
            else:
                webbrowser.open('https://docs.micropython.org/en/latest/')

        # DIFF
        if command == 'diff':
            if not rest_args:
                print('diff: indicate fileA fileB to compare')
                return

            if '*' in rest_args[0]:
                local_files = []
                dev_cmd_files = (f"from shasum import shasum;"
                                 f"shasum(*{[rest_args[0]]}, debug=True, "
                                 f"rtn=False, size=True);gc.collect()")
                print('diff: checking files...')
                self.fastfileio.init_sha(prog='diff')
                dev_files = self.dev.wr_cmd(dev_cmd_files, follow=True,
                                            rtn_resp=True, long_string=True,
                                            pipe=self.fastfileio.shapipe)
                if not dev_files:
                    dev_files = self.fastfileio._shafiles
                    if dev_files:
                        self.fastfileio.end_sha()
                if dev_files:
                    local_files = shasum(*[rest_args[0]], debug=False, rtn=True,
                                         size=True)
                if local_files:
                    files_to_diff = [(fts[0], fts[2])
                                     for fts in dev_files if fts not in
                                     local_files]
                    for file, fhash in files_to_diff:
                        self.sh_cmd(f'diff {file}')
                return

            file_to_edit = rest_args[0]
            _file_to_edit = file_to_edit.rsplit('/', 1)[-1]
            # dir = file_to_edit.rsplit('/', 1)[0]
            if len(rest_args) == 1 and not nglob(file_to_edit):
                print(f'diff: {file_to_edit}: No such file in local directory')
                return
            self.dev.wr_cmd('from upysh import cat', silent=True)
            files_to_see = f"*{[file_to_edit]}"
            filedata = self.dev.wr_cmd(_CMDDICT_['VIM'].format(files_to_see),
                                       silent=True, rtn_resp=True, multiline=True,
                                       long_string=True)
            # print(filedata)

            local_file = False
            if nglob(file_to_edit):
                local_file = nglob(file_to_edit)[0]
                _file_to_edit = file_to_edit.replace(_file_to_edit,
                                                     f"~{_file_to_edit}")

            if filedata == f'vim: {file_to_edit}: No such file in directory\n':
                print(f'diff: {file_to_edit}: No such file in device directory')
                return

            if filedata:
                with open(_file_to_edit, 'w') as fte:
                    fte.write(filedata)

            if len(rest_args) != 2:
                if not local_file:
                    return
                else:
                    rest_args += [local_file]
            if not args.s:
                diff_cmd = (f"git diff --color-words --no-index "
                            f"{_file_to_edit} {rest_args[1]}")
            else:
                diff_cmd = (f"git diff --color-words --no-index "
                            f"{rest_args[1]} {_file_to_edit}")
            # print(diff_cmd)
            shell_cmd_str = shlex.split(diff_cmd)

            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)
            try:
                subprocess.call(shell_cmd_str, preexec_fn=preexec_function)
                signal.signal(signal.SIGINT, old_action)
            except Exception as e:
                print(e)
            os.remove(_file_to_edit)
            return

        # VIM
        if command == 'vim':
            if not rest_args and not args.d:
                print('vim: indicate a file to edit or -d fileA fileB to compare')
                return

            if not rest_args:
                file_to_edit = args.d[0]
            else:
                file_to_edit = rest_args
            self.dev.wr_cmd('from upysh import cat', silent=True)
            files_to_see = f"*{[file_to_edit]}"
            filedata = self.dev.wr_cmd(_CMDDICT_['VIM'].format(files_to_see),
                                       silent=True, rtn_resp=True, multiline=True,
                                       long_string=True)
            # print(filedata)
            _file_to_edit = file_to_edit.rsplit('/')[-1]
            if args.d:
                args.rm = True
                if _file_to_edit in os.listdir():
                    _file_to_edit = f"~{_file_to_edit}"
                    ov = True
                    if len(args.d) == 1:
                        args.d += [file_to_edit.rsplit('/')[-1]]
            if filedata == f'vim: {file_to_edit}: No such file in directory\n':
                filedata = ''
                ov = False
                if _file_to_edit in os.listdir():
                    print(filedata)
                    print('Using local copy...')

            if filedata:
                if _file_to_edit in os.listdir():
                    if not args.o:
                        dev_sha = _shasum_data(filedata.encode('utf-8'))
                        local_sha = shasum(_file_to_edit, debug=False, rtn=True)
                        if dev_sha != local_sha[0][1]:
                            local_file_to_edit = _file_to_edit
                            _file_to_edit = f"~{_file_to_edit}"
                            args.d = [_file_to_edit, local_file_to_edit]
                            args.rm = True
                            ov = True
                        else:
                            ov = False
                    else:
                        ov = True
                else:
                    ov = True
            if not filedata and _file_to_edit not in os.listdir():
                ov = False
            if ov:
                with open(_file_to_edit, 'w') as fte:
                    fte.write(filedata)

            if not args.d:
                shell_cmd_str = shlex.split(f"vim {_file_to_edit}")
            else:
                if len(args.d) != 2:
                    print('indicate two files to compare')
                    return
                shell_cmd_str = shlex.split(f"vim -d {_file_to_edit} {args.d[1]}")

            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)
            try:
                subprocess.call(shell_cmd_str, preexec_fn=preexec_function)
                signal.signal(signal.SIGINT, old_action)
            except Exception as e:
                print(e)

            # Check if file changes:
            if _file_to_edit in os.listdir():
                with open(_file_to_edit, 'r') as fte:
                    filedata2 = fte.read()
                if filedata != filedata2:
                    dst_name = file_to_edit
                    src_name = _file_to_edit
                    self.dsyncio.file_put(src_name, os.stat(src_name)[6], dst_name)
            if args.rm:
                os.remove(_file_to_edit)
            if args.e:
                script_name = file_to_edit.replace('.py', '').rsplit('/')[-1]
                run_cmd = f"import {script_name}"
                print(f'Running {script_name}...')
                try:
                    self.dev.wr_cmd(run_cmd, follow=True)
                except KeyboardInterrupt:
                    self.dev.kbi()
            if args.r:
                module = script_name
                reload_cmd = f"import sys;del(sys.modules['{module}']);gc.collect()"
                print(f'Reloading {file_to_edit}...')
                self.dev.wr_cmd(reload_cmd)
                print('Done!')
            return

        if command == 'enable_sh':
            command = 'update_upyutils'
            rest_args = ['nanoglob.py', 'upysh*.py', 'shasum.py']
        # UPDATE UPYUTILS:
        if command == 'update_upyutils':
            fileargs = FileArgs()
            SRCDIR = os.path.join(_UPYDEVPATH[0], 'upyutils_dir')
            files = nglob(*[os.path.join(SRCDIR, file)
                            for file in rest_args])
            is_lib = self.dev.wr_cmd("import os; 'lib' in os.listdir()",
                                     rtn_resp=True, silent=True)
            if not is_lib:
                print('Making ./lib directory ...')
                self.dev.wr_cmd("os.mkdir('./lib')")
                print('Done!')
            print('Uploading files to ./lib ...')
            fileargs.fre = files
            if self.dev.dev_class == 'SerialDevice':
                from upydev.serialio import SerialFileIO
                if self.dev.dev_platform == 'pyboard':
                    fileargs.s = '/flash/lib'
                else:
                    fileargs.s = '/lib'
                fileio = SerialFileIO(self.dev,
                                      devname=self.dev_name)
                fileio.put_files(fileargs,
                                 self.dev_name
                                 )
            elif self.dev.dev_class == 'WebSocketDevice':
                from upydev.wsio import WebSocketFileIO
                fileargs.wss = self.dev._uriprotocol == 'wss'
                fileargs.s = '/lib'
                fileio = WebSocketFileIO(self.dev, args=fileargs,
                                         devname=self.dev_name)
                fileio.put_files(fileargs,
                                 self.dev_name)
            elif self.dev.dev_class == 'BleDevice':
                from upydev.bleio import BleFileIO
                fileargs.s = '/lib'
                fileio = BleFileIO(self.dev,
                                   devname=self.dev_name)
                fileio.put_files(fileargs,
                                 self.dev_name)
            return

        # SD
        if command == 'sd':
            sd_command(self.dev, rest_args, args)
            return

        # EXIT
        if command == 'exit':
            if args.r:
                print('Rebooting device...')
                self.dev.reset(silent=True, reconnect=False)
                print('Done!')
            elif args.hr:
                print('Device Hard Reset...')
                self.dev.reset(silent=True, reconnect=False, hr=True)
                print('Done!')
            self.flags.exit['exit'] = True

        if command in _SPECIAL_SHELL_CMDS:
            self.custom_sh_cmd(command, rest_args, args, self.topargs, unknown_args)

    def local_sh_cmds(self, command, args, rest_args):
        # DISK USAGE STATISTICS
        if command == 'ldu':
            if not rest_args:
                du(max_dlev=args.d)

            else:
                du_dir = rest_args
                du(path=f'./{du_dir}', max_dlev=args.d)
            return
        # PWD
        if command == 'lpwd':
            print(os.getcwd())

        if command == 'lcd':
            if not rest_args:
                os.chdir(os.environ['HOME'])
            else:
                dir = rest_args
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

    def get_rprompt(self):

        if self.flags.mem_show_rp['call']:
            RAM = self.send_cmd(_CMDDICT_['MEM'], raise_devexcept=True,
                                capture_output=True)

            mem_info = RAM.splitlines()[1]
            mem = {elem.strip().split(':')[0]: int(elem.strip().split(':')[
                              1]) for elem in mem_info[4:].split(',')}
            # print(f"{'Memory':12}{'Size':^12}{'Used':^12}{'Avail':^12}{'Use%':^12}")
            total_mem = mem['total']/1000
            used_mem = mem['used']/1000
            free_mem = mem['free']/1000
            # total_mem_s = f"{total_mem:.3f} kB"
            used_mem_s = f"{used_mem:.3f} kB"
            free_mem_s = f"{free_mem:.3f} kB"
            # percent_mem = f"{(used_mem/total_mem)*100:.1f} %"
            # set used and free
            self.flags.mem_show_rp['used'] = used_mem_s
            self.flags.mem_show_rp['free'] = free_mem_s
            use_percent = round((used_mem/total_mem)*100, 2)
            self.flags.mem_show_rp['percent'] = use_percent
            self.flags.mem_show_rp['call'] = False
        else:
            pass
        if self.flags.mem_show_rp['show']:
            if self.flags.mem_show_rp['percent'] < 85:
                return HTML('<aaa fg="ansiblack" bg="ansiwhite"> RAM </aaa><b><style '
                            'fg="ansigreen"> USED </style></b><aaa fg="ansiblack" '
                            f'bg="ansiwhite"> {self.flags.mem_show_rp["used"]} '
                            '</aaa><b><style '
                            'fg="ansigreen"> FREE </style></b><aaa fg="ansiblack" '
                            f'bg="ansiwhite"> {self.flags.mem_show_rp["free"]} </aaa>')
            else:
                return HTML('<aaa fg="ansiblack" bg="ansiwhite"> RAM </aaa><b><style '
                            'fg="ansired"> USED </style></b><aaa fg="ansiblack" '
                            'bg="ansiwhite">'
                            f' {self.flags.mem_show_rp["used"]} </aaa><b><style '
                            'fg="ansired"> '
                            'FREE </style></b><aaa '
                            'fg="ansiblack" bg="ansiwhite"> '
                            f'{self.flags.mem_show_rp["free"]} </aaa>')
