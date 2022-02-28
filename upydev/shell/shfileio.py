from upydev.shell.nanoglob import glob as nglob, _get_path_depth
from upydevice import DeviceException, DeviceNotFound
from upydev.shell.common import tree, print_size
from upydev.shell.constants import CHECK
from upydev.shell.shasum import shasum
from upydev.wsio import websocket, get_file, put_file
import shutil
import os
import socket
import re
import sys
import hashlib
import binascii


def fname(cnt, name):
    if cnt == 1:
        return f"{cnt} {name}"
    else:
        return f"{cnt} {name}s"


class ShDsyncIO:
    def __init__(self, dev, dev_name, fileio, fastfileio, shell=None):
        self.dev = dev
        self.dev_name = dev_name
        self.fileio = fileio
        self.fastfileio = fastfileio
        self.shell = shell
        self.stash = {}

    def _re_match_filt(self, patt, files_dirs, raw=False):
        if patt.startswith('r!'):
            raw = True
            patt = patt.replace('r!', '')
        elif patt.startswith('r:'):
            raw = True
            patt = patt.replace('r:', '')
            patt = r"^[^\/]*\/\.*[^\/]*" + patt.replace('.', r'\.').replace('*', '.*')
        if not raw:
            pattrn = re.compile(patt.replace('.', r'\.').replace('*', '.*') + '$')
        else:
            pattrn = re.compile(r"^{}$".format(patt))
        try:
            return [file for file in files_dirs if not pattrn.match(file)]
        except Exception:
            return []

    def re_filt(self, pattrn_list, files_dirs):
        filtered = files_dirs
        for patt in pattrn_list:
            filtered = self._re_match_filt(patt, filtered)
        return filtered

    def sr_put(self, src_name, sz, dst_name):
        try:
            self.fastfileio.init_put(src_name, sz)
            self.fastfileio.sraw_put_file(src_name, dst_name)
        except KeyboardInterrupt:
            print('KeyboardInterrupt: put Operation Canceled')
            self.dev.cmd("f.close()", silent=True)
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt
        except Exception as e:
            print(f'put: Operation failed, reason: {e}')
            self.dev.cmd("f.close()", silent=True)
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt

    def sr_get(self, args, src_name, sz, dst_name):
        if not args.fg:
            try:
                self.fileio.get((sz, src_name), dst_name,
                                fullpath=True, psize=False)
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
                self.dev.cmd("f.close()", silent=True)
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt
            except Exception as e:
                print(f'get: Operation failed, reason: {e}')
                self.dev.cmd("f.close()", silent=True)
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt
        else:
            try:  # FAST GET
                self.fastfileio.init_get(dst_name, sz)
                cmd_gf = (f"rcat('{src_name}', buff={args.b});"
                          f"gc.collect()")
                if sz > 0:
                    self.fastfileio.sr_get_file(cmd_gf)
                    self.fastfileio.save_file()
                else:
                    ff = self.fastfileio
                    ff.do_pg_bar(self.fastfileio.bar_size,
                                 self.fastfileio.wheel,
                                 f"{0:.2f}/{0:.2f} KB",
                                 "0", 0, 0, 1, 0)
                print('\n')
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt
            except Exception as e:
                print(f'get: Operation failed, reason: {e}')
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt

    def ws_put(self, src_name, sz, dst_name):
        self.dev.ws.sock.settimeout(10)
        ws = websocket(self.dev.ws.sock)
        try:
            put_file(ws, src_name, dst_name)
        except KeyboardInterrupt:
            print('KeyboardInterrupt: put Operation Canceled')
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt
        except Exception as e:
            print(f'put: Operation failed, reason: {e}')
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt
        except socket.timeout:
            try:
                raise DeviceNotFound(f"WebSocketDevice @ "
                                     f"{self.dev._uriprotocol}://"
                                     f"{self.dev.ip}:{self.dev.port} "
                                     f"is not reachable")
            except Exception as e:
                print(f'ERROR {e}')

    def ws_get(self, args, src_name, sz, dst_name):
        if not args.fg:
            self.dev.ws.sock.settimeout(10)
            ws = websocket(self.dev.ws.sock)
            try:
                get_file(ws, dst_name, src_name,
                         sz)
            except KeyboardInterrupt:
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
            except Exception as e:
                print(f'get: Operation failed, reason: {e}')
                self.dev.flush()
                self.dev.disconnect()
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    self.dev.connect()
                    raise KeyboardInterrupt
            except socket.timeout:
                try:

                    raise DeviceNotFound(f"WebSocketDevice @ "
                                         f"{self.dev._uriprotocol}://"
                                         f"{self.dev.ip}:{self.dev.port} "
                                         f"is not reachable")
                except Exception as e:
                    print(f'ERROR {e}')
                    return
        else:  # FAST GET
            try:
                self.fileio.init_get(dst_name, sz)
                cmd_gf = (f"rcat('{src_name}', buff={args.b},"
                          f" stream=wss_repl.client_swr);"
                          f"gc.collect()")
                if sz > 0:
                    # self.fileio.ws_get_file(cmd_gf)
                    self.fileio.rs_get_file(cmd_gf,
                                            chunk=args.b)
                    self.fileio.save_file()
                else:
                    self.fileio.do_pg_bar(self.fileio.bar_size,
                                          self.fileio.wheel,
                                          f"{0:.2f}/{0:.2f} KB",
                                          "0", 0, 0, 1, 0)
                print('\n')
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt
            except Exception as e:
                print(f'get: Operation failed, reason: {e}')
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt

    def ble_put(self, src_name, sz, dst_name):
        try:
            self.fileio.put(src_name, dst_name, psize=False)
        except KeyboardInterrupt:
            print('KeyboardInterrupt: put Operation Canceled')
            self.dev.cmd("f.close()", silent=True)
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt
        except Exception as e:
            print(f'put: Operation failed, reason: {e}')
            self.dev.cmd("f.close()", silent=True)
            if input('Continue put Operation with next file? [y/n]') == 'y':
                pass
            else:
                raise KeyboardInterrupt

    def ble_get(self, args, src_name, sz, dst_name):
        if not args.fg:
            try:
                self.fileio.get((sz, src_name), dst_name,
                                fullpath=True, psize=False)
            except (KeyboardInterrupt, Exception):
                print(
                    'KeyboardInterrupt: get Operation Canceled')
                # flush ws and reset
                self.dev.cmd("f.close()", silent=True)
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    raise KeyboardInterrupt
        else:
            try:  # FAST GET
                self.fastfileio.init_get(dst_name, sz)
                cmd_gf = (f"cat('{src_name}');"
                          f"gc.collect()")
                self.dev.wr_cmd(cmd_gf,
                                follow=True,
                                long_string=True,
                                multiline=True,
                                silent=True,
                                pipe=self.fastfileio.get)
                self.fastfileio.save_file()
                print('\n')
            except (KeyboardInterrupt, Exception) as e:
                print(e)
                print(
                    'KeyboardInterrupt: get Operation Canceled')
                if input('Continue get Operation with next file? [y/n]') == 'y':
                    pass
                else:
                    print('Canceling file queue..')
                    return

    def file_put(self, src_name, size, dst_name):
        if self.dev.dev_class == 'SerialDevice':
            self.sr_put(src_name, size, dst_name)
        elif self.dev.dev_class == 'WebSocketDevice':
            self.ws_put(src_name, size, dst_name)
        elif self.dev.dev_class == 'BleDevice':
            self.ble_put(src_name, size, dst_name)

    def file_get(self, args, src_name, size, dst_name):
        if self.dev.dev_class == 'SerialDevice':
            self.sr_get(args, src_name, size, dst_name)
        elif self.dev.dev_class == 'WebSocketDevice':
            self.ws_get(args, src_name, size, dst_name)
        elif self.dev.dev_class == 'BleDevice':
            self.ble_get(args, src_name, size, dst_name)

    def fileop(self, cmd, args, rest_args):
        if cmd == 'put':
            # fileio.put_files(_file_to_edit, dest_file, ppath=True)
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
                    print_size(name, sz)

                for sz, file in file_match:
                    src_file = file
                    if source != '/':
                        if source.startswith('.'):
                            source = source.replace('.', '')
                        dst_file = source + '/' + file.split('/')[-1]
                    else:
                        dst_file = './' + file.split('/')[-1]
                    if dst_file[-1] == "/":
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += basename
                    print(f"{src_file} -> {self.dev_name}:{dst_file}\n")
                    print_size(src_file, sz, nl=True)
                    self.file_put(src_file, sz, dst_file)

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
            print('get: searching files...')
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
                    print_size(name, sz)

                for size_file_to_get, file in file_match:
                    src_file = file
                    dst_file = '.'
                    if os.path.isdir(dst_file):
                        basename = src_file.rsplit("/", 1)[-1]
                        dst_file += "/" + basename
                    abs_src_file = src_file
                    if not src_file.startswith('/'):
                        abs_src_file = f'/{src_file}'
                    print(f"{self.dev_name}:{abs_src_file} -> {dst_file}\n")
                    print_size(src_file, size_file_to_get, nl=True)
                    self.file_get(args, src_file, size_file_to_get, dst_file)

            else:
                if args.dir:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/{args.dir} ')
                else:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/ ')
            return

    def fsync(self, args, rest_args):
        if not args.d:
            # HOST TO DEVICE
            if rest_args == ['.'] or rest_args == ['*']:  # CWD
                rest_args = ['*']
                top_dir = '.'

            else:
                # top_dir = rest_args[0]
                # rest_args[0] = f"./{top_dir}"
                rest_args = [f"./{top_dir}" if not top_dir.startswith('./')
                             else top_dir for top_dir in rest_args]
                top_dir = rest_args

            if args.n:
                self.stash.update(path=top_dir)
                self.stash.update(ignore=args.i)
                self.stash.update(rf=args.rf)
                self.stash.update(d=args.d)

            if args.t:
                if isinstance(top_dir, list):
                    for dir in top_dir:
                        try:
                            tree(dir)
                        except Exception:
                            pass
                else:
                    tree(top_dir)
            else:
                path_sync = top_dir
                if top_dir == '.':
                    path_sync = ''
                if isinstance(path_sync, list):
                    print(f"dsync: syncing path {', '.join(path_sync)}:")
                else:
                    print(f"dsync: syncing path ./{path_sync}:")

            # LOCAL DIRS AND FILES
            local_hashlist = shasum(*rest_args, all=True, size=True, recursive=True,
                                    rtn=True, debug=False)
            # SEPARATE
            if local_hashlist:

                dir_match = [dir for dir, sz, id in local_hashlist if id == 'dir']
                file_match = [fh for fh in local_hashlist if fh[-1] != 'dir']
                if not dir_match:
                    print('dsync: dirs: none')
                if not file_match:
                    print('dsync: files: none')

                # DEVICE DIRS AND FILES
                if not args.f:
                    isdir = True

                    dev_hash_cmd = (f"from shasum import shasum;"
                                    f"shasum(*{rest_args}, debug=True, "
                                    f"rtn=False, size=True, recursive=True, all=True)"
                                    ";gc.collect()")
                    if isdir:
                        print('dsync: checking filesystem...')
                        ff = self.fastfileio
                        ff.init_sha()
                        dev_hashlist = self.dev.wr_cmd(dev_hash_cmd, follow=True,
                                                       rtn_resp=True,
                                                       long_string=True,
                                                       pipe=ff.shapipe)
                        dev_hashlist = ff._shafiles
                        # SEPARATE
                        if dev_hashlist:
                            ff.end_sha()
                            print('', end='\r')
                        dev_dir_match = [dir for dir, sz, id in dev_hashlist
                                         if id == 'dir']
                        dev_file_match = [fh for fh in dev_hashlist
                                          if fh[-1] != 'dir']

                    else:
                        dev_dir_match = []
                        dev_file_match = []
                else:
                    dev_dir_match = []
                    dev_file_match = []

            else:
                print('dsync: dirs: none')
                print('dsync: files: none')
                return
            # OPERATE
            # DEVICE DIRS
            if args.n:
                self.stash.update(dirs=dir_match, files=file_match,
                                  dev_dirs=dev_dir_match, dev_files=dev_file_match)

            dirs_to_make = [ldir for ldir in dir_match
                            if ldir not in dev_dir_match]
            local_dirs = dir_match
            # print(dir_match)
            # print(dev_dir_match)
            if args.i:
                dirs_to_make = self.re_filt(args.i, dirs_to_make)
            if dirs_to_make:
                print(f'dsync: making new dirs ({len(dirs_to_make)}):')
                for ndir in dirs_to_make:
                    print(f'- {ndir}')
                if not args.n:
                    self.dev.wr_cmd(f'mkdir(*{dirs_to_make})', follow=True)
            else:
                if not args.rf:
                    if len(local_dirs) > 1:
                        print(f'dsync: dirs: OK{CHECK}')
                    else:
                        print('dsync: dirs: none')
                # print('dsync: no new directories to make')
            dirs_to_delete = []
            if args.rf:
                dirs_to_delete = [ddir for ddir in dev_dir_match
                                  if ddir not in dir_match]
                # filter and get only root dirs to avoid trying
                # to delete dirs that were already deleted
                dirs_to_delete = [dir for dir in dirs_to_delete
                                  if dir.rsplit('/', 1)[0] not in dirs_to_delete]
                if args.i:
                    dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                if dirs_to_delete:
                    print(f'dsync: deleting old dirs ({len(dirs_to_delete)}):')
                    for ndir in dirs_to_delete:
                        print(f'- {ndir}')
                    if not args.n:
                        self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                        self.dev.wr_cmd(f'rmrf(*{dirs_to_delete})',
                                        follow=True)
                else:
                    if len(local_dirs) > 1:
                        print(f'dsync: dirs: OK{CHECK}')
                    else:
                        print(f'dsync: dirs: none')

            # FILES

            dev_files = dev_file_match
            local_files = file_match
            _new_files = []
            _modified_files = []
            files_to_delete = []
            if dev_files:
                files_to_sync = [(fh[1], fh[0])
                                 for fh in local_files if fh not in
                                 dev_files]
            else:
                files_to_sync = [(fh[1], fh[0])
                                 for fh in local_files]
            if args.i:
                _file_match = self.re_filt(args.i,
                                           [nm for sz, nm in files_to_sync])
                files_to_sync = [(sz, nm)
                                 for sz, nm in files_to_sync
                                 if nm in _file_match]

            # print(local_files)
            # print(dev_files)

            if files_to_sync:
                _new_files = [(sz, name) for sz, name
                              in files_to_sync if name not in
                              [dname for dname, sz, fh in dev_files]]
                _modified_files = [(sz, name) for sz, name
                                   in files_to_sync if name in
                                   [dname for dname, sz, fh in dev_files]]
                if _new_files:
                    print(f'dsync: syncing new files ({len(_new_files)}):')
                    for sz, name in _new_files:
                        print_size(name, sz)
                if _modified_files:
                    print(f'dsync: syncing modified files ({len(_modified_files)}):')
                    for sz, name in _modified_files:
                        print_size(name, sz)
                        if args.p:
                            self.shell.sh_cmd(f"diff {name}")
                print('')
                for sz, name in files_to_sync:
                    print(f"{name} -> {self.dev_name}:{name}")
                    print_size(name, sz, nl=True)
                    # ### DEVICE SPECIFIC ####
                    if not args.n:
                        self.file_put(name, sz, name)
            else:
                if not args.rf:
                    print(f'dsync: files: OK{CHECK}')

            if args.rf:
                _local_files = [lf[0] for lf in local_files]
                files_to_delete = [dfile[0] for dfile in dev_files
                                   if dfile[0] not in _local_files]
                # filter and get only files to avoid trying
                # to delete files whose parent tree was already deleted
                files_to_delete = [file for file in files_to_delete
                                   if file.rsplit('/', 1)[0] not in dirs_to_delete]
                if args.i:
                    files_to_delete = self.re_filt(args.i, files_to_delete)
                if files_to_delete:
                    print(f'dsync: deleting old files ({len(files_to_delete)}):')
                    for ndir in files_to_delete:
                        print(f'- {ndir}')
                    if not args.n:
                        self.dev.wr_cmd(
                            'from upysh2 import rmrf', silent=True)
                        self.dev.wr_cmd(f'rmrf(*{files_to_delete})',
                                        follow=True)
                else:
                    print(f'dsync: files: OK{CHECK}')
                #     print('dsync: no old files to delete')

            # SUM UP
            if dirs_to_make or dirs_to_delete:
                print(f"{fname(len(dirs_to_make),'new dir')}, "
                      f"{fname(len(dirs_to_delete), 'dir')}"
                      f" deleted")
            if _new_files or _modified_files or files_to_delete:
                print(f"{fname(len(_new_files), 'new file')}, "
                      f"{fname(len(_modified_files), 'file')} "
                      f"changed, {fname(len(files_to_delete), 'file')} deleted")

        else:
            # DEVICE TO HOST
            if rest_args == ['.'] or rest_args == ['*']:  # CWD
                rest_args = ['*']
                top_dir = '.'

            else:
                # top_dir = rest_args[0]
                # rest_args[0] = f"./{top_dir}"
                rest_args = [f"./{top_dir}" if not top_dir.startswith('./')
                             else top_dir for top_dir in rest_args]
                top_dir = rest_args

            if args.n:
                self.stash.update(path=top_dir)
                self.stash.update(ignore=args.i)
                self.stash.update(rf=args.rf)
                self.stash.update(d=args.d)

            if args.t:
                if isinstance(top_dir, list):
                    for dir in top_dir:
                        try:
                            self.dev.wr_cmd(f"from upysh2 import tree;"
                                            f"tree('{dir}')", follow=True)
                        except Exception:
                            pass
                else:

                    self.dev.wr_cmd(f"from upysh2 import tree;tree('{top_dir}')",
                                    follow=True)

            else:
                path_sync = top_dir
                if top_dir == '.':
                    path_sync = ''
                if isinstance(path_sync, list):
                    print(f"dsync: path {', '.join(path_sync)}:")
                else:
                    print(f"dsync: path ./{path_sync}:")

            # LOCAL DIRS AND FILES
            if rest_args != ['*']:
                try:
                    # os.stat(rest_args[0])
                    local_hashlist = shasum(*rest_args, all=True, size=True,
                                            recursive=True,
                                            rtn=True, debug=False)
                except Exception:
                    local_hashlist = []

            else:
                local_hashlist = shasum(rest_args[0], all=True, size=True,
                                        recursive=True,
                                        rtn=True, debug=False)
            # SEPARATE
            if local_hashlist:

                dir_match = [dir for dir, sz, id in local_hashlist if id == 'dir']
                file_match = [fh for fh in local_hashlist if fh[-1] != 'dir']

            else:
                dir_match = []
                file_match = []

            dev_hash_cmd = (f"from shasum import shasum;"
                            f"shasum(*{rest_args}, debug=True, "
                            f"rtn=False, size=True, recursive=True, all=True)"
                            ";gc.collect()")
            print('dsync: checking filesystem...')
            ff = self.fastfileio
            ff.init_sha()
            dev_hashlist = self.dev.wr_cmd(dev_hash_cmd, follow=True,
                                           rtn_resp=True,
                                           long_string=True,
                                           pipe=ff.shapipe)
            dev_hashlist = ff._shafiles
            # SEPARATE
            if dev_hashlist:
                ff.end_sha()
                print('', end='\r')
                dev_dir_match = [dir for dir, sz, id in dev_hashlist
                                 if id == 'dir']
                dev_file_match = [fh for fh in dev_hashlist
                                  if fh[-1] != 'dir']

                if not dev_dir_match:
                    ff.get_pb()
                    sys.stdout.write("\033[K")
                    sys.stdout.write("\033[A")
                    print('dsync: dirs: none' + ' ' * (ff.columns - 20))
                if not dev_file_match:
                    ff.get_pb()
                    sys.stdout.write("\033[K")
                    sys.stdout.write("\033[A")
                    print('dsync: files: none' + ' ' * (ff.columns - 20))

            else:
                print('dsync: dirs: none')
                print('dsync: files: none')
                return

            if args.n:
                self.stash.update(dirs=dir_match, files=file_match,
                                  dev_dirs=dev_dir_match, dev_files=dev_file_match)

            dirs_to_delete = []
            dirs_to_make = []
            if dev_dir_match:
                dirs_to_make = [
                    ddir for ddir in dev_dir_match if ddir not in dir_match]
                if args.i:
                    dirs_to_make = self.re_filt(args.i, dirs_to_make)
                if dirs_to_make:
                    print(f'dsync: making new dirs ({len(dirs_to_make)}):')
                    for ndir in dirs_to_make:
                        print(f'- {ndir}')
                        if not args.n:
                            os.makedirs(ndir)
                else:
                    if not args.rf:
                        if len(dev_dir_match) > 1:
                            print(f'dsync: dirs: OK{CHECK}')
                        else:
                            print('dsync: dirs: none')
                if args.rf:
                    # print(local_dirs, dev_dirs)
                    dirs_to_delete = [ldir for ldir in dir_match
                                      if ldir not in dev_dir_match]
                    dirs_to_delete = [dir for dir in dirs_to_delete
                                      if dir.rsplit('/', 1)[0] not in dirs_to_delete]
                    if args.i:
                        dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                    if dirs_to_delete:
                        print(f'dsync: deleting old dirs ({len(dirs_to_delete)}):')
                        for ndir in dirs_to_delete:
                            print(f'- {ndir}')
                            if not args.n:
                                shutil.rmtree(ndir)
                    else:
                        if len(dev_dir_match) > 1:
                            print(f'dsync: dirs: OK{CHECK}')
                        else:
                            print('dsync: dirs: none')

            dev_files = dev_file_match
            local_files = file_match
            _new_files = []
            _modified_files = []
            files_to_delete = []
            if dev_files:

                if local_files:
                    files_to_sync = [(fts[1], fts[0])
                                     for fts in dev_files if fts not in
                                     local_files]
                else:
                    files_to_sync = [(fts[1], fts[0])
                                     for fts in dev_files]

                if args.i:
                    _file_match = self.re_filt(args.i,
                                               [nm for sz, nm in files_to_sync])
                    files_to_sync = [(sz, nm)
                                     for sz, nm in files_to_sync
                                     if nm in _file_match]

                if files_to_sync:
                    local_files_dict = {fts[0]: fts[1] for fts in local_files}
                    _new_files = [(sz, name) for sz, name
                                  in files_to_sync if name not in
                                  local_files_dict.keys()]
                    _modified_files = [(sz, name) for sz, name
                                       in files_to_sync if name in
                                       local_files_dict.keys()]
                    if _new_files:
                        print(f'\ndsync: syncing new files ({len(_new_files)}):')
                        for sz, name in _new_files:
                            print_size(name, sz)
                    if _modified_files:
                        print(f'\ndsync: syncing modified files '
                              f'({len(_modified_files)}):')
                        for sz, name in _modified_files:
                            print_size(name, sz)
                            if args.p:
                                self.shell.sh_cmd(f"diff {name} -s")
                    print('')
                    for sz, name in files_to_sync:
                        print(f"{self.dev_name}:{name} -> {name}")
                        print_size(name, sz, nl=True)
                        if not args.n:
                            self.file_get(args, name, sz, name)
                else:
                    if not args.rf:
                        print(f'dsync: files: OK{CHECK}')
                    # print('dsync: no new or modified files to sync')

                if args.rf:
                    _dev_files = [df[0] for df in dev_files]
                    files_to_delete = [dfile[0] for dfile in local_files
                                       if dfile[0] not in _dev_files]
                    # filter and get only files to avoid trying
                    # to delete files whose parent tree was already deleted
                    files_to_delete = [file for file in files_to_delete
                                       if file.rsplit('/', 1)[0] not in dirs_to_delete]
                    if args.i:
                        files_to_delete = self.re_filt(args.i, files_to_delete)
                    if files_to_delete:
                        print(f'dsync: deleting old files ({len(files_to_delete)}):')
                        for ndir in files_to_delete:
                            print(f'- {ndir}')
                            if not args.n:
                                os.remove(ndir)
                    else:
                        print(f'dsync: files: OK{CHECK}')
                    #     print('dsync: no old files to delete')

            # SUM UP
            if dirs_to_make or dirs_to_delete:
                print(f"{fname(len(dirs_to_make),'new dir')}, "
                      f"{fname(len(dirs_to_delete), 'dir')}"
                      f" deleted")
            if _new_files or _modified_files or files_to_delete:
                print(f"{fname(len(_new_files), 'new file')}, "
                      f"{fname(len(_modified_files), 'file')} "
                      f"changed, {fname(len(files_to_delete), 'file')} deleted")
            return

    def show_stash(self):
        id_bytes = hashlib.sha1(repr(self.stash).encode()).digest()
        id = binascii.hexlify(id_bytes).decode()
        return id

    def apply_stash(self, args, rest_args):
        dir_match = self.stash.get('dirs')
        file_match = self.stash.get('files')
        dev_dir_match = self.stash.get('dev_dirs')
        dev_file_match = self.stash.get('dev_files')
        top_dir = self.stash.get('path')
        args.i = self.stash.get('ignore')
        args.rf = self.stash.get('rf')
        args.d = self.stash.get('d')
        path_sync = top_dir
        if top_dir == '.':
            path_sync = ''
        if isinstance(path_sync, list):
            print(f"dsync: syncing path {', '.join(path_sync)}:")
        else:
            print(f"dsync: syncing path ./{path_sync}:")
        # HOST TO DEVICE

        if not args.d:
            dirs_to_make = [ldir for ldir in dir_match
                            if ldir not in dev_dir_match]
            local_dirs = dir_match
            # print(dir_match)
            # print(dev_dir_match)
            if args.i:
                dirs_to_make = self.re_filt(args.i, dirs_to_make)
            if dirs_to_make:
                print(f'dsync: making new dirs ({len(dirs_to_make)}):')
                for ndir in dirs_to_make:
                    print(f'- {ndir}')
                if not args.n:
                    self.dev.wr_cmd(f'mkdir(*{dirs_to_make})', follow=True)
            else:
                if not args.rf:
                    if len(local_dirs) > 1:
                        print(f'dsync: dirs: OK{CHECK}')
                    else:
                        print('dsync: dirs: none')
                # print('dsync: no new directories to make')
            dirs_to_delete = []
            files_to_delete = []
            if args.rf:
                dirs_to_delete = [ddir for ddir in dev_dir_match
                                  if ddir not in dir_match]
                # filter and get only root dirs to avoid trying
                # to delete dirs that were already deleted
                dirs_to_delete = [dir for dir in dirs_to_delete
                                  if dir.rsplit('/', 1)[0] not in dirs_to_delete]
                if args.i:
                    dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                if dirs_to_delete:
                    print(f'dsync: deleting old dirs ({len(dirs_to_delete)}):')
                    for ndir in dirs_to_delete:
                        print(f'- {ndir}')
                    if not args.n:
                        self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                        self.dev.wr_cmd(f'rmrf(*{dirs_to_delete})',
                                        follow=True)
                else:
                    if len(local_dirs) > 1:
                        print(f'dsync: dirs: OK{CHECK}')
                    else:
                        print('dsync: dirs: none')

            # FILES

            dev_files = dev_file_match
            local_files = file_match
            _new_files = []
            _modified_files = []
            files_to_delete = []
            if dev_files:
                files_to_sync = [(fh[1], fh[0])
                                 for fh in local_files if fh not in
                                 dev_files]
            else:
                files_to_sync = [(fh[1], fh[0])
                                 for fh in local_files]
            if args.i:
                _file_match = self.re_filt(args.i,
                                           [nm for sz, nm in files_to_sync])
                files_to_sync = [(sz, nm)
                                 for sz, nm in files_to_sync
                                 if nm in _file_match]

            # print(local_files)
            # print(dev_files)

            if files_to_sync:
                _new_files = [(sz, name) for sz, name
                              in files_to_sync if name not in
                              [dname for dname, sz, fh in dev_files]]
                _modified_files = [(sz, name) for sz, name
                                   in files_to_sync if name in
                                   [dname for dname, sz, fh in dev_files]]
                if _new_files:
                    print(f'dsync: syncing new files ({len(_new_files)}):')
                    for sz, name in _new_files:
                        print_size(name, sz)
                if _modified_files:
                    print(f'dsync: syncing modified files ({len(_modified_files)}):')
                    for sz, name in _modified_files:
                        print_size(name, sz)
                        if args.p:
                            self.shell.sh_cmd(f"diff {name}")
                print('')
                for sz, name in files_to_sync:
                    print(f"{name} -> {self.dev_name}:{name}")
                    print_size(name, sz, nl=True)
                    # ### DEVICE SPECIFIC ####
                    if not args.n:
                        self.file_put(name, sz, name)
            else:
                if not args.rf:
                    print(f'dsync: files: OK{CHECK}')

            if args.rf:
                _local_files = [lf[0] for lf in local_files]
                files_to_delete = [dfile[0] for dfile in dev_files
                                   if dfile[0] not in _local_files]
                # filter and get only files to avoid trying
                # to delete files whose parent tree was already deleted
                files_to_delete = [file for file in files_to_delete
                                   if file.rsplit('/', 1)[0] not in dirs_to_delete]
                if args.i:
                    files_to_delete = self.re_filt(args.i, files_to_delete)
                if files_to_delete:
                    print(f'dsync: deleting old files ({len(files_to_delete)}):')
                    for ndir in files_to_delete:
                        print(f'- {ndir}')
                    if not args.n:
                        self.dev.wr_cmd(
                            'from upysh2 import rmrf', silent=True)
                        self.dev.wr_cmd(f'rmrf(*{files_to_delete})',
                                        follow=True)
                else:
                    print(f'dsync: files: OK{CHECK}')

            # SUM UP
            if dirs_to_make or dirs_to_delete:
                print(f"{fname(len(dirs_to_make),'new dir')}, "
                      f"{fname(len(dirs_to_delete), 'dir')}"
                      f" deleted")
            if _new_files or _modified_files or files_to_delete:
                print(f"{fname(len(_new_files), 'new file')}, "
                      f"{fname(len(_modified_files), 'file')} "
                      f"changed, {fname(len(files_to_delete), 'file')} deleted")

        else:
            # DEVICE TO HOST
            dirs_to_delete = []
            dirs_to_make = []
            if dev_dir_match:
                dirs_to_make = [
                    ddir for ddir in dev_dir_match if ddir not in dir_match]
                if args.i:
                    dirs_to_make = self.re_filt(args.i, dirs_to_make)
                if dirs_to_make:
                    print(f'dsync: making new dirs ({len(dirs_to_make)}):')
                    for ndir in dirs_to_make:
                        print(f'- {ndir}')
                        if not args.n:
                            os.makedirs(ndir)
                else:
                    if not args.rf:
                        if len(dev_dir_match) > 1:
                            print(f'dsync: dirs: OK{CHECK}')
                        else:
                            print('dsync: dirs: none')
                if args.rf:
                    # print(local_dirs, dev_dirs)
                    dirs_to_delete = [ldir for ldir in dir_match
                                      if ldir not in dev_dir_match]
                    dirs_to_delete = [dir for dir in dirs_to_delete
                                      if dir.rsplit('/', 1)[0] not in dirs_to_delete]
                    if args.i:
                        dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                    if dirs_to_delete:
                        print(f'dsync: deleting old dirs ({len(dirs_to_delete)}):')
                        for ndir in dirs_to_delete:
                            print(f'- {ndir}')
                            if not args.n:
                                shutil.rmtree(ndir)
                    else:
                        if len(dev_dir_match) > 1:
                            print(f'dsync: dirs: OK{CHECK}')
                        else:
                            print('dsync: dirs: none')

            dev_files = dev_file_match
            local_files = file_match
            _new_files = []
            _modified_files = []
            files_to_delete = []
            if dev_files:

                if local_files:
                    files_to_sync = [(fts[1], fts[0])
                                     for fts in dev_files if fts not in
                                     local_files]
                else:
                    files_to_sync = [(fts[1], fts[0])
                                     for fts in dev_files]

                if args.i:
                    _file_match = self.re_filt(args.i,
                                               [nm for sz, nm in files_to_sync])
                    files_to_sync = [(sz, nm)
                                     for sz, nm in files_to_sync
                                     if nm in _file_match]

                if files_to_sync:
                    local_files_dict = {fts[0]: fts[1] for fts in local_files}
                    _new_files = [(sz, name) for sz, name
                                  in files_to_sync if name not in
                                  local_files_dict.keys()]
                    _modified_files = [(sz, name) for sz, name
                                       in files_to_sync if name in
                                       local_files_dict.keys()]
                    if _new_files:
                        print(f'\ndsync: syncing new files ({len(_new_files)}):')
                        for sz, name in _new_files:
                            print_size(name, sz)
                    if _modified_files:
                        print(f'\ndsync: syncing modified files '
                              f'({len(_modified_files)}):')
                        for sz, name in _modified_files:
                            print_size(name, sz)
                            if args.p:
                                self.shell.sh_cmd(f"diff {name} -s")
                    print('')
                    for sz, name in files_to_sync:
                        print(f"{self.dev_name}:{name} -> {name}")
                        print_size(name, sz, nl=True)
                        if not args.n:
                            self.file_get(args, name, sz, name)
                else:
                    if not args.rf:
                        print(f'dsync: files: OK{CHECK}')
                    # print('dsync: no new or modified files to sync')

                if args.rf:
                    _dev_files = [df[0] for df in dev_files]
                    files_to_delete = [dfile[0] for dfile in local_files
                                       if dfile[0] not in _dev_files]
                    # filter and get only files to avoid trying
                    # to delete files whose parent tree was already deleted
                    files_to_delete = [file for file in files_to_delete
                                       if file.rsplit('/', 1)[0] not in dirs_to_delete]
                    if args.i:
                        files_to_delete = self.re_filt(args.i, files_to_delete)
                    if files_to_delete:
                        print(f'dsync: deleting old files ({len(files_to_delete)}):')
                        for ndir in files_to_delete:
                            print(f'- {ndir}')
                            if not args.n:
                                os.remove(ndir)
                    else:
                        print(f'dsync: files: OK{CHECK}')

            # SUM UP
            if dirs_to_make or dirs_to_delete:
                print(f"{fname(len(dirs_to_make),'new dir')}, "
                      f"{fname(len(dirs_to_delete), 'dir')}"
                      f" deleted")
            if _new_files or _modified_files or files_to_delete:
                print(f"{fname(len(_new_files), 'new file')}, "
                      f"{fname(len(_modified_files), 'file')} "
                      f"changed, {fname(len(files_to_delete), 'file')} deleted")
