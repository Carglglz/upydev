import sys
import os
import re

CGREEN = '\33[32;1m'
CEND = '\033[0m'
ABLUE_bold = '\u001b[34;1m'
MAGENTA_bold = '\u001b[35;1m'


def print_table(data, cols=4, wide=16, format_SH=False, autocols=True,
                autocol_tab=False, sort=True, autowide=False, max_cols=4,
                gts=(40, 0)):
    '''Prints formatted data on columns of given width.'''
    if sort:
        data.sort(key=str.lower)
    if format_SH:
        if autocols:
            wide_data = max([len(namefile) for namefile in data]) + 2
            if wide_data > wide:
                wide = wide_data
            columns, rows = gts
            cols = int(columns/(wide))
        data = ['{}{}{}{}'.format(ABLUE_bold, val, CEND, ' '*(wide-len(val)))
                if '.' not in val else val for val in data]
        data = ['{}{}{}{}'.format(MAGENTA_bold, val, CEND, ' '*(wide-len(val)))
                if '.py' not in val and '.mpy'
                not in val and '.' in val else val for val in data]
        data = ['{}{}{}{}'.format(
                CGREEN, val, CEND, ' '*(wide-len(val))) if '.mpy' in val else val
                for val in data]
    if autocol_tab:
        data = [namefile if len(namefile) < wide else namefile
                + '\n' for namefile in data]
    if autowide:
        wide_data = max([len(namefile) for namefile in data]) + 2
        if wide_data > wide:
            wide = wide_data
        columns, rows = gts
        cols = int(columns/(wide))
        if max_cols < cols:
            cols = max_cols
    n, r = divmod(len(data), cols)
    pat = '{{:{}}}'.format(wide)
    line = '\n'.join(pat * cols for _ in range(n))
    last_line = pat * r
    print(line.format(*data))
    print(last_line.format(*data[n*cols:]))


def _print_files(filelist, dir_name, show=True, hidden=False, gts=(40, 0)):
    if show:
        if not hidden:
            filelist = [file for file in filelist if not file.startswith('.')]
        if dir_name != '':
            if os.stat(dir_name)[0] & 0x4000:
                print(f'\n{ABLUE_bold}{dir_name}:{CEND}')
        if filelist:
            print_table(filelist, wide=28, format_SH=True, gts=gts)


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
        root_dir, b_dir = '', dir
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

    def __call__(self, *args, gts=(40, 0), hidden=False, show=True,
                 bydir=True, rtn=False, fullpath=False):
        dir_names_or_pattrn = args
        files_in_dir = []
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
                    dir = ''
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
                                             hidden=hidden, gts=gts)
                            else:
                                files_in_dir += [f"{exp_dir}/{file}" for file
                                                 in _files_in_dir]
                        _files_in_dir = []  # reset
                else:
                    if bydir:
                        files_in_dir = _os_match(pattrn, dir)
                    else:
                        files_in_dir += [f"{dir}/{file}" for file
                                         in _os_match(pattrn, dir)]

            if files_in_dir:
                if bydir:
                    _print_files(files_in_dir, dir_name, show=show,
                                 hidden=hidden, gts=gts)
                    files_in_dir = []  # reset
        if files_in_dir:
            if not fullpath:
                files_in_dir = [file.rsplit('/', 1)[-1] for file in files_in_dir]
            _print_files(files_in_dir, '', show=show, hidden=hidden, gts=gts)
        if rtn:
            return files_in_dir


class PWD:

    def __repr__(self):
        return os.getcwd()

    def __call__(self):
        return self.__repr__()


class CLEAR:
    def __repr__(self):
        return "\x1b[2J\x1b[H"

    def __call__(self):
        return self.__repr__()


pwd = PWD()
ls = LS()
clear = CLEAR()


def cd(dir):
    try:
        os.chdir(dir)
    except Exception:
        print(f'cd: {dir} : is not a directory')


# cd = os.chdir
# mkdir = os.mkdir
mv = os.rename
# rm = os.remove
# rmdir = os.rmdir


def mkdir(*dirs):
    if not dirs:
        print('mkdir: indicate a directory to make')
    for dir in dirs:
        try:
            os.mkdir(dir)
        except OSError:
            pass


def rm(*args):
    if not args:
        print('rm: No such file in directory')
    for file in args:
        try:
            if os.stat(file)[0] & 0x4000:
                print(f'rm: {file}: is a directory, use rmdir')
            else:
                os.remove(file)
        except Exception:
            print(f'rm: {file}: No such file in directory')


def rmdir(*args):
    if not args:
        print('rmdir: No such directory')
    for dir in args:
        try:
            if not os.stat(dir)[0] & 0x4000:
                print(f'rmdir: {dir}: is a file, use rm')
            else:
                os.rmdir(dir)
        except Exception:
            print(f'rmdir: {dir}: No such directory or directory not empty')


def head(f, n=10):
    with open(f) as f:
        for i in range(n):
            l = f.readline()
            if not l:
                break
            sys.stdout.write(l)


def rcat(f, n=1 << 30, buff=256, stream=None):
    with open(f, 'rb') as f:
        for i in range(n):
            if not buff:
                l = f.readline()
            else:
                l = f.read(buff)
            if not l:
                break
            if not stream:
                print(l)
            else:
                bs = 0
                rest = l
                while rest:
                    bs = stream.write(rest)
                    rest = rest[bs:]


def _catfile(files, path, n, prog):
    for filecat in files:
        if path != '':
            print(f'\n\u001b[42;1m{path}/\u001b[44;1m{filecat}:'
                  '\u001b[0m')
            file_str = f"{path}/{filecat}"
        else:
            print(f'\n\u001b[44;1m{filecat}:'
                  '\u001b[0m')
            file_str = f"{filecat}"

        if os.stat(file_str)[0] & 0x4000:
            print(f'{prog}: {file_str}: Is a directory')
        else:
            head(file_str, n)


def cat(*args, n=1 << 30, prog='cat'):
    files_in_dir = []
    for file_name in args:
        if '*' not in file_name:
            try:
                if os.stat(f"{file_name}")[0] & 0x4000:
                    print(f'{prog}: {file_name}: Is a directory')
                else:
                    head(file_name, n)
            except OSError:
                print(f'{prog}: {file_name}: No such file in directory')

        else:
            file_pattrn = file_name.rsplit('/', 1)
            if len(file_pattrn) > 1:
                dir, pattrn = file_pattrn
            else:
                dir = ''
                pattrn = file_pattrn[0]
            dir_name = dir
            # expand dirs
            if '*' in dir_name:
                expanded_dirs = _expand_dirs_recursive(dir_name)
                for exp_dir in expanded_dirs:
                    files_in_dir = _os_match(pattrn, exp_dir)
                    if files_in_dir:
                        _catfile(files_in_dir, exp_dir, n, prog)
                files_in_dir = []
            else:
                files_in_dir = _os_match(pattrn, dir)

            if files_in_dir:
                _catfile(files_in_dir, dir_name, n, prog)


def newfile(path):
    print("Type file contents line by line, finish with EOF (Ctrl+D).")
    with open(path, "w") as f:
        while 1:
            try:
                l = input()
            except EOFError:
                break
            f.write(l)
            f.write("\n")


class Man():

    def __repr__(self):
        return("""
upysh is intended to be imported using:
from upysh import *

To see this help text again, type "man".

upysh commands:
pwd, cd("new_dir"), ls, ls(...), head(...), cat(...)
newfile(...), mv("old", "new"), rm(...), mkdir(...), rmdir(...),
clear
""")


man = Man()

print(man)
