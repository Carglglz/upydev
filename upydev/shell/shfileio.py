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


class ShDsyncIO:
    def __init__(self, dev, dev_name, fileio, fastfileio, shell=None):
        self.dev = dev
        self.dev_name = dev_name
        self.fileio = fileio
        self.fastfileio = fastfileio
        self.shell = shell

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

    def ble_put(self, name, sz):
        pass

    def ble_get(self, args, name, sz):
        pass

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
                    # try:
                    #     # self.fileio.put(src_file, dst_file)
                    #     self.fastfileio.init_put(src_file, sz)
                    #     self.fastfileio.sraw_put_file(src_file, dst_file)
                    # except (KeyboardInterrupt, Exception):
                    #     print('KeyboardInterrupt: put Operation Canceled')
                    #     self.dev.cmd("f.close()", silent=True)
                    #     if input('Continue put Operation with next file? [y/n]') == 'y':
                    #         pass
                    #     else:
                    #         raise KeyboardInterrupt

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
                    # if not args.fg:
                    #     try:
                    #         self.fileio.get((size_file_to_get, src_file), dst_file)
                    #     except (KeyboardInterrupt, Exception):
                    #         print('KeyboardInterrupt: get Operation Canceled')
                    #         # flush ws and reset
                    #         self.dev.cmd("f.close()", silent=True)
                    #         if input('Continue get Operation with next file? [y/n]') == 'y':
                    #             pass
                    #         else:
                    #             print('Canceling file queue..')
                    #             raise KeyboardInterrupt
                    # else:
                    #     try:  # FAST GET
                    #         self.fastfileio.init_get(src_file, size_file_to_get)
                    #         cmd_get_file = (f"rcat('{src_file}', buff={args.b});"
                    #                         f"gc.collect()")
                    #         if size_file_to_get > 0:
                    #             self.fastfileio.sr_get_file(cmd_get_file)
                    #             self.fastfileio.save_file()
                    #         else:
                    #             self.fastfileio.do_pg_bar(self.fastfileio.bar_size,
                    #                                       self.fastfileio.wheel,
                    #                                       f"{0:.2f}/{0:.2f} KB",
                    #                                       "0", 0, 0, 1, 0)
                    #         print('\n')
                    #     except (KeyboardInterrupt, Exception) as e:
                    #         print(e)
                    #         print('KeyboardInterrupt: get Operation Canceled')
                    #         if input('Continue get Operation with next file? [y/n]') == 'y':
                    #             pass
                    #         else:
                    #             print('Canceling file queue..')
                    #             return
            else:
                if args.dir:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/{args.dir} ')
                else:
                    print(f'get: {", ".join(rest_args)}: No matching files found in '
                          f'{self.dev_name}:/ ')
            return

    def dsync(self, args, rest_args):
        if not args.d:
            # HOST TO DEVICE
            if rest_args == ['.'] or rest_args == ['*']:  # CWD
                rest_args = ['*']
                if args.t:
                    tree()
                else:
                    print("dsync: syncing path ./:")
                file_match = nglob(*rest_args, size=True)
                if file_match:
                    local_files = shasum(*rest_args, debug=False, rtn=True)
                    local_files_dict = {
                        fname: fhash for fname, fhash in local_files}
                    if local_files:
                        if not args.f:
                            dev_cmd_files = (f"from shasum import shasum;"
                                             f"shasum(*{rest_args}, debug=True, "
                                             f"rtn=False, size=True);gc.collect()")
                            print('dsync: checking files...')
                            ff = self.fastfileio
                            ff.init_sha()
                            dev_files = self.dev.wr_cmd(dev_cmd_files, follow=True,
                                                        rtn_resp=True,
                                                        long_string=True,
                                                        pipe=ff.shapipe)
                            # print(local_files[0])
                            if not dev_files:
                                dev_files = [(hf[0], hf[2])
                                             for hf in ff._shafiles]
                                if dev_files:
                                    ff.end_sha()
                        else:
                            dev_files = []

                        if dev_files:
                            files_to_sync = [(os.stat(fts[0])[6], fts[0])
                                             for fts in local_files if fts not in
                                             dev_files]
                        else:
                            files_to_sync = [(os.stat(fts)[6], fts)
                                             for fts in local_files_dict.keys()]
                        if args.i:
                            _file_match = self.re_filt(args.i,
                                                       [nm for sz, nm in files_to_sync])
                            files_to_sync = [(sz ,nm)
                                             for sz, nm in files_to_sync
                                             if nm in _file_match]

                        if files_to_sync:
                            print('\ndsync: syncing new or modified files:')
                            for sz, name in files_to_sync:
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
                            print(f'dsync: ./ : OK{CHECK}')

                        if args.rf:
                            _local_files = [lf[0] for lf in local_files]
                            files_to_delete = [dfile[0] for dfile in dev_files
                                               if dfile[0] not in _local_files]
                            if args.i:
                                files_to_delete = self.re_filt(args.i, files_to_delete)
                            if files_to_delete:
                                print('dsync: deleting old files:')
                                for ndir in files_to_delete:
                                    print(f'- {ndir}')
                                if not args.n:
                                    self.dev.wr_cmd(
                                        'from upysh2 import rmrf', silent=True)
                                    self.dev.wr_cmd(f'rmrf(*{files_to_delete})',
                                                    follow=True)
                            else:
                                print('dsync: no old files to delete')

                    else:
                        print('dsync: no files found directory tree')
            # LOCAL DIRS
            dir_match = nglob(*rest_args, dir_only=True)
            if dir_match:
                if args.i:
                    dir_match = self.re_filt(args.i, dir_match)
                for dir in dir_match:
                    if args.t:
                        tree(dir)
                    else:
                        print(f"dsync: syncing path {dir}:")
                    depth_level = _get_path_depth(dir) + 1
                    pattern_dir = [f"{dir}/*{'/*'* i}" for i in range(depth_level)]
                    pattern_dir = [dir] + pattern_dir
                    local_dirs = nglob(*pattern_dir, dir_only=True)
                    if not args.f:
                        dev_dirs = self.dev.wr_cmd(f"from nanoglob import glob;"
                                                   f"glob(*{pattern_dir}, "
                                                   f"dir_only=True);gc.collect()",
                                                   silent=True, rtn_resp=True)
                    else:
                        dev_dirs = []
                    dirs_to_make = [ldir for ldir in local_dirs
                                    if ldir not in dev_dirs]
                    if args.i:
                        dirs_to_make = self.re_filt(args.i, dirs_to_make)
                    if dirs_to_make:
                        print('dsync: making new dirs:')
                        for ndir in dirs_to_make:
                            print(f'- {ndir}')
                        if not args.n:
                            self.dev.wr_cmd(f'mkdir(*{dirs_to_make})', follow=True)
                    else:
                        print(f'dsync: dirs: OK{CHECK}')
                        # print('dsync: no new directories to make')

                    if args.rf:
                        dirs_to_delete = [ddir for ddir in dev_dirs
                                          if ddir not in local_dirs]
                        if args.i:
                            dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                        if dirs_to_delete:
                            print('dsync: deleting old dirs:')
                            for ndir in dirs_to_delete:
                                print(f'- {ndir}')
                            if not args.n:
                                self.dev.wr_cmd('from upysh2 import rmrf', silent=True)
                                self.dev.wr_cmd(f'rmrf(*{dirs_to_delete})',
                                                follow=True)
                        else:
                            print('dsync: no old directories to delete')

                    local_files = shasum(*pattern_dir, debug=False, rtn=True)
                    local_files_dict = {
                        fname: fhash for fname, fhash in local_files}
                    if local_files:
                        if not args.f:
                            dev_cmd_files = (f"from shasum import shasum;"
                                             f"shasum(*{pattern_dir}, debug=True, "
                                             f"rtn=False, size=True);gc.collect()")
                            print('dsync: checking files...')
                            ff = self.fastfileio
                            ff.init_sha()
                            dev_files = self.dev.wr_cmd(dev_cmd_files, follow=True,
                                                        rtn_resp=True,
                                                        long_string=True,
                                                        pipe=ff.shapipe)
                            # print(local_files[0])
                            if not dev_files:
                                dev_files = [(hf[0], hf[2])
                                             for hf in ff._shafiles]
                                if dev_files:
                                    ff.end_sha()
                        else:
                            dev_files = []
                        if dev_files:
                            files_to_sync = [(os.stat(fts[0])[6], fts[0])
                                             for fts in local_files if fts not in
                                             dev_files]
                        else:
                            files_to_sync = [(os.stat(fts)[6], fts)
                                             for fts in local_files_dict.keys()]
                        # print(local_files)
                        # print(dev_files)
                        # print(files_to_sync)
                        if args.i:
                            _file_match = self.re_filt(args.i,
                                                       [nm for sz, nm in files_to_sync])
                            files_to_sync = [(sz ,nm)
                                             for sz, nm in files_to_sync
                                             if nm in _file_match]
                        if files_to_sync:
                            print('\ndsync: syncing new or modified files:')
                            for sz, name in files_to_sync:
                                print_size(name, sz)
                                if args.p:
                                    self.shell.sh_cmd(f"diff {name}")
                            print('')
                            for sz, name in files_to_sync:
                                print(f"{name} -> {self.dev_name}:{name}")
                                print_size(name, sz, nl=True)
                                if not args.n:
                                    self.file_put(name, sz, name)
                        else:
                            print(f'dsync: files: OK{CHECK}')
                            # print('dsync: no new or modified files to sync')

                        if args.rf:
                            _local_files = [lf[0] for lf in local_files]
                            files_to_delete = [dfile[0] for dfile in dev_files
                                               if dfile[0] not in _local_files]
                            if args.i:
                                files_to_delete = self.re_filt(args.i, files_to_delete)
                            if files_to_delete:
                                print('dsync: deleting old files:')
                                for ndir in files_to_delete:
                                    print(f'- {ndir}')
                                if not args.n:
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
            if rest_args == ['.'] or rest_args == ['*']:  # CWD
                rest_args = ['*']
                if args.t:
                    self.dev.wr_cmd("from upysh2 import tree;tree", follow=True)
                else:
                    print("dsync: syncing path ./:")
                dev_cmd_files = (f"from shasum import shasum;"
                                 f"shasum(*{rest_args}, debug=True, "
                                 f"rtn=False, size=True);gc.collect()")
                print('dsync: checking files...')
                self.fastfileio.init_sha()
                dev_files = self.dev.wr_cmd(dev_cmd_files, follow=True,
                                            rtn_resp=True, long_string=True,
                                            pipe=self.fastfileio.shapipe)
                if not dev_files:
                    dev_files = self.fastfileio._shafiles
                    if dev_files:
                        self.fastfileio.end_sha()


                if dev_files:
                    local_files = shasum(*rest_args, debug=False, rtn=True,
                                         size=True)

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
                        files_to_sync = [(sz ,nm)
                                         for sz, nm in files_to_sync
                                         if nm in _file_match]

                    if files_to_sync:
                        print('\ndsync: syncing new or modified files:')
                        for sz, name in files_to_sync:
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
                        print(f'dsync: ./ : OK{CHECK}')
                        # print('dsync: no new or modified files to sync')

                    if args.rf:
                        _dev_files = [df[0] for df in dev_files]
                        files_to_delete = [dfile[0] for dfile in local_files
                                           if dfile[0] not in _dev_files]
                        if args.i:
                            files_to_delete = self.re_filt(args.i, files_to_delete)
                        if files_to_delete:
                            print('dsync: deleting old files:')
                            for ndir in files_to_delete:
                                print(f'- {ndir}')
                                if not args.n:
                                    os.remove(ndir)
                        else:
                            print('dsync: no old files to delete')

                else:
                    print('dsync: no files found directory tree')
            # DEVICE DIRS
            dir_match = self.dev.wr_cmd(f"from nanoglob import glob;"
                                        f"glob(*{rest_args}, dir_only=True)"
                                        f";gc.collect()",
                                        silent=True, rtn_resp=True)
            if dir_match:
                self.dev.wr_cmd("from nanoglob import _get_path_depth"
                                ";from upysh2 import tree",
                                silent=True)
                if args.i:
                    dir_match = self.re_filt(args.i, dir_match)
                for dir in dir_match:
                    if args.t:
                        self.dev.wr_cmd(f"tree('{dir}')", follow=True)
                    else:
                        print(f"dsync: syncing path {dir}:")
                    depth_level = self.dev.wr_cmd(f"_get_path_depth('{dir}') + 1",
                                                  silent=True, rtn_resp=True)
                    pattern_dir = [f"{dir}/*{'/*'* i}" for i in range(depth_level)]
                    pattern_dir = [dir] + pattern_dir
                    local_dirs = nglob(*pattern_dir, dir_only=True)
                    dev_dirs = self.dev.wr_cmd(f"glob(*{pattern_dir}, "
                                               f"dir_only=True);gc.collect()",
                                               silent=True, rtn_resp=True)
                    dirs_to_make = [
                        ddir for ddir in dev_dirs if ddir not in local_dirs]
                    if args.i:
                        dirs_to_make = self.re_filt(args.i, dirs_to_make)
                    if dirs_to_make:
                        print('dsync: making new dirs:')
                        for ndir in dirs_to_make:
                            print(f'- {ndir}')
                            if not args.n:
                                os.makedirs(ndir)
                    else:
                        print(f'dsync: dirs: OK{CHECK}')
                    if args.rf:
                        dirs_to_delete = [ldir for ldir in local_dirs
                                          if ldir not in dev_dirs]
                        if args.i:
                            dirs_to_delete = self.re_filt(args.i, dirs_to_delete)
                        if dirs_to_delete:
                            print('dsync: deleting old dirs:')
                            for ndir in dirs_to_delete:
                                print(f'- {ndir}')
                                if not args.n:
                                    shutil.rmtree(ndir)

                    dev_cmd_files = (f"from shasum import shasum;"
                                     f"shasum(*{pattern_dir}, debug=True, "
                                     f"rtn=False, size=True);gc.collect()")
                    print('dsync: checking files...')
                    self.fastfileio.init_sha()
                    dev_files = self.dev.wr_cmd(dev_cmd_files, follow=True,
                                                rtn_resp=True, long_string=True,
                                                pipe=self.fastfileio.shapipe)
                    if not dev_files:
                        dev_files = self.fastfileio._shafiles
                        if dev_files:
                            self.fastfileio.end_sha()

                    if dev_files:
                        try:
                            local_files = shasum(*pattern_dir, debug=False, rtn=True,
                                                 size=True)
                        except Exception as e:
                            print(f'dsync: exception: {e}')
                            local_files = []

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
                            files_to_sync = [(sz ,nm)
                                             for sz, nm in files_to_sync
                                             if nm in _file_match]

                        if files_to_sync:
                            print('\ndsync: syncing new or modified files:')
                            for sz, name in files_to_sync:
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
                            print(f'dsync: files: OK{CHECK}')

                        if args.rf:
                            _dev_files = [df[0] for df in dev_files]
                            files_to_delete = [dfile[0] for dfile in local_files
                                               if dfile[0] not in _dev_files]
                            if args.i:
                                files_to_delete = self.re_filt(args.i, files_to_delete)
                            if files_to_delete:
                                print('dsync: deleting old files:')
                                for ndir in files_to_delete:
                                    print(f'- {ndir}')
                                    if not args.n:
                                        os.remove(ndir)
                            else:
                                print('dsync: no old files to delete')

                    else:
                        print('dsync: no files found directory tree')

            else:
                print(
                    f'dsync: {", ".join(rest_args)}: No matching dirs found in ./')
            return
