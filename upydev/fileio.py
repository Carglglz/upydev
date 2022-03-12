from upydevice import check_device_type, Device
from upydev.serialio import SerialFileIO
from upydev.wsio import WebSocketFileIO
from upydev.bleio import BleFileIO
import upydev
import os
import sys
import argparse
import shlex
import time

rawfmt = argparse.RawTextHelpFormatter

UPYDEV_PATH = upydev.__path__[0]

dict_arg_options = {'put': ['dir', 'f', 'fre', 'rst'],
                    'get': ['dir', 'f', 'fre'],
                    'dsync': ['p', 't', 's', 'i', 'f', 'fre'],
                    'update_upyutils': ['f', 'fre'],
                    'install': ['f', 'fre']}

PUT = dict(help="upload files to device",
           subcmd=dict(help='indicate a file/pattern/dir to '
                            'upload',
                       default=[],
                       metavar='file/pattern/dir',
                       nargs='+'),
           options={"-dir": dict(help='path to upload to',
                                 required=False,
                                 default=''),
                    "-rst": dict(help='to soft reset after upload',
                                 required=False,
                                 default=False,
                                 action='store_true')})

GET = dict(help="download files from device",
           subcmd=dict(help='indicate a file/pattern/dir to '
                            'download',
                       default=[],
                       metavar='file/pattern/dir',
                       nargs='+'),
           options={"-dir": dict(help='path to download from',
                                 required=False,
                                 default=''),
                    "-d": dict(help='depth level search for pattrn', required=False,
                               default=0,
                               type=int),
                    "-fg": dict(help='switch off faster get method',
                                required=False,
                                default=True,
                                action='store_false'),
                    "-b": dict(help='read buffer for faster get method', required=False,
                               default=512,
                               type=int)})

DSYNC = dict(help="recursively sync a folder from/to device's filesystem",
             desc="* needs shasum.py in device",
             subcmd=dict(help='indicate a dir/pattern to '
                         'sync',
                         default=['.'],
                         metavar='dir/pattern',
                         nargs='*'),
             options={"-rf": dict(help='remove recursive force a dir or file deleted'
                                       ' in local/device directory',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-d": dict(help='sync from device to host', required=False,
                                 default=False,
                                 action='store_true'),
                      "-fg": dict(help='switch off faster get method',
                                  required=False,
                                  default=True,
                                  action='store_false'),
                      "-b": dict(help='read buffer for faster get method',
                                 required=False,
                                 default=512,
                                 type=int),
                      "-t": dict(help='show tree of directory to sync', required=False,
                                 default=False,
                                 action='store_true'),
                      "-f": dict(help='force sync, no hash check', required=False,
                                 default=False,
                                 action='store_true'),
                      "-p": dict(help='show diff', required=False,
                                 default=False,
                                 action='store_true'),
                      "-n": dict(help='dry-run and save stash', required=False,
                                 default=False,
                                 action='store_true'),
                      "-i": dict(help='ignore file/dir or pattern', required=False,
                                 default=[],
                                 nargs='*')})

UPDATE_UPYUTILS = dict(help="update upyutils scripts",
                       subcmd=dict(help=("filter to match one/multiple "
                                         "upyutils; default: all"),
                                   default=['*'],
                                   nargs='*',
                                   metavar='name/pattern'),
                       options={},
                       alt_ops=os.listdir(os.path.join(UPYDEV_PATH,
                                                       'upyutils_dir')))

INSTALL = dict(help="install libraries or modules with upip to ./lib",
               subcmd=dict(help='indicate a lib/module to install',
                           metavar='module'),
               options={})

FIO_CMD_DICT_PARSER = {"put": PUT, "get": GET, "dsync": DSYNC,
                       "update_upyutils": UPDATE_UPYUTILS, "install": INSTALL}

usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('file io tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in FIO_CMD_DICT_PARSER.items():
    if 'desc' in subcmd.keys():
        _desc = f"{subcmd['help']}\n\n{subcmd['desc']}"
    else:
        _desc = subcmd['help']
    _subparser = subparser_cmd.add_parser(command, help=subcmd['help'],
                                          description=_desc,
                                          formatter_class=rawfmt)
    for pos_arg in subcmd.keys():
        if pos_arg not in ['subcmd', 'help', 'desc', 'options', 'alt_ops']:
            _subparser.add_argument(pos_arg, **subcmd[pos_arg])
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


def expand_margs(v):
    if isinstance(v, list):
        return ' '.join([str(val) for val in v])
    else:
        return v


#############################################
def fileio_action(args, unkwargs, **kargs):
    args_dict = {f"-{k}": v for k, v in vars(args).items()
                 if k in dict_arg_options[args.m]}
    args_list = [f"{k} {expand_margs(v)}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
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

    result = sh_cmd(cmd_inp)
    # print(result)
    if not result:
        sys.exit()

    dev = Device(args.t, args.p, ssl=args.wss, auth=args.wss, init=True)
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
    sh.dsyncio.dev_name = kargs.get('device')
    inp = kargs.get('command_line')
    inp = inp.split('-@')[0]
    if args.m == 'dsync':
        sh_args, unknown_args = result
        if sh_args.d:
            dev.wr_cmd('from upysh import rcat', silent=True)
        sh.cmd(inp)
    else:
        # print(cmd_inp)
        sh_args, unknown_args = result
        if args.m == 'get':
            if sh_args.fg:
                dev.wr_cmd('from upysh import rcat', silent=True)

        sh.cmd(cmd_inp)
        if args.m == 'put':
            if sh_args.rst:
                dev.reset(reconnect=False)
                time.sleep(1)
