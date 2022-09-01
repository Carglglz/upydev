import machine 


def freq():
    fq = machine.freq()
    if isinstance(fq, tuple):
        return int(fq[0]/1e6)
    return int(fq/1e6)
