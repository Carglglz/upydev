from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from pygments.styles import get_all_styles

# Prompt Style
style_p = Style.from_dict({
    # User input (default text).
    '':          '#ffffff',

    # Prompt.
    'userpath': 'ansimagenta bold',
    'username': 'ansigreen bold',
    'at':       'ansigreen bold',
    'colon':    '#ffffff',
    'pound':    'ansiblue bold',
    'host':     'ansigreen bold',
    'path':     'ansiblue bold',
})

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
                    'ap', 'mem', 'install', 'touch', 'edit', 'wrepl',
                    'whoami', 'exit', 'lpwd', 'lsl', 'lcd', 'put', 'get', 'ls',
                    'set', 'tree', 'fget', 'dsync', 'reload', 'docs',
                    'getcert', 'bat', 'du', 'ldu', 'upip', 'uping',
                    'timeit', 'i2c', 'git', 'batstyle',
                    'upy-config', 'wss', 'jupyterc', 'pytest', 'rssi',
                    'info', 'id', 'uhelp', 'modules', 'shasum', 'dvim']

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
PYGM_SYNTAX = list(get_all_styles()) + ['one_dark']
batstyle = {'style': 'monokai'}
AUTHMODE_DICT = {0: 'NONE', 1: 'WEP', 2: 'WPA PSK', 3: 'WPA2 PSK',
                    4: 'WPA/WAP2 PSK'}

git_diff_files = {'diff': [], 'commit': '', 'n_commits': 0}


# KEYBINDINGS INFO
kb_info = """
Custom keybindings:
- CTRL-x : to exit SSLWebREPL Terminal
- CTRL-p : toggle RAM STATUS right aligned message (USED/FREE)
- CTRL-e : paste mode in repl,(in shell mode set cursor position at the end)/(edit mode after 'edit' shell command)
- CTRL-d : ends paste mode in repl, (ends edit mode after 'edit' shell command)
- CTRL-c : KeyboardInterrupt, in normal mode, cancel in paste or edit mode
- CTRL-b : prints MicroPython version and sys platform
- CTRL-r : to flush line buffer
- CTRL-o : to list files in cwd (sz shorcut command)
- CTRL-n : shows mem_info()
- CTRL-y : gc.collect() shortcut command
- CTRL-space : repeats last command
- CTRL-t : runs test_code.py if present
- CTRL-w : flush test_code from sys modules, so it can be run again
- CTRL-a : set cursor position at the beggining
- CTRL-f : toggle autosuggest mode (Fish shell like)(use right arrow to complete)
- CTRL-g : To active listen for device output (Timer or hardware interrupts), CTRL-c to break
- CRTL-s : toggle shell mode to navigate filesystem (see shell commands)
- CTRL-k : prints the custom keybindings (this list) (+ shell commands if in shell mode)
>>> """


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
LS = dict(help="list device files or directories",
          subcmd=dict(help='Indicate a file/dir or pattern to see', default=[],
                      metavar='file/dir/pattern', nargs='*'),
          options={"-a": dict(help='list hidden files', required=False,
                              default=False,
                              action='store_true')})
HEAD = dict(help="display first lines of a file",
            subcmd=dict(help='Indicate a file or pattern to see', default=[],
                        metavar='file/pattern', nargs='*'),
            options={"-n": dict(help='number of lines to print', required=False,
                                default=10,
                                type=int)})
CAT = dict(help="concatenate and print files",
           subcmd=dict(help='Indicate a file or pattern to see', default=[],
                       metavar='file/pattern', nargs='*'),
           options={})

MKDIR = dict(help="make directories",
             subcmd=dict(help='Indicate a dir/pattern to create', default=[],
                         metavar='dir', nargs='*'),
             options={})

CD = dict(help="change current working directory",
          subcmd=dict(help='Indicate a dir to change to', default='/',
                      metavar='dir', nargs='?'),
          options={})
PWD = dict(help="print current working directory",
           subcmd={},
           options={})
RM = dict(help="remove file or pattern of files",
          subcmd=dict(help='Indicate a file/pattern to remove', default=[],
                      metavar='file/dir/pattern', nargs='*'),
          options={"-rf": dict(help='remove recursive force a dir or file',
                               required=False,
                               default=10,
                               action='store_true')})
RMDIR = dict(help="remove directories or pattern of directories",
             subcmd=dict(help='Indicate a dir/pattern to remove', default=[],
                         metavar='dir', nargs='*'),
             options={})

DU = dict(help="display disk usage statistics",
          subcmd=dict(help='Indicate a dir to see usage', default=[],
                      metavar='dir', nargs='*'),
          options={"-d": dict(help='depth level', required=False,
                              default=0,
                              type=int)})
TREE = dict(help="list contents of directories in a tree-like format",
            subcmd=dict(help='Indicate a dir to see', default='',
                        metavar='dir', nargs='?'),
            options={"-a": dict(help='list hidden files', required=False,
                                default=False,
                                action='store_true')})
DF = dict(help="display free disk space",
          subcmd={},
          options={})

MEM = dict(help="show RAM usage info",
           subcmd=dict(help='mem info (default) or dump memory',
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

SHELL_CMD_DICT_PARSER = {"ls": LS, "head": HEAD, "cat": CAT, "mkdir": MKDIR,
                         "cd": CD, "rm": RM, "rmdir": RMDIR, "du": DU,
                         "tree": TREE, "df": DF, "mem": MEM, "exit": EXIT}
