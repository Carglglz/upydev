import io
import re
import uasyncio as asyncio


class AioStream(io.StringIO):
    def __init__(self, alloc_size):
        super().__init__(alloc_size)
        self._max_size = alloc_size
        self._write = super().write

    def write(self, sdata):
        if self.tell() + len(sdata) > self._max_size:
            self.seek(0)
            self._write(" " * self._max_size)
            self.seek(0)
        self._write(sdata)

    def cat(self, grep=""):
        index = self.tell()
        self.seek(0)
        # read and grep for regex
        if grep:
            for line in self.read().strip().splitlines():
                if grep in line:
                    print(line)
        else:
            print(self.read().strip())
        self.seek(index)

    async def follow(self, grep="", wait=0.05):
        init_index = self.tell()
        while True:
            try:
                current_index = self.tell()
                if current_index != init_index:
                    if grep:
                        for line in self.getvalue()[init_index:].strip().splitlines():
                            if line and grep in line:
                                print(line)
                    else:

                        for line in self.getvalue()[init_index:].strip().splitlines():
                            if line:
                                print(line)

                init_index = current_index
                await asyncio.sleep(wait)
            except KeyboardInterrupt:
                break


streamlog = AioStream(2000)
