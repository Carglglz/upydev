import shlex
import subprocess
import sys
from upydev.keygen import keygen_action
from upydevice import check_device_type, Device
from upydev.shellrepls import ble_repl
import argparse
rawfmt = argparse.RawTextHelpFormatter


repl_options = ['t', 'p', 'wss', 'rkey']

REPLS = dict(help="enter REPL",
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
                                    action='store_true')})

REPL_CMD_DICT_PARSER = {"rpl": REPLS}


usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

ld = """\n\nREPL type will be selected by device (address) class:\n\n\
    SerialDevice -> SerialREPL (needs picocom)\n\n    WebSocketDevice -> WebREPL/\
WebSecREPL\n\n    BleDevice -> BleREPL"""

rplparser = argparse.ArgumentParser(prog="upydev",
                                    description=(f'REPL for MicroPython devices {ld}'
                                                 + '\n\n'
                                                 + _help_subcmds),
                                    formatter_class=rawfmt,
                                    usage=usag, prefix_chars='-')
subrplparser_cmd = rplparser.add_subparsers(title='commands', prog='', dest='m',
                                            )

for command, subcmd in REPL_CMD_DICT_PARSER.items():
    _subparser = subrplparser_cmd.add_parser(command, help=subcmd['help'],
                                             description=subcmd['help'])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)


def parseap(command_args):
    try:
        return rplparser.parse_known_args(command_args)
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


def wrepl(args, device):
    dev_name = device
    web_repl_cmd_str = 'web_repl {} -p {}'.format(args.t, args.p)
    web_repl_cmd = shlex.split(web_repl_cmd_str)
    try:
        subprocess.call(web_repl_cmd)
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
        subprocess.call(web_repl_cmd)
    except KeyboardInterrupt:
        pass
        print('')
    if args.rkey:
        args.m = 'rf_wrkey'
        args.wss = True
        keygen_action(args, device=dev_name)


def srepl(args, device):
    s_port = args.t
    serial_repl_cmd_str = 'picocom -t \x02 {} -b{} -q '.format(s_port, args.p)
    serial_repl_cmd = shlex.split(serial_repl_cmd_str)
    try:
        subprocess.call(serial_repl_cmd)
    except KeyboardInterrupt:
        pass
        print('')


def repl_action(args, unkwargs, **kargs):
    dev_name = kargs.get('device')
    # get top args and make command line filtering
    args_dict = {f"-{k}": v for k, v in vars(args).items() if k in repl_options}
    args_list = [f"{k} {v}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    if args.m == 'repl':
        args.m = 'rpl'
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

    dt = check_device_type(args.t)

    if args.m == 'repl' or args.m == 'rpl':
        if dt == 'WebSocketDevice':
            if not args.wss and ':' not in args.p:
                print('Initiating WebREPL terminal for {} ...'.format(dev_name))
                print('Do CTRL-k so see keybindings')
                wrepl(args, dev_name)
            else:
                print('Initiating WebSecREPL terminal for {} ...'.format(dev_name))
                print('Do CTRL-k so see keybindings')
                wssrepl(args, dev_name)
        elif dt == 'SerialDevice':
            print('Initiating SerialREPL terminal for {} ...'.format(dev_name))
            print('Do C-a, C-x to exit')
            Device(args.t, args.p, init=True)
            srepl(args, dev_name)

        elif dt == 'BleDevice':
            print('Initiating BleREPL terminal for {} ...'.format(dev_name))
            print('Do C-x to exit')
            ble_repl(args, dev_name)
