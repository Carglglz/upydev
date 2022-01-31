import sys
import os
import re

CRED = '\033[91;1m'
CGREEN = '\33[32;1m'
CEND = '\033[0m'
YELLOW = '\u001b[33m'
BCYAN = '\u001b[36;1m'
ABLUE_bold = '\u001b[34;1m'
MAGENTA_bold = '\u001b[35;1m'
WHITE_ = '\u001b[37m'
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"


class LS:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, *args, gts=(40, 0), hidden=False, show=True, rtn=False):
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
                    dir = ''
                    pattrn = dir_pattrn[0]
                dir_name = dir
                filter_files = []
                filter_files.append(pattrn.replace(
                    '.', r'\.').replace('*', '.*') + '$')
                pattrn = [re.compile(f) for f in filter_files]
                files_in_dir = [file for file in os.listdir(dir)
                                if any([patt.match(file) for patt in pattrn])]

            if files_in_dir:
                if show:
                    if not hidden:
                        files_in_dir = [file for file in files_in_dir
                                        if not file.startswith('.')]
                    if dir_name != '':
                        if os.stat(dir_name)[0] & 0x4000:
                            print(f'\n{dir_name}/:')
                    self.print_table(files_in_dir, wide=28, format_SH=True, gts=gts)
                if rtn:
                    all_files += [f"{dir_name}/{file}" for file in files_in_dir
                                  if dir_name != '']
        if rtn:
            return all_files

        # from @The Data Scientician : https://stackoverflow.com/questions/9535954/\
        # printing-\lists-as-tabular-data
    def print_table(self, data, cols=4, wide=16, format_SH=False, autocols=True,
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

cd = os.chdir
mkdir = os.mkdir
mv = os.rename
rm = os.remove
rmdir = os.rmdir


def head(f, n=10):
    with open(f) as f:
        for i in range(n):
            l = f.readline()
            if not l:
                break
            sys.stdout.write(l)


def cat(*args):
    files_to_cat = args
    files_in_dir = []
    for file_name in files_to_cat:
        if '*' not in file_name:
            try:
                if os.stat(f"{file_name}")[0] & 0x4000:
                    print(f'cat: {file_name}: Is a directory')
                else:
                    head(file_name, 1 << 30)
            except OSError:
                print(f'cat: {file_name}: No such file in directory')

        else:
            file_pattrn = file_name.rsplit('/', 1)
            if len(file_pattrn) > 1:
                dir, pattrn = file_pattrn
            else:
                dir = ''
                pattrn = file_pattrn[0]
            dir_name = dir
            # list to filter files:
            filter_files = []
            filter_files.append(pattrn.replace(
                '.', r'\.').replace('*', '.*') + '$')
            pattrn = [re.compile(f) for f in filter_files]
            files_in_dir = [file for file in os.listdir(dir)
                            if any([patt.match(file) for patt in pattrn])]

            if files_in_dir:
                for filecat in files_in_dir:
                    if dir_name != '':
                        print(f'\n\u001b[42;1m{dir_name}/\u001b[44;1m{filecat}:'
                              '\u001b[0m')
                        file_str = f"{dir_name}/{filecat}"
                    else:
                        print(f'\n\u001b[44;1m{filecat}:'
                              '\u001b[0m')
                        file_str = f"{filecat}"

                    if os.stat(file_str)[0] & 0x4000:
                        print(f'cat: {file_str}: Is a directory')
                    else:
                        head(file_str, 1 << 30)


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
