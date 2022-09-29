import os

_cycles = '.cycles'

def set():
    cycles = 0
    if _cycles in os.listdir():
        cycles = get()
    cycles = cycles + 1
    with open(_cycles, 'wb') as wcycles:
        wcycles.write(cycles.to_bytes(4, 'big'))

def get():
    if _cycles in os.listdir():
        with open(_cycles, 'rb') as rcycles:
            cycles = int.from_bytes(rcycles.read(), 'big')
        return cycles
    else:
        return 0



