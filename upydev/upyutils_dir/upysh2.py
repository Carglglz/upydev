import sys
import os

class LS:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path="."):
        l = os.listdir(path)
        l.sort()
        for f in l:
            st = os.stat("%s/%s" % (path, f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print("   <dir> %s" % f)
            else:
                print("% 8d %s" % (st[6], f))

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


class LTREE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", level=0, is_last=False):
        l = os.listdir(path)
        l.sort()
        if len(l) > 0:
            last_file = l[-1]
        else:
            last_file = ''
        for f in l:
            st = os.stat("%s/%s" % (path, f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print(self._treeindet(level, f, last_file, is_last=is_last) + "  %s <dir>" % f)
                os.chdir(f)
                level +=1
                lf = last_file == f
                self.__call__(level=level, is_last=lf)
                os.chdir('..')
                level += (-1)
            else:
                print(self._treeindet(level, f, last_file, is_last=is_last) + "  %s" % (f))

    def _treeindet(self, lev, f, lastfile, is_last=False):
        if lev == 0:
            return ""
        elif lev >= 2:
            if f != lastfile:
                if is_last:
                    return lev*"    " + "    ├────"
                else:
                    return lev*"    " + "│   ├────"
            else:
                if is_last:
                    return lev*"    " + "    └────"
                else:
                    return lev*"    " + "│   └────"

        else:
            if f != lastfile:
                return lev*"    " + "    ├────"
            else:
                return lev*"    " + "    └────"

tree = LTREE()
