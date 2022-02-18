import shlex
import subprocess
import sys
from upydev.keygen import keygen_action
from upydevice import check_device_type, Device
from upydev.shellrepls import ble_repl

REPLS_HELP = """
> REPLS: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - repl/rpl: to enter one of the following depending of upydevice type:
                * WebSocketDevice --> wrepl/wssrepl (with -wss flag)
                * SerialDeivce --> srepl
"""


def wrepl(args, device):
    dev_name = device
    web_repl_cmd_str = 'web_repl {} -p {}'.format(args.t, args.p)
    web_repl_cmd = shlex.split(web_repl_cmd_str)
    try:
        web_repl = subprocess.call(web_repl_cmd)
    except KeyboardInterrupt:
        pass
        print('')
    if args.rkey:
        args.m = 'rf_wrkey'
        keygen_action(args, device=dev_name)


def wssrepl(args, device):
    dev_name = device
    web_repl_cmd_str = 'web_repl {} -p {} -wss'.format(args.t, args.p)
    web_repl_cmd = shlex.split(web_repl_cmd_str)
    try:
        web_repl = subprocess.call(web_repl_cmd)
    except KeyboardInterrupt:
        pass
        print('')
    if args.rkey:
        args.m = 'rf_wrkey'
        args.wss = True
        keygen_action(args, device=dev_name)


def srepl(args, device):
    s_port = args.t
    if args.port is not None:
        s_port = args.port
    serial_repl_cmd_str = 'picocom -t \x02 {} -b{} -q '.format(s_port, args.p)
    serial_repl_cmd = shlex.split(serial_repl_cmd_str)
    try:
        serial_repl = subprocess.call(serial_repl_cmd)
    except KeyboardInterrupt:
        pass
        print('')


def repl_action(args, **kargs):
    dev_name = kargs.get('device')
    dt = check_device_type(args.t)

    if args.m == 'repl' or args.m == 'rpl':
        if dt == 'WebSocketDevice':
            if not args.wss:
                print('Initiating WebREPL terminal for {} ...'.format(dev_name))
                print('Do CTRL-k so see keybindings')
                wrepl(args, dev_name)
            else:
                print('Initiating WebSecREPL terminal for {} ...'.format(dev_name))
                print('Do CTRL-k so see keybindings')
                wssrepl(args, dev_name)
        elif dt == 'SerialDevice':
            print('Initiating Serial REPL terminal for {} ...'.format(dev_name))
            print('Do C-a, C-x to exit')
            dev = Device(args.t, args.p, init=True)
            srepl(args, dev_name)

        elif dt == 'BleDevice':
            print('Initiating BleREPL terminal for {} ...'.format(dev_name))
            print('Do C-x to exit')
            ble_repl(args, dev_name)


    # SERIAL REPL:

    elif args.m == 'srepl':
        if dt == 'SerialDevice' or args.port:

            if args.port:
                print('Initiating Serial REPL terminal for {} ...'.format(args.port))
                if isinstance(args.b, int):
                    args.p = args.b
                else:
                    args.p = 115200

                dev = Device(args.port, args.p, init=True)
            else:
                print('Initiating Serial REPL terminal for {} ...'.format(dev_name))
                dev = Device(args.t, args.p, init=True)
            print('Do C-a, C-x to exit')
            srepl(args, dev_name)
        else:
            print('{} is NOT a SerialDevice'.format(dev_name))
            if dt == 'WebSocketDevice':
                print('Use wrepl or wssrepl instead')
            elif dt == 'BleDevice':
                print('Use brepl instead')
        sys.exit()
