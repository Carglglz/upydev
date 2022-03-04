import sys


class QRcode:
    def __init__(self, qr):
        self.qr = qr
        self.size = qr.packed()[0]
        self.width = qr.width()
        self.height = qr.width()

    def pprint(self):

        modcount = self.qr.width()
        sys.stdout.write("\x1b[1;47m" + (" " * (modcount * 2 + 4)) + "\x1b[0m\n")
        for r in range(modcount):
            sys.stdout.write("\x1b[1;47m  \x1b[40m")
            for c in range(modcount):
                if self.qr.get(r, c):
                    sys.stdout.write("  ")
                else:
                    sys.stdout.write("\x1b[1;47m  \x1b[40m")
            sys.stdout.write("\x1b[1;47m  \x1b[0m\n")
        sys.stdout.write("\x1b[1;47m" + (" " * (modcount * 2 + 4)) + "\x1b[0m\n")

    def get(self, x, y):
        return self.qr.get(x, y)

    def packed(self):
        return self.qr.packed()
