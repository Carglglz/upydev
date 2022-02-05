import sys
import os
import gc
import re


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


class DISK_USAGE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", dlev=0, max_dlev=0, hidden=False, pattrn=False):
        if pattrn:
            rpatt = [re.compile(pat.replace('.', r'\.').replace('*', '.*') + '$')
                     for pat in pattrn]
        else:
            rpatt = False
        if path != ".":
            if not os.stat(path)[0] & 0x4000:
                self.pprint(path, path, rpatt)
            else:
                if hidden:
                    resp = {path+'/'+dir: os.stat(path+'/'+dir)
                            [6] for dir in os.listdir(path)}
                else:
                    resp = {path+'/'+dir: os.stat(path+'/'+dir)[6]
                            for dir in os.listdir(path)
                            if not dir.startswith('.')}
                for dir in resp.keys():

                    if not os.stat(dir)[0] & 0x4000:
                        self.pprint(resp[dir], dir, rpatt)

                    else:
                        if dlev < max_dlev:
                            dlev += 1
                            self.__call__(path=dir, dlev=dlev,
                                          max_dlev=max_dlev, hidden=hidden,
                                          pattrn=pattrn)
                            dlev += (-1)
                        else:
                            self.pprint(self.get_dir_sz_recv(dir),
                                        f'\u001b[34;1m{dir}\033[0m', rpatt)

        else:
            if hidden:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)
                        [6] for dir in os.listdir(path)}
            else:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)[6]
                        for dir in os.listdir(path) if not dir.startswith('.')}
            for dir in resp.keys():

                if not os.stat(dir)[0] & 0x4000:
                    self.pprint(resp[dir], dir, rpatt)

                else:
                    if dlev < max_dlev:
                        dlev += 1
                        self.__call__(path=dir, dlev=dlev,
                                      max_dlev=max_dlev, hidden=hidden, pattrn=pattrn)
                        dlev += (-1)
                    else:
                        self.pprint(self.get_dir_sz_recv(dir),
                                    f'\u001b[34;1m{dir}\033[0m', rpatt)

                    gc.collect()

    def print_fs_info(self, filesize):
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

    def pprint(self, sz, path, _patt):
        if sz == path:
            sz = os.stat(path)[6]
        if _patt:
            if any([patt.match(path) for patt in _patt]):
                print(f'{self.print_fs_info(sz):9} {path}')
        else:
            print(f'{self.print_fs_info(sz):9} {path}')

    def get_dir_sz_recv(self, dir):
        return sum([os.stat(dir+'/'+f)[6]
                    if not os.stat(dir+'/'+f)[0] & 0x4000
                    else self.get_dir_sz_recv(dir+'/'+f)
                    for f in os.listdir(dir)])


# from @Roberthh #https://forum.micropython.org/viewtopic.php?f=2&t=7512
def rmrf(*args):  # Remove file or tree
    for d in args:
        try:
            if os.stat(d)[0] & 0x4000:  # Dir
                for f in os.ilistdir(d):
                    if f[0] not in ('.', '..'):
                        rmrf("/".join((d, f[0])))  # File or Dir
                os.rmdir(d)
            else:  # File
                os.remove(d)
        except Exception:
            print(f"rm: {d}: remove failed")


def touch(*args):
    files_to_create = args
    for file in files_to_create:
        nf = open(file, 'w')
        nf.close()


tree = LTREE()
du = DISK_USAGE()
