from upydevice import Device, check_device_type
from upydev.commandlib import _CMDDICT_
from upydev.shell.constants import SHELL_CMD_DICT_PARSER
import argparse
import time
import sys
import shlex

rawfmt = argparse.RawTextHelpFormatter

fs_commands = ['ls', 'cat', 'head', 'rm', 'rmdir', 'mkdir', 'cd', 'pwd']

RESET = dict(help="reset device",
             subcmd={},
             options={"-hr": dict(help='to do hard reset',
                                  required=False,
                                  default=False,
                                  action='store_true')})

CONFIG = dict(help="set or check config (from *_config.py files)#",
              desc="to set config --> [config]: [parameter]=[value]",
              subcmd=dict(help='indicate parameter to set or check ',
                          default=[],
                          metavar='parameter',
                          nargs='*'),
              options={"-y": dict(help='print config in YAML format',
                                  required=False,
                                  default=False,
                                  action='store_true')})

KBI = dict(help="to send KeyboardInterrupt to device",
           subcmd={},
           options={})

UPYSH = dict(help="import upysh",
             subcmd={},
             options={})
GC_CMD_DICT = {"reset": RESET, "uconfig": CONFIG, "kbi": KBI, "upysh": UPYSH}

GC_CMD_DICT_PARSER = {}

usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('general comands tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )
GC_CMD_DICT_PARSER.update(SHELL_CMD_DICT_PARSER)
GC_CMD_DICT_PARSER.update(GC_CMD_DICT)
GC_CMD_DICT_PARSER.pop("config")

for command, subcmd in GC_CMD_DICT_PARSER.items():
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


def gen_command(args, unkwargs, **kargs):

    if '-h' not in unkwargs and args.m != 'gc':
        dev = Device(args.t, args.p, ssl=args.wss, auth=args.wss, init=True)
    else:
        dev = None

    if args.m == 'gc':
        from upydev.shell.commands import ShellCmds
        # TODO: create own dummy args parse help
        sh = ShellCmds(None)
        # sh.parser = parser
        sh_cmd('-h')
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
    # sh.parser = parser
    inp = kargs.get('command_line')
    inp = inp.split('-@')[0]

    if args.m not in ['reset', 'kbi', 'upysh']:
        if args.m in fs_commands:
            dev.wr_cmd(_CMDDICT_['UPYSH'], silent=True)
        if args.m == 'uconfig':
            if '-h' in inp:
                sh_cmd(inp)
                sys.exit()
            inp = inp.replace('uconfig', 'config')
        sh.cmd(inp)

    elif args.m == 'reset':
        result = sh_cmd(inp)
        if '-h' in inp:
            sys.exit()
        if not result:
            hr = False
        else:
            args, unknown_args = result
            hr = args.hr
        dev.reset(reconnect=False, hr=hr)
        time.sleep(0.5)
        dev.disconnect()
        return
    elif args.m == 'kbi':
        result = sh_cmd(inp)
        if '-h' in inp:
            sys.exit()
        dev.kbi()
        dev.disconnect()
        return
    elif args.m == 'upysh':
        result = sh_cmd(inp)
        if '-h' in inp:
            sys.exit()
        dev.cmd(_CMDDICT_['UPYSH'], long_string=True)
        dev.disconnect()
        return
