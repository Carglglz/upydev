from upydev.shell.commands import ShellCmds, _SHELL_CMDS, _UPYDEVPATH
from upydev.shell.parser import subshparser_cmd
from upydevice import DeviceException
from upydev.bleio import BleFileIO
from upydev.shell.common import CatFileIO
from upydev.shell.shfileio import ShDsyncIO
from upydev.shell.shfwio import ShfwIO
from upydev.shell.upyconfig import show_upy_config_dialog
import subprocess
import shlex
import signal
import shutil
import os

shbl_cmd_kw = ["services", "ota"]


SERVS = dict(help="show GATT services and characteristics",
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
                                action='store_true')})

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

SHELLBLE_CMD_DICT_PARSER = {"jupyterc": JUPYTERC,
                            "pytest": PYTEST, "put": PUT, "get": GET,
                            "dsync": DSYNC, "fw": FW, "mpyx": MPYX, "ota": OTA,
                            "services": SERVS, "upy-config": UPY_CONFIG}


class ShellBleCmds(ShellCmds):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for command, subcmd in SHELLBLE_CMD_DICT_PARSER.items():
            _subparser = subshparser_cmd.add_parser(command, help=subcmd['help'],
                                                    description=subcmd['help'])
            if subcmd['subcmd']:
                _subparser.add_argument('subcmd', **subcmd['subcmd'])
            for option, op_kargs in subcmd['options'].items():
                _subparser.add_argument(option, **op_kargs)
        self._shkw = _SHELL_CMDS + shbl_cmd_kw
        self.fileio = BleFileIO(self.dev, devname=self.dev_name)
        self.fastfileio = CatFileIO()
        self.fastfileio.dev = self.dev
        self.dsyncio = ShDsyncIO(self.dev, self.dev_name, self.fileio, self.fastfileio,
                                 shell=self)
        self.fwio = ShfwIO(self.dev, self.dev_name)

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None,
                      ukw_args=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        if cmd == 'brepl':
            print('<-- Device {} MicroPython -->'.format(self.dev_name))
            print('Use CTRL-a,CTRL-x to exit')
            try:
                self.dev.disconnect()
            except Exception:
                pass
            serial_repl_cmd_str = 'picocom {} -b115200'.format(topargs.p)
            serial_repl_cmd = shlex.split(serial_repl_cmd_str)
            try:
                subprocess.call(serial_repl_cmd)
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

        if cmd == 'services':
            self.dev.get_services()

        if cmd == 'jupyterc':
            # print('<-- Device {} MicroPython -->'.format(dev_platform))
            print('Use CTRL-D to exit, Use %lsmagic to see custom magic commands')
            try:
                self.dev.disconnect()
            except Exception:
                pass

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
