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
_kb_info_cmd = "Do CTRL-k to see keybindings info"
_help_subcmds = "[command] -h to see further help of any command"

shparser = argparse.ArgumentParser(prog="upydev shell",
                                   description=('Shell for MicroPython devices'
                                                '\n\n' + _kb_info_cmd + '\n'
                                                + _help_subcmds),
                                   formatter_class=rawfmt,
                                   usage=usag, prefix_chars='-')
subshparser_cmd = shparser.add_subparsers(title='commands', prog='', dest='m')
shparser.version = f'{uname} shell: {uversion}'
shparser.add_argument('-v', action='version')

for command, subcmd in SHELL_CMD_DICT_PARSER.items():
    _subparser = subshparser_cmd.add_parser(command, help=subcmd['help'])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)
