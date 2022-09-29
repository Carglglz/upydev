import os
from upydev import __path__
UPYDEV_PATH = __path__[0]

# SHELL_CMD_PARSER

shell_commands = ['cd', 'mkdir', 'cat', 'head', 'rm', 'rmdir', 'pwd',
                  'run', 'mv']
custom_sh_cmd_kw = ['df', 'datetime', 'ifconfig', 'net',
                    'ap', 'mem', 'install', 'touch',
                    'exit', 'lpwd', 'lsl', 'lcd', 'put', 'get', 'ls',
                    'set', 'tree', 'dsync', 'reload', 'docs',
                    'du', 'ldu', 'upip', 'uping',
                    'timeit', 'i2c',
                    'upy-config', 'jupyterc', 'pytest', 'rssi',
                    'info', 'id', 'uhelp', 'modules', 'shasum', 'vim',
                    'update_upyutils', 'mdocs', 'ctime', 'enable_sh',
                    'diff', 'config', 'fw', 'mpyx', 'sd', 'uptime', 'cycles', 'play']

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

MV = dict(help="move/rename a file",
          subcmd=dict(help='indicate a file to rename', default=[],
                      metavar='file', nargs=2),
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

UPTIME = dict(help=("prints device's uptime since latest boot, "
                    "(requires uptime.py and uptime.settime()"
                    " at boot.py/main.py)"),
              subcmd={},
              options={})

CYCLES = dict(help=("prints device's cycle count"
                    "(requires cycles.py and cycles.set()"
                    " at boot.py/main.py)"),
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
                       alt_ops=os.listdir(os.path.join(UPYDEV_PATH,
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

LOAD = dict(help="run local script in device",
            desc="load a local script in device buffer and execute it.",
            subcmd=dict(help='indicate a file/script to load', default='',
                        metavar='file',
                        nargs='*'),
            options={})


SHELL_CMD_DICT_PARSER = {"ls": LS, "head": HEAD, "cat": CAT, "mkdir": MKDIR,
                         "touch": TOUCH, "cd": CD, "mv": MV, "pwd": PWD,
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
                         "diff": DIFF, "config": CONFIG, "sd": SD, 'uptime': UPTIME,
                         "cycles": CYCLES, "load": LOAD}

# DEBUGGING
PING = dict(help="ping the device to test if device is"
                 " reachable, CTRL-C to stop.",
            desc="this sends ICMP ECHO_REQUEST packets to device",
            subcmd={},
            options={"-t": dict(help="device target address",
                                required=True),
                     "-p": dict(help='device password or baudrate',
                                required=True),
                     "-zt": dict(help='internal flag for zerotierone device',
                                 required=False,
                                 default=False,
                                 action='store_true')})

PROBE = dict(help="to test if a device is reachable",
             desc="ping, scan serial ports or ble scan depending on device type",
             subcmd={},
             options={"-t": dict(help="device target address",
                                 required=True),
                      "-p": dict(help='device password or baudrate',
                                 required=True),
                      "-zt": dict(help='internal flag for zerotierone device',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-G": dict(help='internal flag for group mode',
                                 required=False,
                                 default=None),
                      "-gg": dict(help='flag for global group',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-devs": dict(help='flag for filtering devs in global group',
                                    required=False,
                                    nargs='*')})

SCAN = dict(help="to scan for available devices, use a flag to filter for device type",
            desc="\ndefault: if no flag provided will do all three scans.",
            subcmd={},
            options={"-sr": dict(help="scan for SerialDevice",
                                 required=False,
                                 default=False,
                                 action='store_true'),
                     "-nt": dict(help='scan for WebSocketDevice',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                     "-bl": dict(help='scan for BleDevice',
                                 required=False,
                                 default=False,
                                 action='store_true')})

RUN = dict(help="run a script in device, CTRL-C to stop",
           desc="this calls 'import [script]' in device and reloads it at the end",
           subcmd=dict(help=('indicate a script to run'),
                       metavar='script'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-s": dict(help='indicate the path of the script if in external fs'
                                    ' e.g. an sd card.',
                               required=False)})


PLAY = dict(help="play custom tasks in ansible playbook style",
            desc="task must be yaml file with name, hosts, tasks, name, command\n"
                 "structure",
            subcmd=dict(help=('indicate a task file to play.'),
                        metavar='task',
                        choices=["add", "rm", "list"]),
            options={"-t": dict(help="device target address",
                                required=True),
                     "-p": dict(help='device password or baudrate',
                                required=True),
                     "-wss": dict(help='use WebSocket Secure',
                                  required=False,
                                  default=False,
                                  action='store_true')})

TIMEIT = dict(help="to measure execution time of a module/script",
              desc="source: https://github.com/peterhinch/micropython-samples"
                   "/tree/master/timed_function",
              subcmd=dict(help=('indicate a script to run'),
                          metavar='script'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true'),
                       "-s": dict(help='indicate the path of the script if in external'
                                  ' fs e.g. an sd card.',
                                  required=False)})
STREAM_TEST = dict(help="to test download speed (from device to host)",
                   desc="default: 10 MB of random bytes are sent in chunks of 20 kB "
                        "and received in chunks of 32 kB.\n\n*(sync_tool.py required)",
                   subcmd={},
                   options={"-t": dict(help="device target address",
                                       required=True),
                            "-p": dict(help='device password or baudrate',
                                       required=True),
                            "-wss": dict(help='use WebSocket Secure',
                                         required=False,
                                         default=False,
                                         action='store_true'),
                            "-chunk_tx": dict(help='chunk size of data packets in kB to'
                                                   ' send',
                                              required=False, default=20, type=int),
                            "-chunk_rx": dict(help='chunk size of data packets in kB to'
                                                   ' receive',
                                              required=False, default=32, type=int),
                            "-total_size": dict(help='total size of data packets in MB',
                                                required=False, default=10, type=int)})

SYSCTL = dict(help="to start/stop a script without following the output",
              desc="to follow initiate repl",
              mode=dict(help='indicate a mode {start,stop}',
                        metavar='mode',
                        choices=['start', 'stop']),
              subcmd=dict(help='indicate a script to start/stop',
                          metavar='script'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true')})

LOG = dict(help="to log the output of a script running in device",
           desc="log levels (sys.stdout and file), run modes (normal, daemon) are"
                "available through following options",
           subcmd=dict(help=('indicate a script to run and log'),
                       metavar='script'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-s": dict(help='indicate the path of the script if in external fs'
                                    ' e.g. an sd card.',
                               required=False),
                    "-dflev": dict(help='debug file mode level; default: error',
                                   default='error',
                                   choices=['debug', 'info', 'warning', 'error',
                                            'critical']),
                    "-dslev": dict(help='debug sys.stdout mode level; default: debug',
                                   default='debug',
                                   choices=['debug', 'info', 'warning', 'error',
                                            'critical']),
                    "-daemon": dict(help='enable "daemon mode", uses nohup so this '
                                         'means running in background, output if any is'
                                         ' redirected to [SCRIPT_NAME]_daemon.log',
                                    default=False, action='store_true'),
                    "-stopd": dict(help='To stop a log daemon script',
                                   default=False, action='store_true'),
                    "-F": dict(help='To follow a daemon log script file',
                               action='store_true',
                               default=False)})

PYTEST = dict(help="run tests on device with pytest (use pytest setup first)",
              subcmd=dict(help='indicate a test script to run, any optional '
                               'arg is passed to pytest',
                          default=[''],
                          metavar='test',
                          nargs='*'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true')})


DB_CMD_DICT_PARSER = {"ping": PING, "probe": PROBE, "scan": SCAN, "run": RUN,
                      "timeit": TIMEIT, "stream_test": STREAM_TEST, "sysctl": SYSCTL,
                      "log": LOG, "pytest": PYTEST, "play": PLAY}

# DEVICE MANAGEMENT
CONFIG = dict(help="to save device settings",
              desc="this will allow set default device configuration or \n"
                   "target a specific device in a group.\n"
                   "\ndefault: a configuration file 'upydev_.config' is saved in\n"
                   "current working directory, use -[options] for custom configuration",
              subcmd={},
              options={"-t": dict(help="device target address"),
                       "-p": dict(help='device password or baudrate'),
                       "-g": dict(help='save configuration in global path',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                       "-gg": dict(help='save device configuration in global group',
                                   required=False,
                                   default=False,
                                   action='store_true'),
                       "-@": dict(help='specify a device name',
                                  required=False),
                       "-zt": dict(help='zerotierone device configuration',
                                   required=False),
                       "-sec": dict(help='introduce password with no echo',
                                    required=False,
                                    default=False,
                                    action='store_true')})

CHECK = dict(help='to check device information',
             desc='shows current device information or specific device\n'
                  'indicated with -@ option if it is stored in the global group.',
             subcmd={},
             options={"-@": dict(help='specify device/s name',
                                 required=False,
                                 nargs='+'),
                      "-i": dict(help='if device is online/connected gets device info',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                      "-g": dict(help='looks for configuration in global path',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                      "-wss": dict(help='use WebSocket Secure',
                                   required=False,
                                   default=False,
                                   action='store_true'),
                      "-G": dict(help='specify a group, default: global group',
                                 required=False)})

SET = dict(help='to set current device configuration',
           subcmd={},
           options={"-@": dict(help='specify device name',
                               required=False),
                    "-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-G": dict(help='specify a group, default: global group',
                               required=False)})

REGISTER = dict(help='to register a device/group as a shell function so it is callable',
                subcmd=dict(help='alias for device/s or group',
                            metavar='alias',
                            nargs='*'),
                options={"-@": dict(help='specify device name',
                                    required=False,
                                    nargs='+'),
                         "-gg": dict(help='register a group of devices',
                                     required=False,
                                     default=False,
                                     action='store_true'),
                         "-s": dict(help='specify a source file, default: ~/.profile',
                                    required=False),
                         "-g": dict(help='looks for configuration in global path',
                                    required=False,
                                    default=False,
                                    action='store_true')})

LSDEVS = dict(help='to see registered devices or groups',
              desc='this also defines a shell function with the same name in the source'
                   ' file',
              subcmd={},
              options={"-s": dict(help='specify a source file, default: ~/.profile',
                                  required=False),
                       "-G": dict(help='specify a group, default: global group',
                                  required=False)})

MKG = dict(help='make a group of devices',
           desc='this save a config file with devices settings so they can be targeted'
                ' all together',
           subcmd=dict(help='group name',
                       metavar='group'),
           options={"-g": dict(help='save configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-devs": dict(help='device configuration [name] [target] '
                                       '[password]',
                                  required=False,
                                  nargs='+')})

GG = dict(help='to see global group of devices',
          subcmd={},
          options={"-g": dict(help='looks for configuration in global path',
                              required=False,
                              default=False,
                              action='store_true')})

SEE = dict(help='to see a group of devices',
           subcmd=dict(help='indicate a group name',
                       metavar='group'),
           options={"-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true')})

MGG = dict(help='manage a group of devices',
           desc='add/remove one or more devices to/from a group',
           subcmd=dict(help='group name',
                       metavar='group',
                       default='UPY_G',
                       nargs='?'),
           options={"-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-add": dict(help='add device/s name',
                                 required=False,
                                 nargs='*'),
                    "-rm": dict(help='remove device/s name',
                                required=False,
                                nargs='*'),
                    "-gg": dict(help='manage global group',
                                required=False,
                                default=False,
                                action='store_true')})

MKSG = dict(help='manage a subgroup of devices',
            desc='make group from another group with a subset of devices',
            subcmd=dict(help='group name',
                        metavar='group',
                        default='UPY_G',
                        nargs='?'),
            sgroup=dict(help='subgroup name',
                        metavar='subgroup'),
            options={"-g": dict(help='looks for configuration in global path',
                                required=False,
                                default=False,
                                action='store_true'),
                     "-devs": dict(help='add device/s name',
                                   required=True,
                                   nargs='*'),
                     "-gg": dict(help='manage global group',
                                 required=False,
                                 default=False,
                                 action='store_true')})

DM_CMD_DICT_PARSER = {"config": CONFIG, "check": CHECK,
                      "register": REGISTER, "lsdevs": LSDEVS, "mkg": MKG, "gg": GG,
                      "see": SEE, "mgg": MGG, "mksg": MKSG}

# FW
MPYX = dict(help="freeze .py files using mpy-cross. (must be available in $PATH)",
            subcmd=dict(help='indicate a file/pattern to '
                             'compile',
                        default=[],
                        metavar='file/pattern',
                        nargs='+'),
            options={})

FW = dict(help="list or get available firmware from micropython.org",
          subcmd=dict(help=('{list, get, update}'
                            '; default: list'),
                      default=['list'],
                      metavar='action', nargs='*'),
          options={"-b": dict(help='to indicate device platform',
                              required=False),
                   "-n": dict(help='to indicate keyword for filter search',
                              required=False),
                   "-t": dict(help="device target address",
                              required=True),
                   "-p": dict(help='device password or baudrate',
                              required=True),
                   "-wss": dict(help='use WebSocket Secure',
                                required=False,
                                default=False,
                                action='store_true')},
          alt_ops=['list', 'get', 'update', 'latest'])

FLASH = dict(help="to flash a firmware file using available serial tools "
             "(esptool.py, pydfu.py)",
             subcmd=dict(help=('indicate a firmware file to flash'),
                         metavar='firmware file'),
             options={"-i": dict(help='to check wether device platform and '
                                 'firmware file name match',
                                 required=False,
                                 action='store_true'),
                      "-t": dict(help="device target address",
                                 required=True),
                      "-p": dict(help='device baudrate',
                                 required=True),
                      })

OTA = dict(help="to flash a firmware file using OTA system (ota.py, otable.py)",
           subcmd=dict(help=('indicate a firmware file to flash'),
                       metavar='firmware file'),
           options={"-i": dict(help='to check wether device platform and '
                               'firmware file name match',
                               required=False,
                               action='store_true'),
                    "-sec": dict(help='to enable OTA TLS',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-zt": dict(help='zerotierone host IP',
                                required=False,
                                default=False)})


FW_CMD_DICT_PARSER = {"mpyx": MPYX, "fwr": FW, "flash": FLASH, "ota": OTA}

# GC
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
GC_CMD_DICT_PARSER = {"reset": RESET, "uconfig": CONFIG, "kbi": KBI, "upysh": UPYSH}

# KG
KG = dict(help="to generate a key pair (RSA) or key & certificate (ECDSA) for ssl",
          desc="generate key pair and exchange with device, or refresh WebREPL "
               "password",
          mode=dict(help='indicate a key {rsa, ssl, wr}',
                    metavar='mode',
                    choices=['rsa', 'ssl', 'wr'],
                    nargs='?'),
          subcmd=dict(help='- gen: generate a ECDSA key/cert (default)'
                           '\n- rotate: To rotate CA key/cert pair old->new or'
                           ' new->old'
                           '\n- add: add a device cert to upydev path verify location.'
                           '\n- export: export CA or device cert to cwd.',
                      metavar='subcmd',
                      # just for arg completion
                      choices=['gen', 'add', 'export', 'rotate', 'dev', 'host', 'CA',
                               'status'],
                      default='gen',
                      nargs='?'),
          dst=dict(help='indicate a subject: {dev, host, CA}, default: dev',
                   metavar='dest',
                   choices=['dev', 'host', 'CA'],
                   default='dev',
                   nargs='?'),
          options={"-t": dict(help="device target address",
                              required=True),
                   "-p": dict(help='device password or baudrate',
                              required=True),
                   "-wss": dict(help='use WebSocket Secure',
                                required=False,
                                default=False,
                                action='store_true'),
                   "-zt": dict(help='internal flag for zerotierone device',
                               required=False,
                               default=False,
                               action='store_true'),
                   "-rst": dict(help='internal flag for reset',
                                required=False,
                                default=False,
                                action='store_true'),
                   "-key_size": dict(help="RSA key size, default:2048",
                                     default=2048,
                                     required=False,
                                     type=int),
                   "-show_key": dict(help='show generated RSA key',
                                     required=False,
                                     default=False,
                                     action='store_true'),
                   "-tfkey": dict(help='transfer keys to device',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                   "-rkey": dict(help='option to remove private device key from host',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                   "-g": dict(help='option to store new WebREPL password globally',
                              required=False,
                              default=False,
                              action='store_true'),
                   "-to": dict(help='serial device name to upload to',
                               required=False),
                   "-f": dict(help='cert name to add to verify locations',
                              required=False),
                   "-a": dict(
                       help="show all devs ssl cert status",
                       required=False,
                       default=False,
                       action="store_true",
                   ), })

RSA = dict(help="to perform operations with RSA key pair as sign, verify or "
                "authenticate",
           desc="sign files, verify signatures or authenticate devices with "
                "RSA challenge\nusing device keys or host keys",
           mode=dict(help='indicate an action {sign, verify, auth}',
                     metavar='mode',
                     choices=['sign', 'verify', 'auth']),
           subcmd=dict(help='indicate a file to sign/verify',
                       metavar='file/signature',
                       nargs='?'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-host": dict(help='to use host keys',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                    "-rst": dict(help='internal flag for reset',
                                 required=False,
                                 default=False,
                                 action='store_true')})

KG_CMD_DICT_PARSER = {"kg": KG, "rsa": RSA}

# SHELL-REPL
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

# REPL
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

# FIO
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

ALL_PARSER = {}
ALL_PARSER.update(SHELL_CMD_DICT_PARSER)
ALL_PARSER.update(DB_CMD_DICT_PARSER)
ALL_PARSER.update(DM_CMD_DICT_PARSER)
ALL_PARSER.update(FW_CMD_DICT_PARSER)
ALL_PARSER.update(GC_CMD_DICT_PARSER)
ALL_PARSER.update(KG_CMD_DICT_PARSER)
ALL_PARSER.update(SHELLREPL_CMD_DICT_PARSER)
ALL_PARSER.update(REPL_CMD_DICT_PARSER)
ALL_PARSER.update(FIO_CMD_DICT_PARSER)


def argopts_complete(option):
    if option in ALL_PARSER.keys():
        opt_args = []
        if ALL_PARSER[option]['subcmd']:
            choices = ALL_PARSER[option]['subcmd'].get('choices')
            if choices:
                opt_args += choices
        if 'mode' in ALL_PARSER[option].keys():
            choices = ALL_PARSER[option]['mode'].get('choices')
            if choices:
                opt_args += choices
        alt_ops = ALL_PARSER[option].get('alt_ops')
        if alt_ops:
            opt_args += alt_ops
        kw_args = ALL_PARSER[option].get('options')
        if kw_args:
            opt_args += list(kw_args.keys())
        return opt_args
    else:
        return []


def get_opts_dict(option):
    kw_args = ALL_PARSER[option].get('options')
    if kw_args:
        return kw_args
    else:
        return {}
