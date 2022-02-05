from upydev.shell.commands import ShellCmds, _SHELL_CMDS, _UPYDEVPATH
from upydev.shell.constants import CRED, CEND
from upydev.shell.parser import subshparser_cmd
from upydev.shell.nanoglob import glob as nglob, _get_path_depth
from upydev.wsio import websocket, get_file, put_file
from upydevice import DeviceException, DeviceNotFound
from upydev.shell.common import tree
from upydev.shell.shasum import shasum
import socket
import subprocess
import shlex
import signal
import shutil
import os

shws_cmd_kw = ["wrepl", "getcert", "fw", "flash"]

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
                               type=int)})

DSYNC = dict(help="recursively sync a folder in device filesystem",
             subcmd=dict(help='Indicate a dir/pattern to '
                         'sync',
                         default=['.'],
                         metavar='dir/pattern',
                         nargs='+'),
             options={"-rf": dict(help='remove recursive force a dir or file deleted'
                                       ' in local directory',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-d": dict(help='sync from device to host', required=False,
                                 default=False,
                                 action='store_true')})

SHELLWS_CMD_DICT_PARSER = {"wrepl": WREPL, "getcert": GETCERT, "jupyterc": JUPYTERC,
                           "pytest": PYTEST, "put": PUT, "get": GET,
                           "dsync": DSYNC}


class ShellWsCmds(ShellCmds):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for command, subcmd in SHELLWS_CMD_DICT_PARSER.items():
            _subparser = subshparser_cmd.add_parser(command, help=subcmd['help'])
            if subcmd['subcmd']:
                _subparser.add_argument('subcmd', **subcmd['subcmd'])
            for option, op_kargs in subcmd['options'].items():
                _subparser.add_argument(option, **op_kargs)
        self._shkw = _SHELL_CMDS + shws_cmd_kw

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None,
                      ukw_args=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        if cmd == 'wrepl':
            if not topargs.wss:
                print(CRED + 'WARNING: ENCRYPTION DISABLED IN THIS MODE' + CEND)
            print('<-- Device {} MicroPython -->'.format(self.dev.dev_platform))
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
            file_match = []
            if args.dir:
                # rest_args = [f"{args.dir}/{file}" for file in rest_args]
                # check dir
                try:
                    self.dev.cmd(f"os.stat('{args.dir}')", silent=True)
                    if self.dev._traceback.decode() in self.dev.response:
                        try:
                            raise DeviceException(self.dev.response)
                        except Exception as e:
                            print(e)
                            print(
                                f'Directory {self.dev_name}:/{args.dir} does NOT exist')
                            return
                except Exception:
                    return
            file_match = nglob(*rest_args, size=True)
            if file_match:
                source = '/'
                file_match = [(sz, file.replace(os.getcwd(), ''))
                              for sz, file in file_match]
                if args.dir:
                    source = args.dir
                    print(f'Uploading files @ {self.dev_name}:/{args.dir} \n')
                else:
                    print(f'Uploading files @ {self.dev_name}:/ \n')
                for sz, name in file_match:
                    print(f'- {name} [{sz/1000:.2f} kB]')

                self.dev.ws.sock.settimeout(10)
                ws = websocket(self.dev.ws.sock)

                for sz, file in file_match:
                    src_file = file
                    if source != '/':
                        if source.startswith('.'):
                            source = source.replace('.', '')
                        dst_file = source + '/' + file.split('/')[-1]
                    else:
                        dst_file = '/' + file.split('/')[-1]
                    if dst_file[-1] == "/":
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += basename
                    print(f"{src_file} -> {self.dev_name}:{dst_file}")
                    print(f'\n{src_file} [{sz/1000:.2f} kB]')
                    try:
                        put_file(ws, src_file, dst_file)
                    except KeyboardInterrupt:
                        print('KeyboardInterrupt: put Operation Canceled')
                        if input('Continue put Operation with next file? [y/n]') == 'y':
                            pass
                        else:
                            raise KeyboardInterrupt
                    except socket.timeout:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:
                            raise DeviceNotFound(f"WebSocketDevice @ "
                                                 f"{self.dev._uriprotocol}://"
                                                 f"{self.dev.ip}:{self.dev.port} "
                                                 f"is not reachable")
                        except Exception as e:
                            print(f'ERROR {e}')

            else:
                print(f'put: {", ".join(rest_args)}: No matching files found in ./')
            return

        if cmd == 'get':
            file_match = []
            if args.d:
                _rest_args = [[('*/' * i) + patt for i in range(args.d)] for patt in
                              rest_args]
                rest_args = []
                for gpatt in _rest_args:
                    for dpatt in gpatt:
                        rest_args.append(dpatt)
            if args.dir:
                rest_args = [f"{args.dir}/{file}" for file in rest_args]
                # check dir
                try:
                    self.dev.cmd(f"os.stat('{args.dir}')", silent=True)
                    if self.dev._traceback.decode() in self.dev.response:
                        try:
                            raise DeviceException(self.dev.response)
                        except Exception as e:
                            print(e)
                            print(
                                f'Directory {self.dev_name}:/{args.dir} does NOT exist')
                            return
                except Exception:
                    return
            file_match = self.dev.cmd(f"from nanoglob import glob; "
                                      f"glob(*{rest_args}, size=True)",
                                      silent=True,
                                      rtn_resp=True)
            if file_match:
                if args.dir:
                    print(f'Downloading files @ {self.dev_name}:/{args.dir}: \n')
                else:
                    print(f'Downloading files @ {self.dev_name}:/ : \n')
                for sz, name in file_match:
                    print(f'- {name} [{sz/1000:.2f} kB]')

                self.dev.ws.sock.settimeout(10)
                ws = websocket(self.dev.ws.sock)
                for size_file_to_get, file in file_match:
                    src_file = file
                    dst_file = '.'
                    if os.path.isdir(dst_file):
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += "/" + basename
                    abs_src_file = src_file
                    if not src_file.startswith('/'):
                        abs_src_file = f'/{src_file}'
                    print(f"{self.dev_name}:{abs_src_file} -> {dst_file}")
                    print(f'\n{src_file} [{size_file_to_get/1000:.2f} kB]')
                    try:
                        get_file(ws, dst_file, src_file, size_file_to_get)
                    except (KeyboardInterrupt, Exception):
                        print('KeyboardInterrupt: get Operation Canceled')
                        # flush ws and reset
                        self.dev.flush()
                        self.dev.disconnect()
                        if input('Continue get Operation with next file? [y/n]') == 'y':
                            self.dev.connect()
                        else:
                            print('Canceling file queue..')
                            self.dev.connect()
                            raise KeyboardInterrupt
                        self.dev.ws.sock.settimeout(10)
                        ws = websocket(self.dev.ws.sock)
                    except socket.timeout:
                        # print(e, 'Device {} unreachable'.format(devname))
                        try:

                            raise DeviceNotFound(f"WebSocketDevice @ "
                                                 f"{self.dev._uriprotocol}://"
                                                 f"{self.dev.ip}:{self.dev.port} "
                                                 f"is not reachable")
                        except Exception as e:
                            print(f'ERROR {e}')
                            return
            else:
                if args.dir:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/{args.dir} ')
                else:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/ ')
            return

        if cmd == 'dsync':
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
            if not args.d:
                # HOST TO DEVICE
                dir_match = nglob(*rest_args, dir_only=True)
                if dir_match:
                    for dir in dir_match:
                        tree(dir)
                        depth_level = _get_path_depth(dir) + 1
                        pattern_dir = [f"{dir}/*{'/*'* i}" for i in range(depth_level)]
                        pattern_dir = [dir] + pattern_dir
                        local_dirs = nglob(*pattern_dir, dir_only=True)
                        dev_dirs = self.dev.wr_cmd(f"glob(*{pattern_dir}, "
                                                   f"dir_only=True)",
                                                   silent=True, rtn_resp=True)
                        dirs_to_make = [
                            ldir for ldir in local_dirs if ldir not in dev_dirs]
                        if dirs_to_make:
                            print('dsync: making new dirs:')
                            for ndir in dirs_to_make:
                                print(f'- {ndir}')
                                self.dev.wr_cmd(f'mkdir("{ndir}")', follow=True)
                        else:
                            print('dsync: no new directories to make')
                        if args.rf:
                            dirs_to_delete = [ddir for ddir in dev_dirs
                                              if ddir not in local_dirs]
                            if dirs_to_delete:
                                print('dsync: deleting old dirs:')
                                for ndir in dirs_to_delete:
                                    print(f'- {ndir}')
                                self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                                self.dev.wr_cmd(f'rmrf(*{dirs_to_delete})',
                                                follow=True)

                        local_files = shasum(*pattern_dir, debug=False, rtn=True)
                        local_files_dict = {
                            fname: fhash for fname, fhash in local_files}
                        if local_files:
                            dev_cmd_files = (f"from shasum import shasum;"
                                             f"shasum(*{pattern_dir}, debug=False, "
                                             f"rtn=True)")
                            dev_files = self.dev.wr_cmd(dev_cmd_files, silent=True,
                                                        rtn_resp=True)
                            if dev_files:
                                files_to_sync = [(os.stat(fts[0])[6], fts[0])
                                                 for fts in local_files if fts not in
                                                 dev_files]
                            else:
                                files_to_sync = [(os.stat(fts)[6], fts)
                                                 for fts in local_files_dict.keys()]

                            if files_to_sync:
                                print('\ndsync: syncing new or modified files:')
                                for sz, name in files_to_sync:
                                    print(f'- {name} [{sz/1000:.2f} kB]')
                                self.dev.ws.sock.settimeout(10)
                                ws = websocket(self.dev.ws.sock)
                                print('')
                                for sz, name in files_to_sync:
                                    print(f"{name} -> {self.dev_name}:{name}")
                                    print(f'\n{name} [{sz/1000:.2f} kB]')
                                    try:
                                        put_file(ws, name, name)
                                    except KeyboardInterrupt:
                                        print('KeyboardInterrupt: put Operation Canceled')
                                        if input('Continue put Operation with next file? [y/n]') == 'y':
                                            pass
                                        else:
                                            raise KeyboardInterrupt
                                    except socket.timeout:
                                        # print(e, 'Device {} unreachable'.format(devname))
                                        try:
                                            raise DeviceNotFound(f"WebSocketDevice @ "
                                                                 f"{self.dev._uriprotocol}://"
                                                                 f"{self.dev.ip}:{self.dev.port} "
                                                                 f"is not reachable")
                                        except Exception as e:
                                            print(f'ERROR {e}')
                            else:
                                print('dsync: no new or modified files to sync')

                            if args.rf:
                                _local_files = [lf[0] for lf in local_files]
                                files_to_delete = [dfile[0] for dfile in dev_files
                                                   if dfile[0] not in _local_files]
                                if files_to_delete:
                                    print('dsync: deleting old files:')
                                    for ndir in files_to_delete:
                                        print(f'- {ndir}')
                                    self.dev.wr_cmd(
                                        'from upysh2 import rmrf', silent=True)
                                    self.dev.wr_cmd(f'rmrf(*{files_to_delete})',
                                                    follow=True)
                                else:
                                    print('dsync: no old files to delete')

                        else:
                            print('dsync: no files found directory tree')

                else:
                    print(
                        f'dsync: {", ".join(rest_args)}: No matching dirs found in ./')
                return
            else:
                # DEVICE TO HOST
                dir_match = self.dev.wr_cmd(f"glob(*{rest_args}, dir_only=True)",
                                            silent=True, rtn_resp=True)
                if dir_match:
                    self.dev.wr_cmd("from nanoglob import _get_path_depth",
                                    silent=True)
                    for dir in dir_match:
                        self.dev.wr_cmd(f"tree('{dir}')", follow=True)
                        depth_level = self.dev.wr_cmd(f"_get_path_depth('{dir}') + 1",
                                                      silent=True, rtn_resp=True)
                        pattern_dir = [f"{dir}/*{'/*'* i}" for i in range(depth_level)]
                        pattern_dir = [dir] + pattern_dir
                        local_dirs = nglob(*pattern_dir, dir_only=True)
                        dev_dirs = self.dev.wr_cmd(f"glob(*{pattern_dir}, "
                                                   f"dir_only=True)",
                                                   silent=True, rtn_resp=True)
                        dirs_to_make = [
                            ddir for ddir in dev_dirs if ddir not in local_dirs]
                        if dirs_to_make:
                            print('dsync: making new dirs:')
                            for ndir in dirs_to_make:
                                print(f'- {ndir}')
                                os.makedirs(ndir)
                                # self.dev.wr_cmd(f'mkdir("{ndir}")', follow=True)
                        else:
                            print('dsync: no new directories to make')
                        if args.rf:
                            dirs_to_delete = [ldir for ldir in local_dirs
                                              if ldir not in dev_dirs]
                            if dirs_to_delete:
                                print('dsync: deleting old dirs:')
                                for ndir in dirs_to_delete:
                                    print(f'- {ndir}')
                                shutil.rmtree(ndir)

                        dev_cmd_files = (f"from shasum import shasum;"
                                         f"shasum(*{pattern_dir}, debug=False, "
                                         f"rtn=True, size=True)")
                        dev_files = self.dev.wr_cmd(dev_cmd_files, silent=True,
                                                    rtn_resp=True)

                        if dev_files:
                            local_files = shasum(*pattern_dir, debug=False, rtn=True,
                                                 size=True)

                            if local_files:
                                files_to_sync = [(fts[1], fts[0])
                                                 for fts in dev_files if fts not in
                                                 local_files]
                            else:
                                files_to_sync = [(fts[1], fts[0])
                                                 for fts in dev_files]

                            if files_to_sync:
                                print('\ndsync: syncing new or modified files:')
                                for sz, name in files_to_sync:
                                    print(f'- {name} [{sz/1000:.2f} kB]')
                                self.dev.ws.sock.settimeout(10)
                                ws = websocket(self.dev.ws.sock)
                                print('')
                                for sz, name in files_to_sync:
                                    print(f"{self.dev_name}:{name} -> {name}")
                                    print(f'\n{name} [{sz/1000:.2f} kB]')
                                    try:
                                        get_file(ws, name, name,
                                                 sz)
                                    except (KeyboardInterrupt, Exception):
                                        print('KeyboardInterrupt: get Operation Canceled')
                                        # flush ws and reset
                                        self.dev.flush()
                                        self.dev.disconnect()
                                        if input('Continue get Operation with next file? [y/n]') == 'y':
                                            self.dev.connect()
                                        else:
                                            print('Canceling file queue..')
                                            self.dev.connect()
                                            raise KeyboardInterrupt
                                        self.dev.ws.sock.settimeout(10)
                                        ws = websocket(self.dev.ws.sock)
                                    except socket.timeout:
                                        # print(e, 'Device {} unreachable'.format(devname))
                                        try:

                                            raise DeviceNotFound(f"WebSocketDevice @ "
                                                                 f"{self.dev._uriprotocol}://"
                                                                 f"{self.dev.ip}:{self.dev.port} "
                                                                 f"is not reachable")
                                        except Exception as e:
                                            print(f'ERROR {e}')
                                            return
                            else:
                                print('dsync: no new or modified files to sync')

                            if args.rf:
                                _dev_files = [df[0] for df in dev_files]
                                files_to_delete = [dfile[0] for dfile in local_files
                                                   if dfile[0] not in _dev_files]
                                if files_to_delete:
                                    print('dsync: deleting old files:')
                                    for ndir in files_to_delete:
                                        print(f'- {ndir}')
                                    os.remove(ndir)
                                else:
                                    print('dsync: no old files to delete')

                        else:
                            print('dsync: no files found directory tree')

                else:
                    print(
                        f'dsync: {", ".join(rest_args)}: No matching dirs found in ./')
                return
