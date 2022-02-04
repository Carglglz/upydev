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
import re
import socket


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


SHELL_ALIASES = parse_bash_profile()
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
                 carrier="│   ", hidden=False):
        if is_root:
            print('\u001b[34;1m{}\033[0m'.format(path))
        os.chdir(path)
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
                                       carrier=carrier) + "  \u001b[34;1m%s\033[0m" % f)
                if f == last_file and level == 0:
                    carrier = "    "
                os.chdir(f)
                level += 1
                lf = last_file == f
                if level > 1:
                    if lf:
                        carrier += "     "
                    else:
                        carrier += "    │"
                ns_f, ns_d = self.__call__(level=level, is_last=lf,
                                           is_root=False, carrier=carrier,
                                           hidden=hidden)
                if level > 1:
                    carrier = carrier[:-5]
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
                return carrier + "    ├────"
            else:
                return carrier + "    └────"


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


def get_dir_size_recursive(dir):
    return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0]
                & 0x4000 else get_dir_size_recursive(dir+'/'+f)
                for f in os.listdir(dir)])


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
