import shlex
import subprocess
import sys
from upydev.keygen import keygen_action
from upydevice import check_device_type, Device

REPLS_HELP = """
> REPLS: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - repl/rpl: to enter one of the following depending of upydevice type:
                * WebSocketDevice --> wrepl/wssrepl (with -wss flag)
                * SerialDeivce --> srepl

        - wrepl : to enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
                To see more keybindings info do CTRL-k
                (Added custom keybindings and autocompletion on tab to the previous work
                see: https://github.com/Hermann-SW/webrepl for the original work)

        - wssrepl : to enter the terminal WebSecureREPL; CTRL-x to exit, CTRL-d to do soft reset
                To see more keybindings info do CTRL-k. REPL over WebSecureSockets (This needs use of
                'sslgen_key -tfkey', 'update_upyutils' and enable WebSecureREPL in the device
                "import wss_repl;wss_repl.start(ssl=True)")

        - srepl : to enter the terminal serial repl using picocom, indicate port by -port option
                (to exit do CTRL-a, CTRL-x)
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

    elif args.m == 'wrepl':
        if dt == 'WebSocketDevice':
            print('Initiating WebREPL terminal for {} ...'.format(dev_name))
            print('Do CTRL-k so see keybindings')
            wrepl(args, dev_name)
        else:
            print('{} is NOT a WebSocketDevice'.format(dev_name))
            if dt == 'SerialDevice':
                print('Use srepl instead')
            elif dt == 'BleDevice':
                print('Use brepl instead')
        sys.exit()

    # WEB SECURE REPL :

    elif args.m == 'wssrepl':
        if dt == 'WebSocketDevice':
            print('Initiating WebSecREPL terminal for {} ...'.format(dev_name))
            print('Do CTRL-k so see keybindings')
            wssrepl(args, dev_name)
        else:
            print('{} is NOT a WebSocketDevice'.format(dev_name))
            if dt == 'SerialDevice':
                print('Use srepl instead')
            elif dt == 'BleDevice':
                print('Use brepl instead')
        sys.exit()

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
