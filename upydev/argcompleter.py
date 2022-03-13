from upydev.shell.constants import SHELL_CMD_DICT_PARSER
from upydev.debugging import DB_CMD_DICT_PARSER
from upydev.devicemanagement import DM_CMD_DICT_PARSER
from upydev.firmwaretools import FW_CMD_DICT_PARSER
from upydev.gencommands import GC_CMD_DICT_PARSER
from upydev.keygen import KG_CMD_DICT_PARSER
from upydev.shellrepls import SHELLREPL_CMD_DICT_PARSER
from upydev.repls import REPL_CMD_DICT_PARSER

ALL_PARSER = {}
ALL_PARSER.update(SHELL_CMD_DICT_PARSER)
ALL_PARSER.update(DB_CMD_DICT_PARSER)
ALL_PARSER.update(DM_CMD_DICT_PARSER)
ALL_PARSER.update(FW_CMD_DICT_PARSER)
ALL_PARSER.update(GC_CMD_DICT_PARSER)
ALL_PARSER.update(KG_CMD_DICT_PARSER)
ALL_PARSER.update(SHELLREPL_CMD_DICT_PARSER)
ALL_PARSER.update(REPL_CMD_DICT_PARSER)

DEVICE_MANAGEMENT_ACTIONS = ['config', 'check', 'register', 'lsdevs',
                             'gg', 'see',
                             'set', 'mkg', 'mgg', 'mksg']

# FIRMWARE ACTIONS

FIRMWARE_ACTIONS = ['mpyx', 'fwr', 'flash', 'ota']


# KEYGEN ACTIONS

KEYGEN_ACTIONS = ['kg', 'rsa']

# REPL ACTIONS

REPL_ACTIONS = ['repl', 'rpl']

# SHELL-REPL ACTIONS

SHELL_REPL_ACTIONS = ['set_wss', 'jupyterc', 'shell', 'shl', 'shl-config']

# DEBUGGING ACTIONS

DEBUGGING_ACTIONS = ['ping', 'probe', 'scan',
                     'stream_test', 'sysctl', 'log', 'pytest', 'run', 'timeit']

# FILEIO ACTIONS

FILEIO_ACTIONS = ['put', 'get', 'install', 'dsync', 'update_upyutils']

# GENERAL COMMANDS
GENERAL_COMMANDS = ['info', 'id', 'upysh', 'reset', 'kbi',
                    'uhelp', 'modules', 'mem', 'du', 'df', 'tree',
                    'net', 'ap', 'i2c', 'set',
                    'datetime', 'gc',
                    'shasum', 'ls', 'cat', 'vim',
                    'enable_sh', 'diff', 'mkdir', 'head', 'rm', 'rmdir',
                    'pwd', 'rssi', 'ifconfig', 'upy-config', 'ctime',
                    'uconfig', 'upip', 'sd', 'reload', 'uping']


def argopts_complete(option):
    if option in ALL_PARSER.keys():
        opt_args = []
        choices = ALL_PARSER[option]['subcmd'].get('choices')
        if choices:
            opt_args += choices
        alt_ops = ALL_PARSER[option].get('alt_ops')
        if alt_ops:
            opt_args += alt_ops
        kw_args = ALL_PARSER[option].get('options')
        if kw_args:
            opt_args += kw_args
        return opt_args
