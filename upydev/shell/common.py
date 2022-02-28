# Common functions to all shells

# for fileio operations use IO classes

# repl, iotool

# args

# flags

# login

# shl functions

# keybidings functions

# Prompt loop

# logout

import os
import ast
from upydev.shell.constants import (ABLUE_bold, CGREEN, MAGENTA_bold, CEND)
from prompt_toolkit.formatted_text import HTML
from upydevice import wsprotocol
import re
import socket
import sys
from datetime import timedelta
import time
import select


class FileArgs:
    def __init__(self):
        self.m = ''
        self.t = ''
        self.p = ''
        self.wss = ''
        self.s = ''
        self.f = ''
        self.fre = []
        self.dir = ''


def find_localip():
    ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_soc.connect(('8.8.8.8', 1))
    local_ip = ip_soc.getsockname()[0]
    ip_soc.close()
    return local_ip


def parse_bash_profile():
    ALIASES = {}
    if '.bash_rc' in os.listdir(os.environ['HOME']):
        bash_rc = os.path.join(os.environ['HOME'], '.bash_rc')
        with open(bash_rc, 'r') as bf:
            bf_content = bf.read()
            bf_alias = [alias_line for alias_line in bf_content.splitlines()
                        if alias_line.startswith('alias')]

        for alias in bf_alias:
            alias_key = alias.split('=')[0].replace('alias', '').strip()
            try:
                alias_value = ast.literal_eval(alias.split('=')[1])
            except Exception:
                alias_value = alias.split('=')[1].split()[0]
            ALIASES[alias_key] = alias_value

    if '.profile' in os.listdir(os.environ['HOME']):
        profile = os.path.join(os.environ['HOME'], '.profile')
        with open(profile, 'r') as pf:
            pf_content = pf.read()
            pf_alias = [alias_line for alias_line in pf_content.splitlines()
                        if alias_line.startswith('alias')]

        for alias in pf_alias:
            alias_key = alias.split('=')[0].replace('alias', '').strip()
            try:
                alias_value = ast.literal_eval(alias.split('=')[1])
            except Exception:
                alias_value = alias.split('=')[1].split()[0]
            ALIASES[alias_key] = alias_value
    return ALIASES


def parse_bash_profile_functions():
    ALIASES = {}
    if '.bash_rc' in os.listdir(os.environ['HOME']):
        bash_rc = os.path.join(os.environ['HOME'], '.bash_rc')
        with open(bash_rc, 'r') as bf:
            bf_content = bf.read()
            bf_alias = [alias_line for alias_line in bf_content.splitlines()
                        if alias_line.startswith('function')]

        for alias in bf_alias:
            alias_key = alias.split(' ')[1].replace('()', '').strip()
            try:
                alias_value = f"{alias} && {alias_key}"
            except Exception:
                pass
            ALIASES[alias_key] = alias_value

    if '.profile' in os.listdir(os.environ['HOME']):
        profile = os.path.join(os.environ['HOME'], '.profile')
        with open(profile, 'r') as pf:
            pf_content = pf.read()
            pf_alias = [alias_line for alias_line in pf_content.splitlines()
                        if alias_line.startswith('function')]

        for alias in pf_alias:
            alias_key = alias.split(' ')[1].replace('()', '').strip()
            try:
                alias_value = f"{alias} && {alias_key}"
            except Exception:
                pass
            ALIASES[alias_key] = alias_value
    return ALIASES


SHELL_ALIASES = parse_bash_profile()
SHELL_FUNCTIONS = parse_bash_profile_functions()
# TAB OPTIONS FORMATTER


# from @The Data Scientician : https://stackoverflow.com/questions/9535954/printing-lists-as-tabular-data
def print_table(data, cols=4, wide=16, format_SH=False, autocols=True,
                autocol_tab=False, sort=True, autowide=False, max_cols=4):
    '''Prints formatted data on columns of given width.'''
    if sort:
        data.sort(key=str.lower)
    if format_SH:
        if autocols:
            wide_data = max([len(namefile) for namefile in data]) + 2
            if wide_data > wide:
                wide = wide_data
            columns, rows = os.get_terminal_size(0)
            cols = int(columns/(wide))
        data = ['{}{}{}{}'.format(ABLUE_bold, val, CEND, ' '*(wide-len(val)))
                if '.' not in val else val for val in data]
        data = ['{}{}{}{}'.format(MAGENTA_bold, val, CEND, ' '*(wide-len(val)))
                if '.py' not in val and '.mpy' not in val and '.' in val else val for val in data]
        data = ['{}{}{}{}'.format(
            CGREEN, val, CEND, ' '*(wide-len(val))) if '.mpy' in val else val for val in data]
    if autocol_tab:
        data = [namefile if len(namefile) < wide else namefile
                + '\n' for namefile in data]
    if autowide:
        wide_data = max([len(namefile) for namefile in data]) + 2
        if wide_data > wide:
            wide = wide_data
        columns, rows = os.get_terminal_size(0)
        cols = int(columns/(wide))
        if max_cols < cols:
            cols = max_cols
    n, r = divmod(len(data), cols)
    pat = '{{:{}}}'.format(wide)
    line = '\n'.join(pat * cols for _ in range(n))
    last_line = pat * r
    print(line.format(*data))
    print(last_line.format(*data[n*cols:]))


def getitem(s, depth=0):  # https://rosettacode.org/wiki/Brace_expansion#Python
    out = [""]
    while s:
        c = s[0]
        if depth and (c == ',' or c == '}'):
            return out, s
        if c == '{':
            x = getgroup(s[1:], depth+1)
            if x:
                out, s = [a+b for a in out for b in x[0]], x[1]
                continue
        if c == '\\' and len(s) > 1:
            s, c = s[1:], c + s[1]

        out, s = [a+c for a in out], s[1:]

    return out, s


def getgroup(s, depth):
    out, comma = [], False
    while s:
        g, s = getitem(s, depth)
        if not s:
            break
        out += g

        if s[0] == '}':
            if comma:
                return out, s[1:]
            return ['{' + a + '}' for a in out], s[1:]

        if s[0] == ',':
            comma, s = True, s[1:]

    return None


# SHELL COMMANDS HANDLERS


def map_upysh(cmd_inp):
    frst_cmd = cmd_inp.split(' ')[0]
    if len(cmd_inp.split(' ')) > 1:
        scnd_cmd = cmd_inp.split(' ')[1]
        if scnd_cmd != '':
            shell_cmd = "{}('{}')".format(frst_cmd, scnd_cmd)
            if '*' in scnd_cmd and frst_cmd in ['rm', 'cat', 'head', 'rmdir']:
                pattrn = scnd_cmd.replace('*', '')
                shell_cmd = f"__ = list(map({frst_cmd}, [f for f in os.listdir(os.getcwd()) if '{pattrn}' in f]))"
    else:
        shell_cmd = frst_cmd

    if shell_cmd == 'sz':
        shell_cmd = 'ls()'
    if frst_cmd == 'run':
        shell_cmd = 'import {}'.format(scnd_cmd.split('.')[0])
        # make a run interactive mode that do not escape input
        # conditional ENTER, flush buffer, send run command, then CTRL-C can
        # be catched, print in terminal
    if shell_cmd == 'cd':
        shell_cmd = "cd('/')"
    return shell_cmd, frst_cmd


def _dt_format(number):
    rtc_n = str(number)
    if len(rtc_n) == 1:
        rtc_n = "0{}".format(rtc_n)
        return rtc_n
    else:
        return rtc_n


def _ft_datetime(t_now):
    return([_dt_format(i) for i in t_now])


def sortSecond(val):
    return val[1]


def _print_files(filelist, dir_name, show=True, hidden=False):
    if show:
        if not hidden:
            filelist = [file for file in filelist if not file.startswith('.')]
        if dir_name != '.':
            if os.stat(dir_name)[0] & 0x4000:
                print(f'\n{ABLUE_bold}{dir_name.replace(os.getcwd(), ".")}:{CEND}')
        if filelist:
            print_table(filelist, wide=28, format_SH=True)


def _expand_dirs_recursive(dir):
    if '*' not in dir:
        return [dir]
    if len(dir.split('/')) > 1:
        dir_matchs = []
        root_dir, b_dir = dir.rsplit('/', 1)
        for _rdir in _expand_dirs_recursive(root_dir):
            dir_matchs += _os_match_dir(b_dir, _rdir)
        return dir_matchs
    else:
        root_dir, b_dir = '.', dir
        return _os_match_dir(b_dir, root_dir)


def _os_match(patt, path):
    pattrn = re.compile(patt.replace('.', r'\.').replace('*', '.*') + '$')
    return [file for file in os.listdir(path) if pattrn.match(file)]


def _os_match_dir(patt, path):
    pattrn = re.compile(patt.replace('.', r'\.').replace('*', '.*') + '$')
    if path == '' and os.getcwd() != '/':
        path = os.getcwd()
    return [f"{path}/{dir}" for dir in os.listdir(path) if pattrn.match(dir)
            and os.stat(f"{path}/{dir}")[0] & 0x4000]


class LS:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, *args, hidden=False, show=True, rtn=False, bydir=True):
        dir_names_or_pattrn = args
        files_in_dir = []
        all_files = []
        for dir_name in dir_names_or_pattrn:
            if '*' not in dir_name and '/' not in dir_name:
                try:
                    st = os.stat(dir_name)
                    if st[0] & 0x4000:  # stat.S_IFDIR
                        files_in_dir = os.listdir(dir_name)
                    else:
                        if dir_name in os.listdir(os.getcwd()):
                            files_in_dir.append(dir_name)
                except OSError:
                    print(f'ls: {dir_name}: No such a file or directory')

            else:
                dir_pattrn = dir_name.rsplit('/', 1)
                if len(dir_pattrn) > 1:
                    dir, pattrn = dir_pattrn
                else:
                    dir = '.'
                    pattrn = dir_pattrn[0]
                dir_name = dir
                # expand dirs
                if '*' in dir_name:
                    expanded_dirs = _expand_dirs_recursive(dir_name)
                    for exp_dir in expanded_dirs:
                        _files_in_dir = _os_match(pattrn, exp_dir)
                        if _files_in_dir:
                            if bydir:
                                _print_files(_files_in_dir, exp_dir, show=show,
                                             hidden=hidden)
                            else:
                                files_in_dir += [f"{exp_dir.replace(os.getcwd(), '')}"
                                                 f"/{file}".replace('./', '', 1)
                                                 for file in _files_in_dir]

                        _files_in_dir = []
                else:
                    if bydir:
                        files_in_dir = _os_match(pattrn, dir)
                    else:
                        files_in_dir += [f"{dir.replace(os.getcwd(), '')}"
                                         f"/{file}".replace('./', '', 1)
                                         for file in _os_match(pattrn, dir)]

            if files_in_dir:
                if bydir:
                    _print_files(files_in_dir, dir_name, show=show, hidden=hidden)
                    files_in_dir = []
        if files_in_dir:
            _print_files(files_in_dir, '.', show=show, hidden=hidden)
        if rtn:
            return files_in_dir


ls = LS()


class LTREE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", level=0, is_last=False, is_root=True,
                 carrier="│", hidden=False):
        if is_root:
            current_dir = os.getcwd()
            if path != '.':
                try:
                    if os.stat(path)[0] & 0x4000:
                        print(f'\u001b[34;1m{path}\033[0m')
                    else:
                        print(f'tree: {path}: Not a directory')
                        return
                except OSError:
                    print(f'tree: {path}: Not such directory')
                    return
            else:
                print(f'\u001b[34;1m{path}\033[0m')
        try:
            os.chdir(path)
        except OSError:
            print(f'tree: {path}: Not a directory')
            return
        r_path = path
        path = "."
        if hidden:
            l = os.listdir(path)
        else:
            l = [f for f in os.listdir(path) if not f.startswith('.')]
        nf = len([file for file in l if not os.stat(
            "%s/%s" % (path, file))[0] & 0x4000])
        nd = len(l) - nf
        ns_f, ns_d = 0, 0
        l.sort()
        if len(l) > 0:
            last_file = l[-1]
        else:
            last_file = ''
        for f in l:
            st = os.stat("%s/%s" % (path, f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print(self._treeindent(level, f, last_file, is_last=is_last,
                                       carrier=carrier) + " \u001b[34;1m%s\033[0m" % f)
                if f == last_file and level == 0:
                    carrier = "   "
                os.chdir(f)
                level += 1
                lf = last_file == f
                if level > 1:
                    if lf:
                        carrier += "    "
                    else:
                        carrier += "   │"
                ns_f, ns_d = self.__call__(level=level, is_last=lf,
                                           is_root=False, carrier=carrier,
                                           hidden=hidden)
                if level > 1:
                    carrier = carrier[:-4]
                os.chdir('..')
                level += (-1)
                nf += ns_f
                nd += ns_d
            else:
                print(self._treeindent(level, f, last_file,
                                       is_last=is_last, carrier=carrier) + " %s" % (f))
        if is_root:
            nd_str = 'directories'
            nf_str = 'files'
            if nd == 1:
                nd_str = 'directory'
            if nf == 1:
                nf_str = 'file'
            print('\n{} {}, {} {}'.format(nd, nd_str, nf, nf_str))
            if r_path != ".":
                os.chdir('..')
            if os.getcwd() != current_dir:
                os.chdir(current_dir)
        else:
            return (nf, nd)

    def _treeindent(self, lev, f, lastfile, is_last=False, carrier=None):
        if lev == 0:
            if f != lastfile:
                return "├──"
            else:
                return "└──"
        else:
            if f != lastfile:
                return carrier + "   ├──"
            else:
                return carrier + "   └──"


tree = LTREE()


class DISK_USAGE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", dlev=0, max_dlev=0, hidden=False, absp=True):
        if path != ".":
            if not os.stat(path)[0] & 0x4000:
                print('{:9} {}'.format(
                        self.print_filesys_info(os.stat(path)[6]), path))
            else:
                if hidden:
                    resp = {
                        path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path)}
                else:
                    resp = {
                        path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
                for dir in resp.keys():

                    if not os.stat(dir)[0] & 0x4000:
                        if absp:
                            print('{:9} {}'.format(
                                self.print_filesys_info(resp[dir]), dir))
                        else:
                            print('{:9} {}'.format(self.print_filesys_info(
                                resp[dir]), dir.split('/')[-1]))

                    else:
                        if dlev < max_dlev:
                            dlev += 1
                            self.__call__(path=dir, dlev=dlev,
                                          max_dlev=max_dlev, hidden=hidden)
                            dlev += (-1)
                        else:
                            if absp:
                                print('{:9} \u001b[34;1m{}\033[0m'.format(
                                    self.print_filesys_info(self.get_dir_size_recursive(dir)), dir))
                            else:
                                print('{:9} \u001b[34;1m{}\033[0m'.format(self.print_filesys_info(
                                    self.get_dir_size_recursive(dir)), dir.split('/')[-1]))

        else:
            if hidden:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)
                        [6] for dir in os.listdir(path)}
            else:
                resp = {
                    path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
            for dir in resp.keys():

                if not os.stat(dir)[0] & 0x4000:
                    print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir))

                else:
                    if dlev < max_dlev:
                        dlev += 1
                        self.__call__(path=dir, dlev=dlev,
                                      max_dlev=max_dlev, hidden=hidden)
                        dlev += (-1)
                    else:
                        print('{:9} \u001b[34;1m{}\033[0m'.format(
                            self.print_filesys_info(self.get_dir_size_recursive(dir)), dir))

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

    def get_dir_size_recursive(self, dir):
        return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0]
                    & 0x4000 else self.get_dir_size_recursive(dir+'/'+f)
                    for f in os.listdir(dir)])


du = DISK_USAGE()


class CatFileIO:
    def __init__(self, dev=None):
        self.buff = bytearray(1024*2)
        self.bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
        self.columns, self.rows = os.get_terminal_size(0)
        self.cnt_size = 65
        self.bar_size = int((self.columns - self.cnt_size))
        self.pb = False
        self.wheel = ['|', '/', '-', "\\"]
        self.filesize = 0
        self.filename = ''
        self.file_buff = b''
        self.cnt = 0
        self.t_start = 0
        self.percentage = 0
        self.dev = dev
        self._commandline = 0
        self._hf_index = 0
        self._shafiles = []

    def enter_raw_repl(self):
        self.dev.serial.write(b"\r\x01")
        data = self.dev.serial.read_until(b"raw REPL; CTRL-B to exit\r\n")
        assert data.endswith(b"raw REPL; CTRL-B to exit\r\n"), f"wrong data: {data}"

    def exit_raw_repl(self):
        self.dev.serial.write(b"\r\x02")  # ctrl-B: enter friendly REPL
        self.dev.serial.read_until(b'\r\n>>> ')

    def exec_raw_cmd(self, command):
        # check we have a prompt
        if not isinstance(command, bytes):
            command = command.encode('utf-8')
        command += b'\r'
        data = self.dev.serial.read_until(b">")
        assert data.endswith(b">"), f"wrong data: {data}"
        for i in range(0, len(command), 256):
            self.dev.serial.write(command[i:min(i + 256, len(command))])
            time.sleep(0.01)
        self.dev.serial.write(b"\x04")

        # check if we could exec command
        data = self.dev.serial.read_until(b"OK")
        assert b"OK" in data, f"Command failed: {command}: data: {data}"
        data = self.dev.serial.read_until(b"\x04\x04")
        assert data == b"\x04\x04", f"Command failed: {command}: data: {data}"

    def init_put(self, filename, filesize, cnt=0):
        self.file_buff = b''
        self.filesize = filesize
        self.filename = filename
        self.cnt = cnt
        self.get_pb()
        self.t_start = time.time()

    def sraw_put_file(self, src, dest, chunk_size=256):
        try:
            self.enter_raw_repl()
            # time.sleep(0.1)
            # print(f"source: {src}")
            # print(f"dest: {dest}")
            self.exec_raw_cmd(f"f=open('{dest}','wb')\nw=f.write")
            if self.filesize == 0:
                self.exec_raw_cmd("f.close()")
                self.exit_raw_repl()
                print('\n')
                return
            # time.sleep(0.1)
            with open(src, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break

                    self.exec_raw_cmd("w(" + repr(data) + ")")
                    self.cnt += len(data)
                    self.file_buff += data
                    loop_index_f = (self.cnt/self.filesize)*self.bar_size
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
                    percentage = self.cnt / self.filesize
                    self.percentage = int((percentage)*100)
                    t_elapsed = time.time() - self.t_start
                    t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
                    ett = self.filesize / (self.cnt / t_elapsed)
                    if self.pb:
                        self.do_pg_bar(loop_index, self.wheel,
                                       nb_of_total, t_speed, t_elapsed,
                                       loop_index_l, percentage, ett)

            self.exec_raw_cmd("f.close()")
            self.exit_raw_repl()
            print('\n')
        except (Exception, KeyboardInterrupt):
            print('flushing serial')
            self.exit_raw_repl()
            self.dev.flush_conn()
            time.sleep(0.5)
            self.dev.serial.write(self.dev._banner)
            self.dev.serial.read_until(b'\r\n>>> ')
            raise Exception

    def sr_get_file(self, cmd, filter_cmd=True):
        self.dev._is_traceback = False
        self.dev.response = ''
        self.dev.output = None
        self.dev.flush_conn()
        self.dev.buff = b''
        self.bytes_sent = self.dev.serial.write(bytes(cmd + '\r', 'utf-8'))
        end_prompt = b''
        if filter_cmd:
            # cmd_filt = bytes(cmd + '\r\n', 'utf-8')
            _cmd_filt_buff = b''
            while b'\r\n' not in _cmd_filt_buff:
                _cmd_filt_buff += self.dev.serial.read_until(b'\r\n')
            recv_cmd, rest = _cmd_filt_buff.split(b'\r\n')
            try:
                assert recv_cmd == bytes(cmd, 'utf-8'), "Command missmatch"
            except Exception:
                print(f'command: {cmd}')
                print(f'recv command: {recv_cmd}')
                print(f'rest: {rest}')
                raise Exception
            if rest:
                self.file_buff += rest.replace(b'\r', b'')
                self.cnt += len(rest.replace(b'\r', b''))
        try:
            while len(self.file_buff) < self.filesize:
                data = self.dev.serial.read_until(b'\r\n').replace(b'\r\n', b'')
                data = ast.literal_eval(data.decode())  # shielded bytes
                if data:
                    if len(self.file_buff + data) <= self.filesize:
                        pass
                    else:
                        offset = len(self.file_buff + data) - self.filesize
                        data, end_prompt = data[:-offset], data[-offset:]
                        assert len(self.file_buff + data) == self.filesize, "Missmatch"
                    self.cnt += len(data)
                    self.file_buff += data
                    loop_index_f = (self.cnt/self.filesize)*self.bar_size
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
                    percentage = self.cnt / self.filesize
                    self.percentage = int((percentage)*100)
                    t_elapsed = time.time() - self.t_start
                    t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
                    ett = self.filesize / (self.cnt / t_elapsed)
                    if self.pb:
                        self.do_pg_bar(loop_index, self.wheel,
                                       nb_of_total, t_speed, t_elapsed,
                                       loop_index_l, percentage, ett)

                if len(self.file_buff) == self.filesize:
                    # assert end_prompt
                    while self.dev.prompt not in end_prompt:
                        end_prompt += self.dev.serial.read_all()
                    break

            assert self.dev.prompt in end_prompt, "Prompt not buffered"

        except KeyboardInterrupt:
            # print(len(self.file_buff), self.filesize)
            # print(self.file_buff.decode)
            # time.sleep(0.2)
            self.dev.kbi(silent=True)
            time.sleep(0.2)
            for i in range(1):
                self.dev.serial.write(b'\r')
                self.dev.flush_conn()
            raise KeyboardInterrupt

    def ws_readline(self, eof=b'\r\n'):
        self.dev.ws.sock.settimeout(10)
        buffdata = b''
        while eof not in buffdata:
            try:
                fin, opcode, data = self.dev.ws.read_frame()
                buffdata += data
            except AttributeError:
                pass
        return buffdata

    def flush(self):
        self.dev.ws.sock.settimeout(0.1)
        self._flush = b''
        data = 1
        while data:
            try:
                fin, opcode, data = self.dev.ws.read_frame()
                self._flush += data
            except socket.timeout:
                break
            except wsprotocol.NoDataException:
                break

    def ws_get_file(self, cmd, filter_cmd=True):
        self.dev._is_traceback = False
        self.dev.response = ''
        self.dev.output = None
        # for i in range(2):
        self.flush()
        self.dev.buff = b''
        self.bytes_sent = self.dev.write(cmd+'\r')
        end_prompt = b''
        if filter_cmd:
            # len_cmd_filt = len(bytes(cmd + '\r\n', 'utf-8'))
            _cmd_filt_buff = b''
            while b'\r\n' not in _cmd_filt_buff:
                _cmd_filt_buff += self.ws_readline()
            recv_cmd, rest = _cmd_filt_buff.split(b'\r\n')
            try:
                assert recv_cmd == bytes(cmd, 'utf-8'), "Command missmatch"
            except Exception:
                print(f'command: {cmd}')
                print(f'recv command: {recv_cmd}')
                print(f'rest: {rest}')
                raise Exception
            # assert not rest, f"This is rest: [{rest}] "
            if rest:
                self.file_buff += rest.replace(b'\r', b'')
                self.cnt += len(rest.replace(b'\r', b''))

        try:
            while len(self.file_buff) < self.filesize:
                try:
                    fin, opcode, data = self.dev.ws.read_frame()
                except AttributeError:
                    pass
                # data = self.ws_readline().replace(b'\r\n', b'')
                # data = ast.literal_eval(data.decode())  # shielded bytes
                if data:
                    data = data.replace(b'\r', b'')
                    if len(self.file_buff + data) <= self.filesize:
                        pass
                    else:
                        offset = len(self.file_buff + data) - self.filesize
                        data, end_prompt = data[:-offset], data[-offset:]
                        assert len(self.file_buff + data) == self.filesize, "Missmatch"
                    self.cnt += len(data)
                    self.file_buff += data
                    loop_index_f = (self.cnt/self.filesize)*self.bar_size
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
                    percentage = self.cnt / self.filesize
                    self.percentage = int((percentage)*100)
                    t_elapsed = time.time() - self.t_start
                    t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
                    ett = self.filesize / (self.cnt / t_elapsed)
                    if self.pb:
                        self.do_pg_bar(loop_index, self.wheel,
                                       nb_of_total, t_speed, t_elapsed,
                                       loop_index_l, percentage, ett)
                if len(self.file_buff) == self.filesize:
                    # assert end_prompt
                    while self.dev.prompt not in end_prompt:
                        try:
                            fin, opcode, data = self.dev.ws.read_frame()
                        except AttributeError:
                            pass
                        end_prompt += data
                    # self.flush()
                    break
            assert self.dev.prompt in end_prompt, "Prompt not buffered"
            self.flush()

        except KeyboardInterrupt:
            # time.sleep(0.2)
            self.dev.kbi(silent=True)
            time.sleep(0.2)
            for i in range(1):
                self.dev.write('\r')
                self.dev.flush_conn()

            raise KeyboardInterrupt

    def rs_get_file(self, cmd, filter_cmd=True, chunk=256):
        self.dev._is_traceback = False
        self.dev.response = ''
        self.dev.output = None
        get_soc = [self.dev.ws.sock]
        self.flush()
        self.dev.buff = b''
        self.bytes_sent = self.dev.write(cmd+'\r')
        chunk = chunk * 2
        end_prompt = b''
        if filter_cmd:
            # len_cmd_filt = len(bytes(cmd + '\r\n', 'utf-8'))
            _cmd_filt_buff = b''
            while b'\r\n' not in _cmd_filt_buff:
                _cmd_filt_buff += self.ws_readline()
            recv_cmd, rest = _cmd_filt_buff.split(b'\r\n')
            try:
                assert recv_cmd == bytes(cmd, 'utf-8'), "Command missmatch"
            except Exception:
                print(f'command: {cmd}')
                print(f'recv command: {recv_cmd}')
                print(f'rest: {rest}')
                raise Exception
            assert not rest, f"This is rest: [{rest}] "
            # if rest:
            #     self.file_buff += rest.replace(b'\r', b'')
            #     self.cnt += len(rest.replace(b'\r', b''))

        try:
            self.dev.ws.sock.settimeout(0)
            while len(self.file_buff) < self.filesize:
                data = b''
                try:
                    readable, writable, exceptional = select.select(get_soc,
                                                                    get_soc,
                                                                    get_soc)
                    if readable:
                        # if self.filesize - len(self.file_buff) < chunk:
                        #     chunk = self.filesize - len(self.file_buff)
                        data = self.dev.ws.sock.recv(chunk)
                except Exception:
                    # print(e)
                    time.sleep(0.01)
                if data:
                    # data = data.replace(b'\r', b'')
                    if len(self.file_buff + data) <= self.filesize:
                        pass
                    else:
                        offset = len(self.file_buff + data) - self.filesize
                        data, end_prompt = data[:-offset], data[-offset:]
                        assert len(self.file_buff + data) == self.filesize, "Missmatch"
                    self.cnt += len(data)
                    self.file_buff += data
                    loop_index_f = (self.cnt/self.filesize)*self.bar_size
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
                    percentage = self.cnt / self.filesize
                    self.percentage = int((percentage)*100)
                    t_elapsed = time.time() - self.t_start
                    t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
                    ett = self.filesize / (self.cnt / t_elapsed)
                    if self.pb:
                        self.do_pg_bar(loop_index, self.wheel,
                                       nb_of_total, t_speed, t_elapsed,
                                       loop_index_l, percentage, ett)
                if len(self.file_buff) == self.filesize:
                    # assert end_prompt
                    self.dev.ws.sock.settimeout(10)
                    while self.dev.prompt not in end_prompt:
                        try:
                            fin, opcode, data = self.dev.ws.read_frame()
                        except AttributeError:
                            pass
                        end_prompt += data
                    # self.flush()
                    break
            assert self.dev.prompt in end_prompt, "Prompt not buffered"
            self.flush()

        except KeyboardInterrupt:
            # time.sleep(0.2)
            self.dev.kbi(silent=True)
            time.sleep(0.2)
            for i in range(1):
                self.dev.write('\r')
                self.dev.flush_conn()

            raise KeyboardInterrupt

    def rble_get_file_callback(self):
        pass
        # callback receives notification with chunks of file
        # and save to file buff
        # use rcat stream and uart.write

    def rble_get_file(self, cmd, filter_cmd=True, chunk=256):
        pass

    def get_pb(self):
        self.columns, self.rows = os.get_terminal_size(0)
        if self.columns > self.cnt_size:
            self.bar_size = int((self.columns - self.cnt_size))
            self.pb = True
        else:
            self.bar_size = 1
            self.pb = False

    def do_pg_bar(self, index, wheel, nb_of_total, speed, time_e, loop_l,
                  percentage, ett):
        l_bloc = self.bloc_progress[loop_l]
        if index == self.bar_size:
            l_bloc = "█"
        sys.stdout.write("\033[K")
        print('▏{}▏{:>2}{:>5} % | {} | '
              '{:>5} kB/s | {}/{} s'.format("█" * index + l_bloc + " "*((self.bar_size+1) - len("█" * index + l_bloc)),
                                            wheel[index % 4],
                                            int((percentage)*100),
                                            nb_of_total, speed,
                                            str(timedelta(seconds=time_e)).split(
                                                                        '.')[0][2:],
                                            str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
        sys.stdout.flush()

    def init_get(self, filename, filesize, cnt=0):
        self.file_buff = b''
        self.filesize = filesize
        self.filename = filename
        self.cnt = cnt
        self.get_pb()
        self.t_start = time.time()
        self._commandline = 0
        with open(self.filename, 'w') as f:
            pass

    def get(self, data, std=True, exec_prompt=False):
        if std != 'stderr':
            # data.replace(b'\r\n', b'')
            # data = ast.literal_eval(data.decode())  # shielded bytes
            data = data.encode()
            with open(self.filename, 'ab') as f:
                if data == b'':
                    return
                if (self.cnt + len(data)) > self.filesize:
                    offset = (self.cnt + len(data)) - self.filesize
                    data = data[:-offset]
                self.cnt += len(data)
                f.write(data)
                loop_index_f = (self.cnt/self.filesize)*self.bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
                percentage = self.cnt / self.filesize
                self.percentage = int((percentage)*100)
                t_elapsed = time.time() - self.t_start
                t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
                ett = self.filesize / (self.cnt / t_elapsed)
                if self.pb:
                    self.do_pg_bar(loop_index, self.wheel,
                                   nb_of_total, t_speed, t_elapsed,
                                   loop_index_l, percentage, ett)
        if exec_prompt:
            print('')

    def show_pgb(self, data, std=True, exec_prompt=False):
        if std != 'stderr':
            data = data.encode()
            if not self._commandline:
                self._commandline = len(self.dev.raw_buff.splitlines()[0])
            # with open(self.filename, 'ab') as f:
            if data == b'':
                return
            self.cnt = len(self.dev.raw_buff) - self._commandline
            if self.cnt > self.filesize:
                self.cnt = self.filesize
            # f.write(data)
            loop_index_f = (self.cnt/self.filesize)*self.bar_size
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
            percentage = self.cnt / self.filesize
            self.percentage = int((percentage)*100)
            t_elapsed = time.time() - self.t_start
            t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
            ett = self.filesize / (self.cnt / t_elapsed)
            if self.pb:
                self.do_pg_bar(loop_index, self.wheel,
                               nb_of_total, t_speed, t_elapsed,
                               loop_index_l, percentage, ett)
        if exec_prompt:
            pass

    def show_pgb_alt(self, data, std=True, exec_prompt=False):
        if std != 'stderr':
            data = data.encode()
            # with open(self.filename, 'ab') as f:
            if data == b'':
                return
            self.cnt = len(self.dev.buff)
            if self.cnt > self.filesize:
                self.cnt = self.filesize
            # f.write(data)
            loop_index_f = (self.cnt/self.filesize)*self.bar_size
            loop_index = int(loop_index_f)
            loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
            nb_of_total = f"{self.cnt/(1000):.2f}/{self.filesize/(1000):.2f} kB"
            percentage = self.cnt / self.filesize
            self.percentage = int((percentage)*100)
            t_elapsed = time.time() - self.t_start
            t_speed = f"{(self.cnt/(1000))/t_elapsed:^2.2f}"
            ett = self.filesize / (self.cnt / t_elapsed)
            if self.pb:
                self.do_pg_bar(loop_index, self.wheel,
                               nb_of_total, t_speed, t_elapsed,
                               loop_index_l, percentage, ett)
        if exec_prompt:
            pass
            # print('')

    def save_file(self):
        with open(self.filename, 'ab') as f:
            f.write(self.file_buff[:self.filesize])

    def init_sha(self, prog='dsync'):
        self._hf_index = 0
        self._shafiles = []
        self._prog = prog
        self.get_pb()

    def end_sha(self):
        print(' ' * self.columns, end='\r')
        sys.stdout.write("\033[A")
        print(' ' * self.columns, end='\r')

    def shapipe(self, data, std=True, **kargs):
        if std != 'stderr' and data != '\n':

            sys.stdout.write("\033[K")
            sys.stdout.write("\033[A")
            print(f"{self._prog}: checking filesystem... "
                  f"{self.wheel[self._hf_index % 4]}")
            if data.endswith('\n'):
                data = data[:-1]
            total_ln = len(data)
            try:
                hf, name, sz = data.split()
            except Exception:
                print(f"shapipe: data: {data}")
                raise Exception
                # return
            if total_ln <= (self.columns - 2):
                print(f"{hf} {name} {sz}", end='\r')
            else:  # short hf
                ixhf = int((len(hf) - ((total_ln - (self.columns - 2)) + 3)) / 2)
                print(f"{hf[:ixhf]}...{hf[-ixhf:]} {name} {sz}", end='\r')
            sys.stdout.flush()
            self._shafiles.append((name, int(sz), hf))
            self._hf_index += 1


def get_dir_size_recursive(dir):
    return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0]
                & 0x4000 else get_dir_size_recursive(dir+'/'+f)
                for f in os.listdir(dir)])


def print_size(name, sz, nl=False):
    if not nl:
        if sz:
            print(f'- {name} [{sz/1000:.2f} kB]')
        else:
            print(f'- {name} [{sz:.2f} kB]')
    else:
        if sz:
            print(f'\n{name} [{sz/1000:.2f} kB]')
        else:
            print(f'\n{name} [{sz:.2f} kB]')


def check_filetype(file):
    if not file.endswith('.py') and not file.endswith('.txt'):
        return True
    return False


def get_rprompt(mem_show_rp, shll):

    if mem_show_rp['call']:

        RAM = shll.send_custom_sh_cmd(
            'from micropython import mem_info;mem_info()', True)
        mem_info = RAM.splitlines()[1]
        mem = {elem.strip().split(':')[0]: int(elem.strip().split(':')[
                          1]) for elem in mem_info[4:].split(',')}
        used_mem = mem['used']/1000
        free_mem = mem['free']/1000
        used_mem_s = "{:.3f} kB".format(used_mem)
        free_mem_s = "{:.3f} kB".format(free_mem)
        # set used and free
        mem_show_rp['used'] = used_mem_s
        mem_show_rp['free'] = free_mem_s
        total_mem = mem['total']/1000
        use_percent = round((used_mem/total_mem)*100, 2)
        mem_show_rp['percent'] = use_percent
        mem_show_rp['call'] = False
    else:
        pass

    if mem_show_rp['percent'] < 85:
        return HTML('<aaa fg="ansiblack" bg="ansiwhite"> RAM </aaa><b><style '
                    'fg="ansigreen"> USED </style></b><aaa fg="ansiblack" '
                    f'bg="ansiwhite"> {mem_show_rp["used"]} </aaa><b><style '
                    'fg="ansigreen"> FREE </style></b><aaa fg="ansiblack" '
                    f'bg="ansiwhite"> {mem_show_rp["free"]} </aaa>')
    else:
        return HTML('<aaa fg="ansiblack" bg="ansiwhite"> RAM </aaa><b><style '
                    'fg="ansired"> USED </style></b><aaa fg="ansiblack" bg="ansiwhite">'
                    f' {mem_show_rp["used"]} </aaa><b><style fg="ansired"> '
                    'FREE </style></b><aaa '
                    f'fg="ansiblack" bg="ansiwhite"> {mem_show_rp["free"]} </aaa>')
