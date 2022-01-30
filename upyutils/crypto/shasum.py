import hashlib
from binascii import hexlify
import os
import re


def _shasum(file, debug=True, save=False, rtn=False, filetosave=False):
    _hash = hashlib.sha256()
    with open(file, 'rb') as bfile:
        buff = bfile.read(1)
        _hash.update(buff)
        while buff != b'':
            try:
                buff = bfile.read(256)
                if buff != b'':
                    _hash.update(buff)
            except Exception as e:
                print(e)

    _result = _hash.digest()
    result = hexlify(_result).decode()
    if debug:
        print(f"{result}  {file}")
    if save:
        if not filetosave:
            with open(f"{file}.sha256", 'w') as shafile:
                shafile.write(f"{result}  {file}")
        else:
            with open(filetosave, 'a') as shafile:
                shafile.write(f"{result}  {file}")
    if rtn:
        return result


def shasum(*args, **kargs):
    files_to_hash = args
    files_in_dir = []
    for file_name in files_to_hash:
        if '*' not in file_name:
            _shasum(file_name, **kargs)

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
                for filehash in files_in_dir:
                    # print(f'\n\u001b[42;1m{dir_name}/\u001b[44;1m{filehash}:'
                    #       '\u001b[0m')
                    _shasum(f"{dir_name}/{filehash}", *kargs)


def shasum_check(shafile):
    with open(shafile, 'r') as shafile_check:
        shasum_lines = shafile_check.readlines()
        for shaline in shasum_lines:
            _sha256, filename = shaline.split()
            _shacheck = _shasum(filename, debug=False, rtn=True)
            if _sha256 == _shacheck:
                print(f"{filename}: OK")
            else:
                print(f"{filename}: Failed")
