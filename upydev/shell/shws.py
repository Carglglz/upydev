from upydev.shell.commands import ShellCmds, _SHELL_CMDS, _UPYDEVPATH
from upydev.shell.constants import CRED, CEND
from upydev.shell.parser import subshparser_cmd
from upydev.shell.common import CatFileIO
from upydev.shell.shfileio import ShDsyncIO
from upydev.shell.shfwio import ShfwIO
from upydev.shell.upyconfig import show_upy_config_dialog
import subprocess
import shlex
import signal
import shutil
import os

shws_cmd_kw = ["repl", "getcert", "fw", "flash", "debugws", "ota"]

WREPL = dict(help="enter WebREPL",
             subcmd={},
             options={})
GETCERT = dict(help="get device certificate if available",
               subcmd={},
               options={})
JUPYTERC = dict(help="enter jupyter console with upydevice kernel",
                subcmd={},
                options={})

PYTEST = dict(help="run tests on device with pytest (use pytest setup first)",
              subcmd=dict(help='Indicate a test script to run, any optional '
                               'args are passed to pytest',
                          default='',
                          metavar='test'),
              options={})

PUT = dict(help="upload files to device",
           subcmd=dict(help='Indicate a file/pattern/dir to '
                            'upload',
                       default=[],
                       metavar='file/pattern/dir',
                       nargs='+'),
           options={"-dir": dict(help='path to upload to',
                                 required=False,
                                 default='')})

GET = dict(help="download files from device",
           subcmd=dict(help='Indicate a file/pattern/dir to '
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
                    "-fg": dict(help='use a faster get method', required=False,
                                default=False,
                                action='store_true'),
                    "-b": dict(help='read buffer for faster get method', required=False,
                               default=512,
                               type=int)})

DSYNC = dict(help="recursively sync a folder from/to device filesystem",
             subcmd=dict(help='Indicate a dir/pattern to '
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
                      "-fg": dict(help='use a faster get method', required=False,
                                  default=False,
                                  action='store_true'),
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
                      "-n": dict(help='dry-run', required=False,
                                 default=False,
                                 action='store_true'),
                      "-i": dict(help='ignore file/dir or pattern', required=False,
                                 default=[],
                                 nargs='*')})
DEBUG = dict(help="toggle debug mode for websocket debugging",
             subcmd={},
             options={})

FW = dict(help="list or get available firmware from micropython.org",
           subcmd=dict(help=('{list, get, update}'
                             '; default: list'),
                       default=['list'],
                       metavar='action', nargs='*'),
           options={"-b": dict(help='to indicate device platform',
                               required=False),
                    "-n": dict(help='to indicate keyword for filter search',
                                     required=False)},
           alt_ops=['list', 'get', 'update', 'latest'])

OTA = dict(help="to flash a firmware file using OTA system",
             subcmd=dict(help=('Indicate a firmware file to flash'),
                         metavar='firmware file'),
             options={"-i": dict(help='to check wether device platform and '
                                    'firmware file name match',
                                 required=False,
                                 action='store_true'),
                      "-sec": dict(help='to enable OTA TLS',
                                   required=False,
                                   action='store_true')})

MPYX = dict(help="freeze .py files using mpy-cross. (must be available in $PATH)",
            subcmd=dict(help='Indicate a file/pattern to '
                            'compile',
                        default=[],
                        metavar='file/pattern',
                        nargs='+'),
            options={})

UPY_CONFIG = dict(help="enter upy-config dialog",
             subcmd={},
             options={})

SHELLWS_CMD_DICT_PARSER = {"repl": WREPL, "getcert": GETCERT, "jupyterc": JUPYTERC,
                           "pytest": PYTEST, "put": PUT, "get": GET,
                           "dsync": DSYNC, "debugws": DEBUG, "fw": FW, "mpyx": MPYX,
                           "ota": OTA, "upy-config": UPY_CONFIG}


class ShellWsCmds(ShellCmds):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for command, subcmd in SHELLWS_CMD_DICT_PARSER.items():
            _subparser = subshparser_cmd.add_parser(command, help=subcmd['help'],
                                                    description=subcmd['help'])
            if subcmd['subcmd']:
                _subparser.add_argument('subcmd', **subcmd['subcmd'])
            for option, op_kargs in subcmd['options'].items():
                _subparser.add_argument(option, **op_kargs)
        self._shkw = _SHELL_CMDS + shws_cmd_kw
        self.fileio = CatFileIO()
        self.fileio.dev = self.dev
        self.fastfileio = self.fileio
        self.dsyncio = ShDsyncIO(self.dev, self.dev_name, self.fileio, self.fileio,
                                 shell=self)
        self.fwio = ShfwIO(self.dev, self.dev_name)

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None,
                      ukw_args=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        if cmd == 'repl':
            if not topargs.wss:
                print(CRED + 'WARNING: ENCRYPTION DISABLED IN THIS MODE' + CEND)
            print('<-- Device {} MicroPython -->'.format(self.dev_name))
            print('Use CTRL-x to exit, Use CTRL-k to see custom wrepl Keybindings')
            try:
                self.dev.disconnect()
            except Exception:
                pass
            if not topargs.wss:
                web_repl_cmd_str = 'web_repl {} -p {}'.format(topargs.t, topargs.p)
            else:
                web_repl_cmd_str = 'web_repl {} -p {} -wss'.format(topargs.t, topargs.p)
            web_repl_cmd = shlex.split(web_repl_cmd_str)
            try:
                subprocess.call(web_repl_cmd)
                try:
                    self.dev.connect()
                except Exception:
                    pass
            except KeyboardInterrupt:
                try:
                    self.dev.connect()
                except Exception:
                    pass
                pass
                print('')
        if cmd == 'getcert':
            if self.dev._uriprotocol == 'wss':
                devcert = self.dev.ws.sock.getpeercert()
                for key in devcert.keys():
                    value = devcert[key]
                    try:
                        if not isinstance(value, str):
                            if len(value) > 1:
                                print('{}:'.format(key.upper()))
                                for val in value:
                                    if len(val) == 1:
                                        print('- {} : {}'.format(*val[0]))
                                    else:
                                        print('- {} : {}'.format(*val))
                        else:
                            print("{}: {}".format(key.upper(), devcert[key]))
                    except Exception:
                        print("{}: {}".format(key.upper(), devcert[key]))

        if cmd == 'jupyterc':
            if not topargs.wss:
                print(CRED + 'WARNING: ENCRYPTION DISABLED IN THIS MODE' + CEND)
            # print('<-- Device {} MicroPython -->'.format(dev_platform))
            print('Use CTRL-D to exit, Use %lsmagic to see custom magic commands')
            try:
                self.dev.disconnect()
            except Exception:
                pass
            if not topargs.wss:
                jupyter_cmd_str = 'jupyter console --kernel=micropython-upydevice'
            else:
                jupyter_cmd_str = 'jupyter console --kernel=micropython-upydevice'

            jupyter_cmd = shlex.split(jupyter_cmd_str)
            old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

            def preexec_function(action=old_action):
                signal.signal(signal.SIGINT, action)

            try:
                subprocess.call(jupyter_cmd, preexec_fn=preexec_function)
                signal.signal(signal.SIGINT, old_action)
                try:
                    self.dev.connect()
                except Exception:
                    pass
            except KeyboardInterrupt:
                try:
                    self.dev.connect()
                except Exception:
                    pass
                pass
                print('')

        if cmd == 'pytest':
            # setup conftest.py
            if rest_args == 'setup':
                shutil.copy(os.path.join(_UPYDEVPATH[0], 'conftest.py'), '.')
                shutil.copy(os.path.join(_UPYDEVPATH[0], 'pytest.ini'), '.')
                print('pytest setup done!')
            else:
                try:
                    self.dev.disconnect()
                except Exception:
                    pass
                try:
                    pytest_cmd = shlex.split(' '.join([cmd, rest_args]))
                    if '--dev' not in pytest_cmd and '-h' not in pytest_cmd:
                        pytest_cmd += ['--dev', self.dev_name]
                    if ukw_args:
                        pytest_cmd += ukw_args
                    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

                    def preexec_function(action=old_action):
                        signal.signal(signal.SIGINT, action)
                    try:
                        subprocess.call(pytest_cmd, preexec_fn=preexec_function)
                        signal.signal(signal.SIGINT, old_action)
                        try:
                            self.dev.connect()
                        except Exception:
                            pass
                    except Exception as e:
                        print(e)
                        try:
                            self.dev.connect()
                        except Exception:
                            pass
                except Exception as e:
                    print(e)
                    try:
                        self.dev.connect()
                    except Exception:
                        pass

        if cmd == 'put':
            self.dsyncio.fileop(cmd, args, rest_args)

        if cmd == 'get':
            self.dsyncio.fileop(cmd, args, rest_args)

        if cmd == 'dsync':
            # dir_only = True
            # be aware of name length error
            # 1: copy dir structure
            #    get depth level path
            #    get local dirs glob (dir_only)
            #    get device dirs glob()
            #    if dir not in glob dir mkdir
            #    match option -rf:
            #    if dir
            # 2: copy files if modified or new
            #   get (files, hash) local
            #   get (files,  hash) device
            #   match: options -rf (remove if not present local)
            #   if in device and not in local:
            #      device rm
            #
            self.dsyncio.dsync(args, rest_args)
        if cmd == 'debugws':
            state = self.dev.debug
            self.dev.debug = not state
            print(f"debugws: {self.dev.debug}")

        if cmd == 'fw':
            self.fwio.fwop(args, rest_args)

        if cmd == 'mpyx':
            self.fwio.mpycross(args, rest_args)

        if cmd == 'ota':
            self.fwio.ota(args, rest_args)

        if cmd == 'upy-config':
            if not self.dev.dev_platform:
                self.dev.dev_platform = self.dev.wr_cmd('import sys; sys.platform',
                                                        silent=True, rtn_resp=True)

            show_upy_config_dialog(self.dev, self.dev.dev_platform)
