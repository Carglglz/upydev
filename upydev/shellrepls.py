import shlex
import subprocess
import sys
from upydev.keygen import keygen_action
from upydevice import check_device_type
import signal
from upydevice import Device
import time
import argparse
import json
import os
from upydev.devicemanagement import UPYDEV_PATH
rawfmt = argparse.RawTextHelpFormatter


arg_options = ['t', 'p', 'wss', 'rkey', 'nem']

SHELLREPLS = dict(help="enter shell-repl",
                  subcmd={},
                  options={"-t": dict(help="device target address",
                                      required=True),
                           "-p": dict(help='device password or baudrate',
                                      required=True),
                           "-wss": dict(help='use WebSocket Secure',
                                        required=False,
                                        default=False,
                                        action='store_true'),
                           "-rkey": dict(help='generate new password after exit '
                                         '(WebSocketDevices)',
                                         required=False,
                                         action='store_true'),
                           "-nem": dict(help='force no encryption mode'
                                             ' (WebSocketDevices)',
                                        required=False,
                                        action='store_true')})

SHELL_CONFIG = dict(help="configure shell prompt colors",
                    desc='see\nhttps://python-prompt-toolkit.readthedocs.io/en/master/'
                         'pages/asking_for_input.html#colors\nfor color options',
                    subcmd={},
                    options={"--userpath": dict(help='user path color; default:'
                                                     ' ansimagenta bold',
                                                required=False,
                                                default='ansimagenta bold'),
                             "--username": dict(help='user name color; default:'
                                                     ' ansigreen bold',
                                                required=False,
                                                default='ansigreen bold'),
                             "--at": dict(help='@ color; default: ansigreen bold',
                                          required=False,
                                          default='ansigreen bold'),
                             "--colon": dict(help='colon color; default: white',
                                             required=False,
                                             default='#ffffff'),
                             "--pound": dict(help='pound color; default: ansiblue bold',
                                             required=False,
                                             default='ansiblue bold'),
                             "--host": dict(help='host color; default: ansigreen bold',
                                            required=False,
                                            default='ansigreen bold'),
                             "--path": dict(help='path color; default: ansiblue bold',
                                            required=False,
                                            default='ansiblue bold')})


SET_WSS = dict(help="toggle between WebSecREPL and WebREPL",
               subcmd={},
               options={"-t": dict(help="device target address",
                                   required=True),
                        "-p": dict(help='device password',
                                   required=True),
                        "-wss": dict(help='use WebSocket Secure',
                                     required=False,
                                     default=False,
                                     action='store_true'),
                        })

JUPYTER = dict(help="MicroPython upydevice kernel for jupyter console, CTRL-D to exit",
               subcmd={},
               options={})

SHELLREPL_CMD_DICT_PARSER = {"shl": SHELLREPLS, "shl-config": SHELL_CONFIG,
                             "set_wss": SET_WSS,
                             "jupyterc": JUPYTER}


usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('shell-repl for MicroPython devices'
                                              + '\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-',
                                 allow_abbrev=False)
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in SHELLREPL_CMD_DICT_PARSER.items():
    if 'desc' in subcmd.keys():
        _desc = f"{subcmd['help']}\n\n{subcmd['desc']}"
    else:
        _desc = subcmd['help']
    _subparser = subparser_cmd.add_parser(command, help=subcmd['help'],
                                          description=_desc,
                                          formatter_class=rawfmt)
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)


def parseap(command_args):
    try:
        return parser.parse_known_args(command_args)
    except SystemExit:  # argparse throws these because it assumes you only want
        # to do the command line
        return None  # should be a default one


def sh_cmd(cmd_inp):
    # parse args
    command_line = shlex.split(cmd_inp)

    all_args = parseap(command_line)

    if not all_args:
        return
    else:
        args, unknown_args = all_args

    return args, unknown_args


def filter_bool_opt(k, v):
    if v and isinstance(v, bool):
        return f"{k}"
    else:
        return ""


def ssl_wrepl(args, device):
    if not args.rkey:
        if not args.nem:
            if device is not None:
                if args.wss:
                    sslweb_repl_cmd_str = (f'sslweb_repl -t {args.t} -p {args.p} -r '
                                           f'-dev {device} -wss ')
                else:
                    sslweb_repl_cmd_str = (f'sslweb_repl -t {args.t} -p {args.p} '
                                           f'-r -dev {device} ')
            else:
                if args.wss:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r -wss'.format(
                        args.t, args.p)
                else:
                    sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -r '.format(
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
            sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {} -dev {} '.format(
                args.t, args.p, device)
        else:
            sslweb_repl_cmd_str = 'sslweb_repl -t {} -p {}'.format(
                args.t, args.p)
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
def shell_repl_action(args, unkwargs, **kargs):
    dev_name = kargs.get('device')
    #get top args and make command line filtering
    args_dict = {f"-{k}": v for k, v in vars(args).items() if k in arg_options}
    args_list = [f"{k} {v}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    if args.m == 'shell':
        args.m = 'shl'
    cmd_inp = f"{args.m} {' '.join(unkwargs)} {' '.join(args_list)}"
    # print(cmd_inp)
    # sys.exit()
    # debug command:
    if cmd_inp.startswith('!'):
        args = parseap(shlex.split(cmd_inp[1:]))
        print(args)
        return
    if '-h' in unkwargs:
        sh_cmd(f"{args.m} -h")
        sys.exit()

    args, unknown_args = sh_cmd(cmd_inp)

    if args.m == 'shell' or args.m == 'shl':
        dt = check_device_type(args.t)
        if dt == 'WebSocketDevice':
            print('shell-repl @ {} '.format(dev_name))
            ssl_wrepl(args, dev_name)
        elif dt == 'SerialDevice':
            print('shell-repl @ {} '.format(dev_name))
            sh_srepl(args, dev_name)
        if dt == 'BleDevice':
            print('shell-repl @ {}'.format(dev_name))
            ble_repl(args, dev_name)
        sys.exit()

    elif args.m == 'shl-config':
        config_dict = {}
        for k, v in vars(args).items():
            if k != 'm':
                if k == 'text':
                    k = ''
                config_dict[k] = v
        with open(os.path.join(UPYDEV_PATH, '.upydev_shl_.config'), 'w') as shconf:
            shconf.write(json.dumps(config_dict))

    elif args.m == 'set_wss':
        if not args.wss:
            print('Enabling WebSecureREPL...')
            wss_repl_cmd = ('import wss_repl;wss_repl.stop();wss_repl.start(ssl=True);'
                            'wss_repl.set_ssl(True)\r')
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            bytes_sent = dev.write(wss_repl_cmd)
            time.sleep(2)
            dev.disconnect()
            print('\rWebSecureREPL enabled!')

        else:
            print('Switching to WebREPL...')
            wrepl_cmd = ('import wss_repl;wss_repl.stop();wss_repl.start(ssl=False);'
                         'wss_repl.set_ssl(False)\r')
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            bytes_sent = dev.write(wrepl_cmd)
            time.sleep(2)
            dev.disconnect()
            print('\rWebREPL enabled!, WebSecureREPL disabled!')
        sys.exit()

    elif args.m == 'jupyterc':
        jupyterc()
