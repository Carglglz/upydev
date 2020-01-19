import sys
import os
import gc


class LTREE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", level=0, is_last=False, is_root=True,
                 carrier="    ", hidden=False):
        os.chdir(path)
        r_path = path
        path = "."
        if hidden:
            l = os.listdir(path)
        else:
            l = [f for f in os.listdir(path) if not f.startswith('.')]
        nf = len([file for file in l if not os.stat("%s/%s" % (path, file))[0] & 0x4000])
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
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + "  %s <dir>" % f)
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
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + "  %s" % (f))
        if is_root:
            print('{} directories, {} files'.format(nd, nf))
            if r_path != ".":
                os.chdir('..')
        else:
            return (nf, nd)

    def _treeindent(self, lev, f, lastfile, is_last=False, carrier=None):
        if lev == 0:
            return ""
        else:
            if f != lastfile:
                return carrier + "    ├────"
            else:
                return carrier + "    └────"


class DISK_USAGE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", dlev=0, max_dlev=0, hidden=False):
        if path != ".":
                if not os.stat(path)[0] & 0x4000:
                    print('{:9} {}'.format(self.print_filesys_info(os.stat(path)[6]), path))
                else:
                    if hidden:
                        resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path)}
                    else:
                        resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
                    for dir in resp.keys():

                        if not os.stat(dir)[0] & 0x4000:
                            print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir))

                        else:
                            if dlev < max_dlev:
                                dlev += 1
                                self.__call__(path=dir, dlev=dlev, max_dlev=max_dlev, hidden=hidden)
                                dlev += (-1)
                            else:
                                print('{:9} {} {}'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir, '<dir>'))
                            gc.collect()

        else:
            if hidden:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path)}
            else:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
            for dir in resp.keys():

                if not os.stat(dir)[0] & 0x4000:
                    print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir))

                else:
                    if dlev < max_dlev:
                        dlev += 1
                        self.__call__(path=dir, dlev=dlev, max_dlev=max_dlev, hidden=hidden)
                        dlev += (-1)
                    else:
                        print('{:9} {} {}'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir, '<dir>'))

                    gc.collect()

    def print_filesys_info(self, filesize):
        _kB = 1024
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f KB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)
        return sizestr

    def get_dir_size_recursive(self, dir):
        return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0] & 0x4000 else self.get_dir_size_recursive(dir+'/'+f) for f in os.listdir(dir)])


tree = LTREE()
du = DISK_USAGE()
