import os
import time
import sys
from datetime import timedelta
from upydevice import Device, DeviceNotFound, DeviceException
from upydev.helpinfo import see_help
import glob


class SerialFileIO:
    def __init__(self, dev, port=None, devname=None):
        self.host = None
        self.port = port
        self.dev = dev
        self.dev_name = devname
        self.buff = bytearray(1024*2)
        self.bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
        self.columns, self.rows = os.get_terminal_size(0)
        self.cnt_size = 65
        self.bar_size = int((self.columns - self.cnt_size))
        self.pb = False
        self.wheel = ['|', '/', '-', "\\"]

    def get_pb(self):
        self.columns, self.rows = os.get_terminal_size(0)
        if self.columns > self.cnt_size:
            self.bar_size = int((self.columns - self.cnt_size))
            self.pb = True
        else:
            self.bar_size = 1
            self.pb = False

    def do_pg_bar(self, index, wheel, nb_of_total, speed, time_e, loop_l,
                  percentage, ett):
        l_bloc = self.bloc_progress[loop_l]
        if index == self.bar_size:
            l_bloc = "█"
        sys.stdout.write("\033[K")
        print('▏{}▏{:>2}{:>5} % | {} | {:>5} kB/s | {}/{} s'.format("█" * index + l_bloc + " "*((self.bar_size+1) - len("█" * index + l_bloc)),
                                                                    wheel[index % 4],
                                                                    int((percentage)*100),
                                                                    nb_of_total, speed,
                                                                    str(timedelta(seconds=time_e)).split(
                                                                        '.')[0][2:],
                                                                    str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
        sys.stdout.flush()

    def get(self, src, dst_file, chunk_size=256, ppath=False, dev_name=None,
            fullpath=False, psize=True):
        if not dev_name:
            dev_name = self.dev_name
        self.get_pb()
        cnt = 0
        t_start = time.time()
        sz = src[0]
        src = src[1]
        if not fullpath:
            dst_file = src.split('/')[-1]
        if ppath:
            print(f'{dev_name}:{src} -> {dst_file}', end='\n\n')
        if psize:
            print(f"{src}  [{sz / 1000:.2f} kB]")
        self.dev.flush_conn()
        self.dev.cmd("f=open('%s','rb');r=f.read" % src, silent=True)
        with open(dst_file, 'wb') as f:
            pass
        with open(dst_file, 'ab') as f:
            while True:
                data = b''
                data = self.dev.cmd("print(r(%u))" % chunk_size, silent=True,
                                    rtn_resp=True)
                if data == b'':
                    break
                f.write(data)
                cnt += len(data)
                loop_index_f = (cnt/sz)*self.bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = f"{cnt/(1000):.2f}/{sz/(1000):.2f} kB"
                percentage = cnt / sz
                t_elapsed = time.time() - t_start
                t_speed = f"{(cnt/(1000))/t_elapsed:^2.2f}"
                ett = sz / (cnt / t_elapsed)
                if self.pb:
                    self.do_pg_bar(loop_index, self.wheel,
                                   nb_of_total, t_speed, t_elapsed,
                                   loop_index_l, percentage, ett)
        print('\n')
        self.dev.cmd("f.close()", silent=True)
        return True

    def get_files(self, args, dev_name):
        files_to_get = args.fre
        for file in files_to_get:
            src_file = file[1]
            dst_file = f"./{file[1].split('/')[-1]}"
            try:
                if not src_file.startswith('/'):
                    src_file = f'/{src_file}'
                print(f"{dev_name}:{src_file} -> {dst_file}\n")
                self.get(file, dst_file)
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
                self.dev.cmd("f.close()", silent=True)
        return True

    def put(self, src, dst_file, chunk_size=256, abs_path=True, ppath=False,
            dev_name=None, psize=True):  # from Pyboard.py
        if not dev_name:
            dev_name = self.dev_name
        self.get_pb()
        sz = os.stat(src)[6]
        cnt = 0
        t_start = time.time()
        if not abs_path:
            src_ori = src
            src = src.split('/')[-1]
        if ppath:
            if not dst_file.startswith('/'):
                print(f"{src} -> {dev_name}:/{dst_file}\n")
            else:
                print(f"{src} -> {dev_name}:{dst_file}\n")
        if psize:
            print(f"{src}  [{sz / 1000:.2f} kB]")
        self.dev.cmd("f=open('%s','wb');w=f.write" % dst_file, silent=True)
        if not abs_path:
            src = src_ori
        with open(src, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break

                self.dev.cmd('w(' + repr(data) + ')'+'\r', silent=True)

                cnt += len(data)
                loop_index_f = (cnt/sz)*self.bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = f"{cnt/(1000):.2f}/{sz/(1000):.2f} kB"
                percentage = cnt / sz
                t_elapsed = time.time() - t_start
                t_speed = f"{(cnt/(1000))/t_elapsed:^2.2f}"
                ett = sz / (cnt / t_elapsed)
                if self.pb:
                    self.do_pg_bar(loop_index, self.wheel,
                                   nb_of_total, t_speed, t_elapsed,
                                   loop_index_l, percentage, ett)
        print('\n')
        self.dev.cmd("f.close()", silent=True)
        self.dev.flush_conn()
        return True

    def put_files(self, args, dev_name):
        files_to_put = args.fre
        for file in files_to_put:
            src_file = file
            dst_file = file.split('/')[-1]
            if args.s:
                if args.s.startswith('./'):
                    args.s = args.s.replace('./', '')
                if args.s != '/':
                    dst_file = '/'.join([args.s, dst_file])
                else:
                    dst_file = ''.join([args.s, dst_file])
            try:
                abs_dst_file = dst_file
                if not dst_file.startswith('/'):
                    abs_dst_file = f'/{dst_file}'
                print(f"{src_file} -> {dev_name}:{abs_dst_file}\n")
                self.put(src_file, dst_file)
            except KeyboardInterrupt:
                print('KeyboardInterrupt: put Operation Canceled')
                self.dev.cmd("f.close()", silent=True)
        return True


def serialtool(args, dev_name):
    if not args.f and not args.fre:
        print('args -f or -fre required:')
        see_help(args.m)
        sys.exit()
    try:
        dev = Device(args.t, args.p, init=True)
        serialio = SerialFileIO(dev)
        if args.m == 'put':
            if not args.f and not args.fre:
                print('args -f or -fre required:')
                see_help(args.m)
                sys.exit()
            if args.f:
                if os.path.isdir(args.f):
                    os.chdir(args.f)
                    args.fre = ['.']
            if not args.fre:
                # One file:
                source = ''
                if args.s == 'sd':
                    source += '/' + args.s
                file = args.f
                if args.dir is not None:
                    source += '/' + args.dir
                file_in_upy = file.split('/')[-1]
                if source:
                    args.s = source + '/'
                # Check if file exists:
                try:
                    os.stat(file)[6]
                    if not os.path.isdir(file):
                        result = None
                        if args.s:
                            is_dir_cmd = (f"import uos, gc; uos.stat('{source}')[0] & "
                                          f"0x4000")
                            is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                            # dev.disconnect()
                            if dev._traceback.decode() in dev.response:
                                try:
                                    raise DeviceException(dev.response)
                                except Exception as e:
                                    print(e)
                                    print(f'Directory {dev_name}:{source} does NOT '
                                          f'exist')
                                    result = False
                            else:
                                if is_dir:
                                    print(f'Uploading file {file_in_upy} @ {dev_name}'
                                          f'...')
                                    src_file = file
                                    dst_file = args.s + file_in_upy
                                    print(f"{src_file} -> {dev_name}:{dst_file}\n")
                                    result = serialio.put(file, dst_file)
                        else:
                            print(f'Uploading file {file_in_upy} @ {dev_name}...')
                            src_file = file
                            if not source:
                                source = '/'
                            dst_file = source + file_in_upy
                            print(f"{src_file} -> {dev_name}:{dst_file}\n")
                            result = serialio.put(file, file_in_upy)

                        # Reset:
                        if result:
                            if args.rst is None:
                                time.sleep(0.1)
                                dev.reset(reconnect=False)
                    else:
                        print(f'FileNotFoundError: {file} is a directory')
                except FileNotFoundError as e:
                    print('FileNotFoundError:', e)
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: put Operation Canceled')
            else:
                # Handle special cases:
                # CASE [cwd]:
                if args.fre[0] == 'cwd' or args.fre[0] == '.':
                    args.fre = [fname for fname in os.listdir(
                        './') if os.path.isfile(fname) and not fname.startswith('.')]
                    print('Files in ./{} to put: '.format(os.getcwd().split('/')[-1]))

                elif '*' in args.fre[0]:
                    args.fre = glob.glob(args.fre[0])
                    print('Files to put: ')
                else:
                    print('Files to put: ')

                files_to_put = []
                for file in args.fre:
                    try:
                        filesize = os.stat(file)[6]
                        if not os.path.isdir(file):
                            files_to_put.append(file)
                            print(f'- {file} [{filesize/1000:.2f} kB]')
                        else:
                            filesize = 'IsDirectory'
                            print(f'- {file} [{filesize}]')
                    except Exception:
                        filesize = 'FileNotFoundError'
                        print(f'- {file} [{filesize}]')
                args.fre = files_to_put
                # Multiple file:
                source = ''
                if args.s == 'sd':
                    source += '/' + args.s
                file = ''
                if args.dir is not None:
                    source += '/' + args.dir
                file_in_upy = file.split('/')[-1]
                if source:
                    args.s = source
                try:
                    if args.s:
                        is_dir_cmd = f"import uos, gc; uos.stat('{source}')[0] & 0x4000"
                        is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                        if dev._traceback.decode() in dev.response:
                            try:
                                raise DeviceException(dev.response)
                            except Exception as e:
                                print(e)
                                print(f'Directory {dev_name}:{source} does NOT exist')
                                result = False
                        else:
                            if is_dir:
                                print(f'\nUploading files @ {dev_name}...\n')
                                result = serialio.put_files(args, dev_name)
                    else:
                        args.s = source
                        print(f'\nUploading files @ {dev_name}...\n')
                        result = serialio.put_files(args, dev_name)

                    # Reset:
                    if result:
                        if args.rst is None:
                            time.sleep(0.1)
                            dev.reset(reconnect=False)
                            # dev.disconnect()
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: put Operation Canceled')
        elif args.m == 'get':
            if not args.f and not args.fre:
                print('args -f or -fre required:')
                see_help(args.m)
                sys.exit()
            if args.f:
                if '/' in args.f:
                    if len(args.f.rsplit('/', 1)) > 1:
                        args.dir, args.f = args.f.rsplit('/', 1)
                        if args.f == '':
                            args.fre = ['.']
            if not args.fre:
                if args.s is None and args.dir is None:
                    print(f'Looking for file in {dev_name}:/ dir ...')
                    cmd_str = (f"import uos;[(uos.stat(file)[6], file) for file "
                               f"in uos.listdir() if file == '{args.f}' and not "
                               f"uos.stat(file)[0] & 0x4000]")
                    dir = ''
                if args.dir is not None or args.s is not None:
                    if args.s is not None:
                        args.dir = f'{args.s}/{args.dir}'
                    print(f'Looking for file in {dev_name}:/{args.dir} dir')
                    cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], file)"
                               f" for file in uos.listdir('/{args.dir}')"
                               f" if file == '{args.f}' and "
                               f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                    dir = f'/{args.dir}'

                try:
                    file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print(f'Directory {dev_name}:{dir} does NOT exist')
                            result = False

                    if isinstance(file_exists, list) and file_exists:
                        print(f'Downloading file {args.f} @ {dev_name}...')
                        file_to_get = (file_exists[0][0], args.f)
                        if args.s == 'sd':
                            file_to_get = (file_exists[0][0], f'/sd/{args.f}')
                        if args.dir is not None:
                            file_to_get = (file_exists[0][0], f'/{args.dir}/{args.f}')
                        dst_file = args.f
                        src_file = file_to_get[1]
                        if not src_file.startswith('/'):
                            src_file = '/'.join([dir, dst_file])
                        print(f"{dev_name}:{src_file} -> ./{dst_file}\n")
                        result = serialio.get(file_to_get, dst_file)
                        print('Done!')
                    else:
                        if not file_exists:
                            if dir == '':
                                dir = '/'
                            print(f'File Not found in {dev_name}:{dir} directory or')
                            if dir == '/':
                                dir = ''
                            print(f'{dev_name}:{dir}/{args.f} is a directory')
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: get Operation Canceled')

            else:
                # list to filter files:
                # regular names:
                # wildcard names:
                # cwd:
                filter_files = []
                for file in args.fre:
                    if file not in ['cwd', '.']:
                        filter_files.append(file.replace(
                            '.', '\.').replace('*', '.*') + '$')

                if args.s is None and args.dir is None:
                    print(f'Looking for files in {dev_name}:/ dir ...')
                    if filter_files:
                        cmd_str = ("import uos;[(uos.stat(file)[6], file) for file in "
                                   "uos.listdir() if any([patt.match(file) for patt in "
                                   "pattrn]) and not uos.stat(file)[0] & 0x4000]")
                    else:
                        cmd_str = ("import uos;[(uos.stat(file)[6], file) for file "
                                   "in uos.listdir() if not "
                                   "uos.stat(file)[0] & 0x4000]")
                    dir = ''
                elif args.dir is not None or args.s is not None:
                    if args.s is not None:
                        args.dir = f'{args.s}/{args.dir}'
                    print(f'Looking for files in {dev_name}:/{args.dir} dir')
                    if filter_files:
                        cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], "
                                   f"file) for file in uos.listdir('/{args.dir}') if "
                                   f"any([patt.match(file) for patt in pattrn]) and "
                                   f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                    else:
                        cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6], "
                                   f"file) for file in uos.listdir('/{args.dir}') if "
                                   f"not uos.stat('/{args.dir}/'+file)[0] & 0x4000]")
                    dir = f'/{args.dir}'
                try:
                    if filter_files:
                        if len(f"filter_files = {filter_files}") < 250:
                            filter_files_cmd = f"filter_files = {filter_files}"
                            dev.cmd(filter_files_cmd, silent=True)
                        else:
                            dev.cmd("filter_files = []", silent=True)
                            for i in range(0, len(filter_files), 15):
                                filter_files_cmd = (f"filter_files += "
                                                    f"{filter_files[i:i+15]}")
                                dev.cmd(filter_files_cmd, silent=True)
                        dev.cmd("import re; pattrn = [re.compile(f) for "
                                "f in filter_files]", silent=True)
                        cmd_str += (';import gc;del(filter_files);del(pattrn);'
                                    'gc.collect()')
                    file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print(f'Directory {dev_name}:{dir} does NOT exist')
                            result = False
                    else:
                        files_to_get = []
                        # Handle special cases:
                        # CASE [cwd]:
                        if len(args.fre) == 1:
                            if args.fre[0] == 'cwd' or args.fre[0] == '.':
                                args.fre = file_exists
                            elif '*' in args.fre[0]:
                                start_exp, end_exp = args.fre[0].split('*')
                                args.fre = [file for file in file_exists if
                                            file[1].startswith(start_exp)
                                            and file[1].endswith(end_exp)]
                        if dir == '':
                            dir = '/'
                        print(f'Files in {dev_name}:{dir} to get: \n')
                        if file_exists == args.fre:
                            args.fre = [nfile[1] for nfile in file_exists]
                        for file in args.fre:
                            if file in [nfile[1] for nfile in file_exists]:
                                for sz, nfile in file_exists:
                                    # print(file, nfile)
                                    if file == nfile:
                                        files_to_get.append((sz, nfile))
                                        print(f'- {nfile} [{sz/1000:.2f} kB]')
                            elif '*' in file:
                                start_exp, end_exp = file.split('*')
                                for reg_file in file_exists:
                                    if (reg_file[1].startswith(start_exp) and reg_file[1].endswith(end_exp)):
                                        files_to_get.append(reg_file)
                                        print(
                                            (f'- {reg_file[1]} [{reg_file[0]/1000:.2f}'
                                             f' kB]'))
                            else:
                                filesize = 'FileNotFoundError'
                                print(f'- {file} [{filesize}]')
                        if files_to_get:
                            print(f'\nDownloading files @ {dev_name}...')
                            # file_to_get = args.f
                            if args.dir is not None:
                                args.fre = [(file[0], f'/{args.dir}/{file[1]}')
                                            for file in files_to_get]
                            else:
                                args.fre = files_to_get
                            result = serialio.get_files(args, dev_name)
                            print('Done!')
                        else:
                            if dir == '':
                                dir = '/'
                            print(f'Files Not found in {dev_name}:{dir} directory')
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: get Operation Canceled')
    except DeviceNotFound as e:
        print(f'ERROR {e}')

    return
