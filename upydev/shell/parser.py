import argparse
from upydev import name as uname, version as uversion
from upydev.shell.constants import SHELL_CMD_DICT_PARSER
rawfmt = argparse.RawTextHelpFormatter


usag = """command [options]\n
This means that if the first argument [command] is not a registered
command it is redirected to the underlying system shell. To redirect a command
to the system shell use %%command\n
"""
descmds = "upydev shell commands"

shparser = argparse.ArgumentParser(prog="upydev shell",
                                   description='Shell for MicroPython devices',
                                   formatter_class=rawfmt,
                                   usage=usag, prefix_chars='-')
subshparser_cmd = shparser.add_subparsers(title='commands', prog='', dest='m')
shparser.version = f'{uname}: {uversion}'
# shparser.add_argument("m", metavar='CMD', help=shell_commands_info,
#                          nargs='*')
# shparser.add_argument("-d", help='indicate depth level for "du" command',
#                       required=False, default=0, type=int)
# shparser.add_argument("-t", help='table format for "ifconfig" command',
#                       required=False, default=False, action='store_true')
# shparser.add_argument("-wp", help='[ssid] [passwd] for "net conn" '
#                       'command', required=False, nargs=2)
# shparser.add_argument("-ap", help='[ssid] [passwd] for "ap config" '
#                       'command', required=False, nargs=2)
# shparser.add_argument("-i2c", help='[scl] [sda] for "i2c config" '
#                       'command', required=False, nargs=2, default=[22, 23])
# shparser.add_argument("-utc", help='[utc] for "set ntptime" '
#                       'command', required=False, nargs=1, type=int)
# shparser.add_argument("-c", help='to check -c [shafile] for "shasum" '
#                       'command', required=False)
# shparser.add_argument("-a", help='list hidden files for "tree" and "ls" '
#                       'command',
#                       required=False, default=False, action='store_true')
# shparser.add_argument('-r', help='reset for command "exit" or reload after'
#                       ' "run" command',
#                       required=False, default=False, action='store_true')
# shparser.add_argument('-hr', help='machine reset for command "exit"',
#                       required=False, default=False, action='store_true')
# shparser.add_argument('-rf', help='recursively force for command "rm"',
#                       required=False, default=[], nargs='+')
# shparser.add_argument('-n', help='number of lines to print for "head" '
#                       'command',
#                       required=False, default=10, type=int)
# MEM
# shparser_mem = subshparser_cmd.add_parser('mem', help='Show mem info')
# shparser_mem.add_argument('subcmd', default=[], choices=[[], 'dump'],
#                           help='Show mem info or dump memory', nargs='?')
# # dict {cmd:{'help':'command_help', 'subcommand':{'help':'subh', 'choices':[]}}...}
# # add_argument(**dict['cmd']['subcmd'])
# # DU
# shparser_du = subshparser_cmd.add_parser('du', help='Show disk usage statistics')
# shparser_du.add_argument('subcmd', default='',
#                          help='Indicate a dir to show, defaults to "."', nargs='?',
#                          metavar='dir')
# shparser_du.add_argument("-d", help='indicate depth level',
#                          required=False, default=0, type=int)
for command, subcmd in SHELL_CMD_DICT_PARSER.items():
    _subparser = subshparser_cmd.add_parser(command, help=subcmd['help'])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)
