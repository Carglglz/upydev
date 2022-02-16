from upydevice import Device, check_device_type
from upydev.commandlib import _CMDDICT_
import time
import sys


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
    # print(inp)
    if args.m not in ['reset', 'kbi', 'upysh']:
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
