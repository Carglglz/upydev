import shlex
import subprocess
import sys
from upydev.keygen import keygen_action
from upydevice import check_device_type
import signal
from upydevice import Device
import time

SHELL_REPLS_HELP = """
> SHELL-REPLS: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - shell/shl: To enter one of the following SHELL-REPLS depending of upydevice type:
                    * WebSocketDevice --> ssl_wrepl/wssl (with -wss flag)
                    * SerialDeivce --> sh_repl/shr
                    * BleDevice --> ble

        - set_wss: To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do 'set_wss', to disable 'set_wss -wss'


        - jupyterc: to run MicroPython upydevice kernel for jupyter console, CTRL-D to exit,
                    %%lsmagic to see magic commands and how to connect to a
                    device either WebREPL (%%websocketconnect) or Serial connection (%%serialconnect).
                    Hit tab to autcomplete magic commands, and MicroPython/Python code.
                    (This needs jupyter and MicroPython upydevice kernel to be installed)"""


def ssl_wrepl(args, device):
    if not args.rkey:
        if not args.nem:
            if device is not None:
                if args.wss:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r -dev {} -wss -zt {}'.format(
                        args.t, args.p, device, args.zt)
                else:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r -dev {} -zt {}'.format(
                        args.t, args.p, device, args.zt)
            else:
                if args.wss:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r -wss -zt {}'.format(
                        args.t, args.p, args.zt)
                else:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r -zt {}'.format(
                        args.t, args.p, args.zt)
            sslweb_repl_cmd = shlex.split(sslweb_repl_cmd_str)

            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)

            try:
                sslweb_repl = subprocess.call(
                    sslweb_repl_cmd, preexec_fn=preexec_function)
            except KeyboardInterrupt:
                pass

        else:
            if device is not None:

                sslweb_repl_cmd_str = (f'sslweb_repl -t {args.t} -p {args.p} -dev '
                                       f'{device} -nem')
            else:
                sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -nem'.format(
                    args.t, args.p)
            if args.wss:
                sslweb_repl_cmd_str += ' -wss'
            sslweb_repl_cmd = shlex.split(sslweb_repl_cmd_str)

            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)

            try:
                sslweb_repl = subprocess.call(
                    sslweb_repl_cmd, preexec_fn=preexec_function)
            except KeyboardInterrupt:
                pass

    if args.rkey:
        if device is not None:
            sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -dev {} -zt {}'.format(
                args.t, args.p, device, args.zt)
        else:
            sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -zt {}'.format(
                args.t, args.p, args.zt)
        sslweb_repl_cmd = shlex.split(sslweb_repl_cmd_str)
        try:
            sslweb_repl = subprocess.call(sslweb_repl_cmd)
        except KeyboardInterrupt:
            pass
            print('')

        args.m = 'rf_wrkey'
        keygen_action(args, device=device)

#############################################


def sh_srepl(args, device):
    if args.port:
        args.t = args.port
    if args.b:
        args.p = args.b
    if device is not None:
        sh_srepl_cmd_str = 'sh_srepl -t {} -p {} -r -dev {}'.format(
            args.p, args.t, device)
    else:
        sh_srepl_cmd_str = 'sh_srepl -t {} -p {} -r'.format(args.p, args.t)
    sh_srepl_cmd = shlex.split(sh_srepl_cmd_str)

    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

    def preexec_function(action=old_action):
        signal.signal(signal.SIGINT, action)

    try:
        sh_srepl = subprocess.call(sh_srepl_cmd, preexec_fn=preexec_function)
    except KeyboardInterrupt:
        pass


#############################################

def ble_repl(args, device):

    if device is not None:

        blerepl_cmd_str = 'blerepl -t {} -dev {} -r'.format(args.t, device)
    else:

        blerepl_cmd_str = 'blerepl -t {} -r'.format(args.t)
    blerepl_cmd = shlex.split(blerepl_cmd_str)

    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

    def preexec_function(action=old_action):
        signal.signal(signal.SIGINT, action)

    try:
        blerepl = subprocess.call(blerepl_cmd, preexec_fn=preexec_function)
    except KeyboardInterrupt:
        pass

    sys.exit()

#############################################


def jupyterc():
    jupyter_cmd_str = 'jupyter console --kernel=micropython-upydevice'
    jupyter_cmd = shlex.split(jupyter_cmd_str)
    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

    def preexec_function(action=old_action):
        signal.signal(signal.SIGINT, action)
    try:
        jupyter_console = subprocess.call(jupyter_cmd, preexec_fn=preexec_function)
        signal.signal(signal.SIGINT, old_action)
    except KeyboardInterrupt:
        pass
        print('')
    sys.exit()


#############################################
def shell_repl_action(args, **kargs):
    dev_name = kargs.get('device')
    dt = check_device_type(args.t)

    if args.m == 'shell' or args.m == 'shl':
        if dt == 'WebSocketDevice':
            print('shell-repl @ {} '.format(dev_name))
            ssl_wrepl(args, dev_name)
        elif dt == 'SerialDevice' or args.port:
            if args.port:
                dev_name = args.port
            print('shell-repl @ {} '.format(dev_name))
            sh_srepl(args, dev_name)
        if dt == 'BleDevice':
            print('shell-repl @ {}'.format(dev_name))
            ble_repl(args, dev_name)
        sys.exit()


    elif args.m == 'set_wss':
        if not args.wss:
            print('Enabling WebSecureREPL...')
            wss_repl_cmd = 'import wss_repl;wss_repl.stop();wss_repl.start(ssl=True);wss_repl.set_ssl(True)\r'
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            bytes_sent = dev.write(wss_repl_cmd)
            time.sleep(2)
            dev.disconnect()
            print('\rWebSecureREPL enabled!')

        else:
            print('Switching to WebREPL...')
            wrepl_cmd = 'import wss_repl;wss_repl.stop();wss_repl.start(ssl=False);wss_repl.set_ssl(False)\r'
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            bytes_sent = dev.write(wrepl_cmd)
            time.sleep(2)
            dev.disconnect()
            print('\rWebREPL enabled!, WebSecureREPL disabled!')
        sys.exit()

    elif args.m == 'jupyterc':
        jupyterc()
