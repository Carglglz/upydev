from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from pygments.styles import get_all_styles
from upydev import __path__ as _UPYDEVPATH
import os
import json

SHELL_CONFIG = '.upydev_shl_.config'

# Prompt Style
style_p = Style.from_dict({
    # User input (default text).

    # Prompt.
    'userpath': 'ansimagenta bold',
    'username': 'ansigreen bold',
    'at':       'ansigreen bold',
    'colon':    '#ffffff',
    'pound':    'ansiblue bold',
    'host':     'ansigreen bold',
    'path':     'ansiblue bold',
})

# apply shell config if exists:
if SHELL_CONFIG in os.listdir(_UPYDEVPATH[0]):
    with open(os.path.join(_UPYDEVPATH[0], SHELL_CONFIG), 'r') as shconf:
        config_dict = json.loads(shconf.read())
    style_p = Style.from_dict(config_dict)

# Prompt format
shell_message = [
    ('class:userpath',    ''),
    ('class:username', ''),  # 1
    ('class:at',       '@'),
    ('class:host',     ''),  # 3
    ('class:colon',    ':'),
    ('class:path',     '~ '),
    ('class:pound',    '$ '),
]

d_prompt = '>>> '

# KEYBINDINGS
kb = KeyBindings()
SHELL_ALIASES = []
mem_show_rp = {'show': False, 'call': False, 'used': '?',
               'free': '?', 'percent': 0}
dev_path = {'p': ' '}
local_path = {'p': ''}
show_local_path = {'s': False}
status_encryp_msg = {'S': False, 'Toggle': True}
exit_flag = {'exit': False}
encrypted_flag = {'sec': True}
prompt = {'p': '>>> '}
paste_flag = {'p': False}
paste_buffer = {'B': []}
reset_flag = {'R': False}
autosuggest = {'A': False}
shell_mode = {'S': False}
frozen_modules = {'FM': [], 'SUB': []}
edit_mode = {'E': False, 'File': ''}
shell_mode_run = {'R': False}
script_is_running = {'R': False, 'script': 'test_code'}
shell_prompt = {'s': shell_message}
shell_commands = ['cd', 'mkdir', 'cat', 'head', 'rm', 'rmdir', 'pwd',
                  'run']
custom_sh_cmd_kw = ['df', 'datetime', 'ifconfig', 'net',
                    'ap', 'mem', 'install', 'touch',
                    'exit', 'lpwd', 'lsl', 'lcd', 'put', 'get', 'ls',
                    'set', 'tree', 'dsync', 'reload', 'docs',
                    'du', 'ldu', 'upip', 'uping',
                    'timeit', 'i2c',
                    'upy-config', 'jupyterc', 'pytest', 'rssi',
                    'info', 'id', 'uhelp', 'modules', 'shasum', 'vim',
                    'update_upyutils', 'mdocs', 'ctime', 'enable_sh',
                    'diff', 'config', 'fw', 'mpyx', 'sd']

CRED = '\033[91;1m'
CGREEN = '\33[32;1m'
CEND = '\033[0m'
YELLOW = '\u001b[33m'
BCYAN = '\u001b[36;1m'
ABLUE_bold = '\u001b[34;1m'
MAGENTA_bold = '\u001b[35;1m'
WHITE_ = '\u001b[37m'
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'
PYGM_SYNTAX = list(get_all_styles()) + ['one_dark']
batstyle = {'style': 'monokai'}
AUTHMODE_DICT = {0: 'NONE', 1: 'WEP', 2: 'WPA PSK', 3: 'WPA2 PSK',
                    4: 'WPA/WAP2 PSK'}

git_diff_files = {'diff': [], 'commit': '', 'n_commits': 0}


# KEYBINDINGS INFO
kb_info = """
* Autocompletion keybindings:
     - tab to autocomplete device file / dirs names / raw micropython (repl commands)
     - shift-tab to autocomplete shell commands
     - shift-right to autocomplete local file / dirs names
     - shift-left to toggle local path in prompt
* CTRL - keybindings:
    - CTRL-x : to exit shell/repl
    - CTRL-p : toggle RAM STATUS right aligned message (USED/FREE)
    - CTRL-e : paste vim mode in repl
    - CTRL-d : ends vim paste mode in repl and execute buffer
    - CTRL-c : KeyboardInterrupt, in normal mode, cancel in paste mode
    - CTRL-b : prints MicroPython version and sys platform
    - CTRL-r : to flush line buffer
    - CTRL-n : shows mem_info()
    - CTRL-y : gc.collect() shortcut command
    - CTRL-space : repeats last command
    - CTRL-o, Enter : to enter upy-config dialog
    - CTRL-t : runs temp buffer ('_tmp_script.py' in cwd)
    - CTRL-w : prints device info
    - CTRL-a : set cursor position at the beggining
    - CTRL-j : set cursor position at the end of line
    - CTRL-f : toggle autosuggest mode (Fish shell like)(use right arrow to complete)
    - CRTL-s : toggle shell mode to navigate filesystem (see shell commands)
    - CTRL-k : prints the custom keybindings (this list)
"""


shell_commands_info = """
* Autocompletion commands:
     - tab to autocomplete device file / dirs names / raw micropython (repl commands)
     - shift-tab to autocomplete shell commands
     - shift-right to autocomplete local file / dirs names
     - shift-left to toggle local path in prompt

* Device shell commands:
    * upysh commands:
        - sz   : list files and size in bytes
        - head : print the head of a file
        - cat  : prints the content of a file
        - mkdir: make directory
        - cd   : change directory (cd .. to go back one level)
        - pwd  : print working directory
        - rm   : to remove a file
        - rmdir: to remove a directory

    * custom shell commands:
        - ls  : list device files in colored format (same as pressing tab on empty line) (allows "*" wildcard or directories)
        - tree : to print a tree version of filesystem (to see also hidden files/dirs use 'tree -a')
        - run  : to run a 'script.py'
        - df   : to see filesystem flash usage (and SD if already mounted)
        - du   : display disk usage statistics (usage: "du", "du [dir or file]" + '-d' deep level option)
        - meminfo: to see RAM info
        - dump_mem: to do a memory dump
        - whoami : to see user, system and machine info
        - datetime: to see device datetime (if not set, will display uptime)
        - set_localtime : to set the device datetime from the local machine time
        - ifconfig: to see STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
        - ifconfig_t: to see STATION interface configuration in table format
                      (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
        - netscan: to scan WLANs available, (ESSID, MAC ADDRESS, CHANNEL, RSSI, AUTH MODE, HIDDEN)
        - uping : to make the device send ICMP ECHO_REQUEST packets to network hosts (do 'uping host' to ping local machine)
        - apconfig: to see access POINT (AP) interface configuration (IP, SUBNET, GATEAWAY, DNS)
        - apconfig_t: to see access POINT (AP) interface configuration in table format
                     (SSID, BSSID, CHANNEL, AUTH, IP, SUBNET, GATEAWAY, DNS)
        - install: to install a library into the device with upip.
        - touch  : to create a new file (e.g. touch test.txt)
        - edit   : to edit a file (e.g. edit my_script.py)
        - get    : to get a file from the device (also allows "*" wildcard, 'cwd' or multiple files)
        - put    : to upload a file to the device (also allows "*" wildcard, 'cwd' or multiple files)
        - sync   : to get file (faster) from the device (use with > 10 KB files) (no encrypted mode only)
        - d_sync : to recursively sync a local directory with the device filesystem,
                   use 'd_sync .' to sync local cwd into device cwd
        - wrepl  : to enter the original WebREPL terminal (no encryption mode)
        - reload : to delete a module from sys.path so it can be imported again.
        - flush_soc: to flush socket in case of wrong output
        - view   : to preview '.pbm' binary image files (image need to be centered and rows = columns) (encryption mode only)
        - bat    : prints the content of a '.py' file with Python syntax hightlighting
        - batstyle: 'bat' output style; to set: 'batstyle [style]', to see: 'batstyle': current style / 'batstyle -a': all styles
        - rcat   : prints the raw content of a file (encryption mode only)
        - timeit : to measure execution time of a script/command
        - i2c    : config/scan (config must be used first, i2c config -scl [SCL] -sda [SDA])
        - upy-config: interactive dialog to configure Network (connect to a WLAN or set an AP) or Interafaces (I2C)
        - wss: on/off; to enable WebSecureREPL for initial handshake (this sets ssl_flag.SSL to True or False)
        - jupyterc: to run MicroPython upydevice kernel for jupyter console
        - exit   : to exit SSLWebREPL Terminal (in encrypted mode soft-reset by default)
                    to exit without reset do 'exit -nr'
                    to exit and do hard reset 'exit -hr'

* Local shell commands:
    - pwdl   : to see local path
    - cdl    : to change local directory
    - lsl    : to list local directory
    - catl   : to print the contents of a local file
    - batl   : prints the content of a local '.py' file with Python syntax hightlighting
    - l_micropython: if "micropython" local machine version available in $PATH, runs it.
    - python : switch to local python3 repl
    - vim    : to edit a local file with vim  (e.g. vim script.py)
    - emacs  : to edit a local file with emacs (e.g. emacs script.py)
    - l_ifconfig: to see local machine STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
    - l_ifconfig_t: to see local machine STATION interface configuration in table format
                  (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
    - lsof : to scan TCP ports of the device (TCP ports 1-10000)
    - docs : to open MicroPython docs site in the default web browser, if a second term
            is passed e.g. 'docs machine' it will open the docs site and search for 'machine'
    - getcert: to print the client SSL Certificate
    - get_rawbuff: to get the raw output of a command (for debugging purpose)
    - ldu  : display local path disk usage statistics (usage: "ldu", "ldu [dir or file]" + '-d' deep level option)
    - upipl : (usage 'upipl' or 'upipl [module]' display available micropython packages that can be installed with install command
    - pkg_info: to see the PGK-INFO file of a module if available at pypi.org or micropython.org/pi
    - lping : to make local machine send ICMP ECHO_REQUEST packets to network hosts (do 'lping dev' to ping the device)
    - git : to call git commands and integrate the git workflow into a project (needs 'git' available in $PATH)
            Use 'git init dev' to initiate device repo
            Use 'git push dev' after a 'git commit ..' or 'git pull' to push the changes to the device.
            Use 'git log dev' to see the latest commit pushed to the device ('git log dev -a' to see all commits)
            Use 'git log host' to see the latest commit in the local repo
            Use 'git status dev' to see if the local repo is ahead of the device repo and track these changes
            Use 'git clone_dev' to clone the local repo into the device
            Use 'git repo' to open the remote repo in the web browser if remote repo exists
            Any other git command will be echoed directly to git
    - tig: to use the 'Text mode interface for git' tool. Must be available in $PATH

* Local shell special commands:
    Commands that start with %% or not registered will be forwarded to local shell.
"""
# dict {cmd:{'help':'command_help', 'subcommand':{'help':'subh', 'choices':[]}}...}
LS = dict(help="list files or directories",
          subcmd=dict(help='indicate a file/dir or pattern to see', default=[],
                      metavar='file/dir/pattern', nargs='*'),
          options={"-a": dict(help='list hidden files', required=False,
                              default=False,
                              action='store_true'),
                   "-d": dict(help='depth level', required=False,
                              default=0,
                              type=int)})
HEAD = dict(help="display first lines of a file",
            subcmd=dict(help='indicate a file or pattern to see', default=[],
                        metavar='file/pattern', nargs='*'),
            options={"-n": dict(help='number of lines to print', required=False,
                                default=10,
                                type=int)})
CAT = dict(help="concatenate and print files",
           subcmd=dict(help='indicate a file or pattern to see', default=[],
                       metavar='file/pattern', nargs='*'),
           options={"-d": dict(help='depth level', required=False,
                               default=0,
                               type=int)})

MKDIR = dict(help="make directories",
             subcmd=dict(help='indicate a dir/pattern to create', default=[],
                         metavar='dir', nargs='*'),
             options={})

CD = dict(help="change current working directory",
          subcmd=dict(help='indicate a dir to change to', default='/',
                      metavar='dir', nargs='?'),
          options={})
PWD = dict(help="print current working directory",
           subcmd={},
           options={})
RM = dict(help="remove file or pattern of files",
          subcmd=dict(help='indicate a file/pattern to remove', default=[],
                      metavar='file/dir/pattern', nargs='+'),
          options={"-rf": dict(help='remove recursive force a dir or file',
                               required=False,
                               default=False,
                               action='store_true'),
                   "-d": dict(help='depth level search', required=False,
                              default=0,
                              type=int),
                   "-dd": dict(help='filter for directories only', required=False,
                               default=False,
                               action='store_true')})
RMDIR = dict(help="remove directories or pattern of directories",
             subcmd=dict(help='indicate a dir/pattern to remove', default=[],
                         metavar='dir', nargs='+'),
             options={"-d": dict(help='depth level search', required=False,
                                 default=0,
                                 type=int)})

DU = dict(help="display disk usage statistics",
          subcmd=dict(help='indicate a dir to see usage', default='',
                      metavar='dir', nargs='?'),
          options={"-d": dict(help='depth level', required=False,
                              default=0,
                              type=int),
                   "-p": dict(help='pattern to match', required=False,
                              default=[],
                              nargs='*')})
TREE = dict(help="list contents of directories in a tree-like format",
            subcmd=dict(help='indicate a dir to see', default='',
                        metavar='dir', nargs='?'),
            options={"-a": dict(help='list hidden files', required=False,
                                default=False,
                                action='store_true')})
DF = dict(help="display free disk space",
          subcmd={},
          options={})

MEM = dict(help="show ram usage info",
           subcmd=dict(help='{info , dump}; default: info',
                       default='info',
                       metavar='action', choices=['info', 'dump'], nargs='?'),
           options={})

EXIT = dict(help="exit upydev shell",
            subcmd={},
            options={"-r": dict(help='soft-reset after exit', required=False,
                                default=False,
                                action='store_true'),
                     "-hr": dict(help='hard-reset after exit', required=False,
                                 default=False,
                                 action='store_true')})
VIM = dict(help="use vim to edit files",
           subcmd=dict(help='indicate a file to edit', default='',
                       metavar='file', nargs='?'),
           options={"-rm": dict(help='remove local copy after upload', required=False,
                                default=False,
                                action='store_true'),
                    "-e": dict(help='execute script after upload', required=False,
                               default=False,
                               action='store_true'),
                    "-r": dict(help='reload script so it can run again',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-o": dict(help='override local copy if present',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-d": dict(help=('use vim diff between device and local files'
                                     ', if same file name device file is ~file'),
                               required=False,
                               default=[],
                               nargs='+')})

DIFF = dict(help=("use git diff between device's [~file/s] and local file/s"),
            subcmd=dict(help='indicate files to compare or pattern', default=['*', '*'],
                        metavar='fileA fileB', nargs='+'),
            options={"-s": dict(help='switch file comparison',
                                required=False,
                                default=False,
                                action='store_true')})

RUN = dict(help="run device's scripts",
           subcmd=dict(help='indicate a file/script to run', default='',
                       metavar='file'),
           options={"-r": dict(help='reload script so it can run again',
                               required=False,
                               default=False,
                               action='store_true'),
                    })

RELOAD = dict(help="reload device's scripts",
              subcmd=dict(help='indicate a file/script to reload', default='',
                          metavar='file', nargs=1),
              options={})

LCD = dict(help="change local current working directory",
           subcmd=dict(help='indicate a dir to change to', default='',
                       metavar='dir', nargs='?'),
           options={})

LSL = dict(help="list local files or directories",
           subcmd=dict(help='indicate a file/dir or pattern to see', default=[],
                       metavar='file/dir/pattern', nargs='*'),
           options={"-a": dict(help='list hidden files', required=False,
                               default=False,
                               action='store_true')})
LPWD = dict(help="print local current working directory",
            subcmd={},
            options={})

LDU = dict(help="display local disk usage statistics",
           subcmd=dict(help='indicate a dir to see usage', default='',
                       metavar='dir', nargs='?'),
           options={"-d": dict(help='depth level', required=False,
                               default=0,
                               type=int)})
INFO = dict(help="prints device's info",
            subcmd={},
            options={})

ID = dict(help="prints device's unique id",
          subcmd={},
          options={})

UHELP = dict(help="prints device's help info",
             subcmd={},
             options={})

MODULES = dict(help="prints device's frozen modules",
               subcmd={},
               options={})

UPING = dict(help="device send ICMP ECHO_REQUEST packets to network hosts",
             subcmd=dict(help='indicate an IP address to ping; default: host IP',
                         default='host',
                         metavar='IP', nargs='?'),
             options={})

RSSI = dict(help="prints device's RSSI (WiFi or BLE)",
            subcmd={},
            options={})

NET = dict(help="manage network station interface (STA._IF)",
           desc="enable/disable station inteface, config and connect to or scan APs",
           subcmd=dict(help='{status, on, off, config, scan}; default: status',
                       default='status',
                       metavar='command',
                       choices=['status', 'on', 'off', 'config', 'scan'],
                       nargs='?'),
           options={"-wp": dict(help='ssid, password for config command',
                                required=False,
                                nargs=2)})
IFCONFIG = dict(help="prints network interface configuration (STA._IF)",
                subcmd={},
                options={"-t": dict(help='print info in table format',
                                    required=False,
                                    default=False,
                                    action='store_true')})

AP = dict(help="manage network acces point interface (AP._IF)",
          desc="enable/disable ap inteface, config an AP or scan connected clients",
          subcmd=dict(help='{status, on, off, scan, config}; default: status',
                      default='status',
                      metavar='command',
                      choices=['status', 'on', 'off', 'config', 'scan'],
                      nargs='?'),
          options={"-ap": dict(help='ssid, password for config command',
                               required=False,
                               nargs=2),
                   "-t": dict(help='print info in table format',
                              required=False,
                              default=False,
                              action='store_true')})

I2C = dict(help="manage I2C interface",
           subcmd=dict(help='{config, scan}; default: config',
                       default='config',
                       metavar='action',
                       choices=['config', 'scan'],
                       nargs='?'),
           options={"-i2c": dict(help='[scl] [sda] for config command',
                                 required=False,
                                 default=[22, 23],
                                 nargs=2)})

SET = dict(help="set device's configuration {rtc, hostname, localname}",
           subcmd=dict(help=('set parameter configuration {rtc localtime, rtc ntptime,'
                             ' hostname, localname}; default: rtc localtime'),
                       default=['rtc'],
                       metavar='parameter', nargs='+'),
           options={"-utc": dict(help='[utc] for "set ntptime" '
                                 'command', required=False, nargs=1, type=int)},
           alt_ops=['rtc', 'localtime', 'ntptime', 'hostname', 'localname'])

DATETIME = dict(help="prints device's RTC time",
                subcmd={},
                options={})

SHASUM = dict(help="shasum SHA-256 tool",
              subcmd=dict(help='Get the hash of a file or check a shasum file',
                          default=[],
                          metavar='file/pattern',
                          nargs='*'),
              options={"-c": dict(help='check a shasum file',
                                  required=False,
                                  default='')})
TOUCH = dict(help="create a new file",
             subcmd=dict(help='indicate a new file/pattern to create',
                         default=[],
                         metavar='file/pattern',
                         nargs='*'),
             options={})

UPIP = dict(help="install or manage MicroPython libs",
            subcmd=dict(help='indicate a lib/module to {install, info, find}',
                        default=[],
                        metavar='file/pattern',
                        nargs='*'),
            options={},
            alt_ops=['install', 'info', 'find'])

TIMEIT = dict(help="measure execution time of a script/function",
              subcmd=dict(help='indicate a script/function to measure',
                          default=[],
                          metavar='script/function',
                          nargs='*'),
              options={})

UPDATE_UPYUTILS = dict(help="update upyutils scripts",
                       subcmd=dict(help=("filter to match one/multiple "
                                         "upyutils; default: all"),
                                   default=['*'],
                                   nargs='*',
                                   metavar='name/pattern'),
                       options={},
                       alt_ops=os.listdir(os.path.join(_UPYDEVPATH[0],
                                                       'upyutils_dir')))
ENABLE_SHELL = dict(help="upload required files so shell is fully operational",
                    subcmd={},
                    options={})

DOCS = dict(help="see upydev docs at https://upydev.readthedocs.io/en/latest/",
            subcmd=dict(help='indicate a keyword to search',
                        metavar='keyword', nargs='?'),
            options={})

MDOCS = dict(help="see MicroPython docs at docs.micropython.org",
             subcmd=dict(help='indicate a keyword to search',
                         metavar='keyword', nargs='?'),
             options={})

CTIME = dict(help="measure execution time of a shell command",
             subcmd=dict(help='indicate a command to measure',
                         default='info',
                         choices=shell_commands+custom_sh_cmd_kw,
                         metavar='command'),
             options={})

CONFIG = dict(help="set or check config (from *_config.py files)#",
              desc="* needs config module\n* to set config --> [config]: "
                   "[parameter]=[value]",
              subcmd=dict(help='indicate parameter to set or check ',
                          default=[],
                          metavar='parameter',
                          nargs='*'),
              options={"-y": dict(help='print config in YAML format',
                                  required=False,
                                  default=False,
                                  action='store_true')})

SD = dict(help="commands to manage an sd",
          desc='enable an sd module, mount/unmount an sd or auto mount/unmount sd\n\n'
               '* auto command needs SD_AM.py in device',
          subcmd=dict(help='actions to mount/unmount sd : {enable, init, deinit, auto}',
                      default='enable',
                      choices=['enable', 'init', 'deinit', 'auto'],
                      metavar='command'),
          options={"-po": dict(help='pin of LDO 3.3V regulator to enable',
                               default=15,
                               type=int),
                   "-sck": dict(help='sck pin for sd SPI',
                                default=5,
                                type=int),
                   "-mosi": dict(help='mosi pin for sd SPI',
                                 default=18,
                                 type=int),
                   "-miso": dict(help='miso pin for sd SPI',
                                 default=19,
                                 type=int),
                   "-cs": dict(help='cs pin for sd SPI',
                               default=21,
                               type=int)})


SHELL_CMD_DICT_PARSER = {"ls": LS, "head": HEAD, "cat": CAT, "mkdir": MKDIR,
                         "touch": TOUCH, "cd": CD, "pwd": PWD,
                         "rm": RM, "rmdir": RMDIR, "du": DU,
                         "tree": TREE, "df": DF, "mem": MEM, "exit": EXIT,
                         "vim": VIM, "run": RUN, "reload": RELOAD,
                         "info": INFO, "id": ID, "uhelp": UHELP, "modules": MODULES,
                         "uping": UPING, "rssi": RSSI, "net": NET, "ifconfig": IFCONFIG,
                         "ap": AP, "i2c": I2C, "set": SET, "datetime": DATETIME,
                         "shasum": SHASUM, "upip": UPIP, "timeit": TIMEIT,
                         "update_upyutils": UPDATE_UPYUTILS,
                         "lcd": LCD,
                         "lsl": LSL, "lpwd": LPWD, "ldu": LDU, "docs": DOCS,
                         "mdocs": MDOCS, "ctime": CTIME, "enable_sh": ENABLE_SHELL,
                         "diff": DIFF, "config": CONFIG, "sd": SD}
