import hashlib
from binascii import hexlify
import os
import re


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


def _shasum(file, debug=True, save=False, rtn=False, filetosave=False):
    _hash = hashlib.sha256()
    try:
        with open(file, 'rb') as bfile:
            buff = bfile.read(1)
            _hash.update(buff)
            while buff != b'':
                try:
                    buff = bfile.read(256)
                    if buff != b'':
                        _hash.update(buff)
                except OSError:
                    return
    except OSError:
        return
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
    rtn = kargs.get('rtn')
    files_in_dir = []
    hashlist = []
    for file_name in files_to_hash:
        if '*' not in file_name:
            if rtn:
                hashlist.append((file_name, _shasum(file_name, **kargs)))
            else:
                _shasum(file_name, **kargs)
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
                        for filehash in files_in_dir:
                            if exp_dir != '':
                                if rtn:
                                    hashlist.append((f"{exp_dir}/{filehash}",
                                                     _shasum(f"{exp_dir}/{filehash}",
                                                             **kargs)))
                                else:
                                    _shasum(f"{exp_dir}/{filehash}", **kargs)
                            else:
                                if rtn:
                                    hashlist.append((filehash, _shasum(filehash,
                                                                       **kargs)))
                                else:
                                    _shasum(filehash, **kargs)
                files_in_dir = []
            else:
                files_in_dir = _os_match(pattrn, dir)

            if files_in_dir:
                for filehash in files_in_dir:
                    if dir_name != '':
                        if rtn:
                            hashlist.append((f"{dir_name}/{filehash}",
                                             _shasum(f"{dir_name}/{filehash}",
                                                     **kargs)))
                        else:
                            _shasum(f"{dir_name}/{filehash}", **kargs)
                    else:
                        if rtn:
                            hashlist.append((filehash, _shasum(filehash,
                                                               **kargs)))
                        else:
                            _shasum(filehash, **kargs)
    if rtn:
        return hashlist


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
