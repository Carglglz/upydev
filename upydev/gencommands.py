from upydevice import Device, check_device_type
from upydev.commandlib import _CMDDICT_
import time
import sys

fs_commands = ['ls', 'cat', 'head']


def print_sizefile_all(fileslist, tabs=0, frep=None):
    for filedata in fileslist:
        namefile = filedata[0]
        filesize = filedata[1]

        _kB = 1024
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f KB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += namefile
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
        if frep is not None:
            frep.append('{0:<40} Size: {1:>10}'.format(
                prettyprintname, sizestr))


def print_filesys_info(filesize):
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


def gen_command(args, unkwargs, **kargs):

    if '-h' not in unkwargs and args.m != 'gc':
        dev = Device(args.t, args.p, ssl=args.wss, auth=args.wss, init=True)
    else:
        dev = None

    if args.m == 'gc':
        from upydev.shell.commands import ShellCmds
        # TODO: create own dummy args parse help
        sh = ShellCmds(None)
        sh.cmd('-h')
        sys.exit()

    dt = check_device_type(args.t)

    if dt == 'SerialDevice':
        from upydev.shell.shserial import ShellSrCmds
        sh = ShellSrCmds(dev, topargs=args)
    elif dt == 'WebSocketDevice':
        from upydev.shell.shws import ShellWsCmds
        sh = ShellWsCmds(dev, topargs=args)
    elif dt == 'BleDevice':
        from upydev.shell.shble import ShellBleCmds
        sh = ShellBleCmds(dev, topargs=args)

    sh.dev_name = kargs.get('device')
    inp = kargs.get('command_line')
    inp = inp.split('-@')[0]

    if args.m not in ['reset', 'kbi', 'upysh']:
        if args.m in fs_commands:
            dev.wr_cmd(_CMDDICT_['UPYSH'], silent=True)
        if args.m == 'uconfig':
            inp = inp.replace('uconfig', 'config')
        sh.cmd(inp)

    elif args.m == 'reset':
        dev.reset(reconnect=False)
        time.sleep(0.5)
        dev.disconnect()
        return
    elif args.m == 'kbi':
        dev.kbi()
        dev.disconnect()
        return
    elif args.m == 'upysh':
        dev.cmd(_CMDDICT_['UPYSH'], long_string=True)
        dev.disconnect()
        return
