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
    try:
        return [file for file in os.listdir(path) if pattrn.match(file)]
    except Exception:
        return []


def _os_match_dir(patt, path):
    pattrn = re.compile(patt.replace('.', r'\.').replace('*', '.*') + '$')
    if path == '' and os.getcwd() != '/':
        path = os.getcwd()
    try:
        return [f"{path}/{dir}" for dir in os.listdir(path) if pattrn.match(dir)
                and os.stat(f"{path}/{dir}")[0] & 0x4000]
    except Exception:
        return []


class GLOB:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, *args, size=False):
        dir_names_or_pattrn = args
        files_in_dir = []
        for dir_name in dir_names_or_pattrn:
            if '*' not in dir_name and '/' not in dir_name:
                try:
                    st = os.stat(dir_name)
                    if st[0] & 0x4000:  # stat.S_IFDIR
                        files_in_dir += [f"{dir_name}/{file}" for file
                                         in os.listdir(dir_name)]
                    else:
                        if dir_name in os.listdir(os.getcwd()):
                            files_in_dir.append(dir_name)
                except OSError:
                    pass

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
                            files_in_dir += [f"{exp_dir}/{file}" for file
                                             in _files_in_dir]
                        _files_in_dir = []  # reset
                else:

                    files_in_dir += [f"{dir}/{file}" for file
                                     in _os_match(pattrn, dir)]

        if size:
            return [(os.stat(file)[6], file) for file in files_in_dir
                    if not os.stat(file)[0] & 0x4000]
        else:
            return files_in_dir


glob = GLOB()
