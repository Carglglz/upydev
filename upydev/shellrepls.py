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

        - ssl_wrepl: To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal over SSL sockets;
                     CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default)
                     To see more keybindings info do CTRL-k. By default resets after exit,
                     use -rkey option to refresh the WebREPL password with a new random password,
                     after exit.This passowrd will be stored in the working directory or in global directory with
                     -g option. (This mode needs ssl_repl.py, upysecrets.py for -rfkey)
                     *(Use -nem option to use without encryption (for esp8266))
                     * Use -zt [HOST ZEROTIER IP/BRIDGE IP] option to for devices connected through zerotier network.
                      (this can be avoided adding the -zt [HOST ZEROTIER IP/BRIDGE IP] option when configuring a device)

        - ssl: to access ssl_wrepl in a 'ssh' style command to be used like e.g.:
              "upydev ssl@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
               The device can be accessed as "upydev ssl@foo_device" or redirect any command as e.g.
               "upydev ping -@foo_device". *(For esp8266 use the option -nem (no encryption mode))

        - sh_srepl: To enter the serial terminal SHELL-REPL; CTRL-x to exit,
                    To see more keybindings info do CTRL-k. By default resets after exit.
                    To configure a serial device use -t for baudrate and -p for serial port
                    To access without previous configuration: "sh_srepl -port [serial port] -b [baudrate]"
                    (default baudrate is 115200)
                    To access with previous configuration:
                        - "sh_srepl" (if device configured in current working directory)
                        - "sh_srepl -@ foo_device" (if foo_device is configured in global group 'UPY_G')

        - shr: to access the serial terminal SHELL-REPL in a 'ssh' style command to be used like e.g.:
              "upydev shr@/dev/tty.usbmodem3370377430372" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g.
               "upydev make_group -g -f UPY_G -devs foo_device 115200 /dev/tty.usbmodem3370377430372")
               The device can be accessed as "upydev shr@foo_device"

        - wssl: to access ssl_wrepl if WebSecureREPL is enabled in a 'ssh' style command to be used like e.g.:
              "upydev wssl@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
               then the device can be accessed as "upydev wssl@foo_device"

        - set_wss: To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do 'set_wss', to disable 'set_wss -wss'

        - ble: to access the terminal BleSHELL-REPL (if BleREPL enabled) in a 'ssh' style command to be used like e.g.:
              "upydev ble@[UUID]" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g.
               "upydev make_group -g -f UPY_G -devs foo_device UUID PASS")
               The device can be accessed as "upydev ble@foo_device"

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
                sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -dev {} -nem'.format(
                    args.t, args.p, device)
            else:
                sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -nem'.format(
                    args.t, args.p)
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
            print('SSL SHELL-REPL @ {} '.format(dev_name))
            ssl_wrepl(args, dev_name)
        elif dt == 'SerialDevice' or args.port:
            if args.port:
                dev_name = args.port
            print('SERIAL SHELL-REPL @ {} '.format(dev_name))
            sh_srepl(args, dev_name)

        if dt == 'BleDevice':
            print('BLE SHELL-REPL @ {}'.format(dev_name))
            ble_repl(args, dev_name)
        sys.exit()

    elif args.m == 'ssl_wrepl' or args.m == 'ssl':
        if dt == 'WebSocketDevice':
            print('SSL SHELL-REPL @ {} '.format(dev_name))
            ssl_wrepl(args, dev_name)
        else:
            print('{} is NOT a WebSocketDevice'.format(dev_name))
            if dt == 'SerialDevice':
                print('Use sh_srepl/shr instead')
            elif dt == 'BleDevice':
                print('Use ble instead')
        sys.exit()

    elif args.m == 'wssl':
        args.wss = True
        if dt == 'WebSocketDevice':
            print('WSSL SHELL-REPL @ {} '.format(dev_name))
            ssl_wrepl(args, dev_name)
        else:
            print('{} is NOT a WebSocketDevice'.format(dev_name))
            if dt == 'SerialDevice':
                print('Use sh_srepl/shr instead')
            elif dt == 'BleDevice':
                print('Use ble instead')
        sys.exit()

    elif args.m == 'sh_srepl' or args.m == 'shr':
        if dt == 'SerialDevice' or args.port:
            if args.port:
                dev_name = args.port
            print('SERIAL SHELL-REPL @ {} '.format(dev_name))
            sh_srepl(args, dev_name)
        else:
            print('{} is NOT a SerialDevice'.format(dev_name))
            if dt == 'WebSocketDevice':
                print('Use ssl_wrepl or ssl instead')
            elif dt == 'BleDevice':
                print('Use ble instead')
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

    elif args.m == 'brepl' or args.m == 'ble':
        if dt == 'BleDevice':
            print('BLE SHELL-REPL @ {}'.format(dev_name))
            ble_repl(args, dev_name)
        else:
            print('{} is NOT a BleDevice'.format(dev_name))
            if dt == 'WebSocketDevice':
                print('Use ssl_wrepl or ssl instead')
            elif dt == 'SerialDevice':
                print('Use sh_srepl or shr instead')
        sys.exit()

    elif args.m == 'jupyterc':
        jupyterc()
