import os
import time
import sys
from datetime import timedelta
from upydevice import Device, DeviceNotFound, DeviceException
from upydev.helpinfo import see_help
from upydev.dsyncio import d_sync_recursive
from upydev import upip_host
import shutil
import glob


class BleFileIO:
    def __init__(self, dev, port=None):
        self.host = None
        self.port = port
        self.dev = dev
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
        print('▏{}▏{:>2}{:>5} % | {} | {:>5} KB/s | {}/{} s'.format("█" *index + l_bloc  + " "*((self.bar_size+1) - len("█" *index + l_bloc)),
                                                                        wheel[index % 4],
                                                                        int((percentage)*100),
                                                                        nb_of_total, speed,
                                                                        str(timedelta(seconds=time_e)).split('.')[0][2:],
                                                                        str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
        sys.stdout.flush()

    def get(self, src, dst_file, chunk_size=256, ppath=False, dev_name=None):  # from Pyboard.py
        self.get_pb()
        cnt = 0
        t_start = time.time()
        # def_chunk = chunk
        sz = self.dev.cmd("import uos; uos.stat('{}')[6]".format(src), silent=True,
                          rtn_resp=True)

        dst_file = src.split('/')[-1]
        if ppath:
            print('{}:{} -> {}'.format(dev_name, src, dst_file), end='\n\n')
        print("{}  [{:.2f} KB]".format(src, sz / 1024))
        self.dev.flush()
        # self.start_SOC()
        self.dev.cmd("f=open('%s','rb');r=f.read" % src, silent=True)
        with open(dst_file, 'wb') as f:
            pass
        with open(dst_file, 'ab') as f:
            while True:
                data = b''
                data = self.dev.cmd("print(r(%u))" % chunk_size, rtn_resp=True,
                                    silent=True)
                if data == b'':
                    break
                f.write(data)
                cnt += len(data)
                loop_index_f = (cnt/sz)*self.bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = "{:.2f}/{:.2f} KB".format(cnt/(1024), sz/(1024))
                percentage = cnt / sz
                t_elapsed = time.time() - t_start
                t_speed = "{:^2.2f}".format((cnt/(1024))/t_elapsed)
                ett = sz / (cnt / t_elapsed)
                if self.pb:
                    self.do_pg_bar(loop_index, self.wheel,
                                   nb_of_total, t_speed, t_elapsed,
                                   loop_index_l, percentage, ett)
        print('\n')
        self.dev.cmd("f.close()")
        return True

    def get_files(self, args, dev_name):
        files_to_get = args.fre
        for file in files_to_get:
            src_file = file
            dst_file = './{}'.format(file.split('/')[-1])
            try:
                if not src_file.startswith('/'):
                    src_file = '/{}'.format(src_file)
                print("{}:{} -> {}\n".format(dev_name, src_file, dst_file))
                self.get(file, dst_file)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: get Operation Cancelled')
                self.dev.cmd("f.close()", silent=True)
        return True

    def put(self, src, dst_file, chunk_size=256, abs_path=True, ppath=False,
            dev_name=None):  # from Pyboard.py
        self.get_pb()
        sz = os.stat(src)[6]
        cnt = 0
        t_start = time.time()
        if not abs_path:
            src_ori = src
            src = src.split('/')[-1]
        if ppath:
            if not dst_file.startswith('/'):
                print("{} -> {}:/{}\n".format(src, dev_name, dst_file))
            else:
                print("{} -> {}:{}\n".format(src, dev_name, dst_file))
        print("{}  [{:.2f} KB]".format(src, sz / 1024))
        self.dev.cmd("f=open('%s','wb');w=f.write" % dst_file, silent=True)
        if not abs_path:
            src = src_ori
        with open(src, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break

                if len(data) > self.dev.len_buffer:
                    for i in range(0, len(data), self.dev.len_buffer):
                        self.dev.cmd('w(' + repr(data[i:i+self.dev.len_buffer]) + ')',
                                     silent=True)
                else:
                    self.dev.cmd('w(' + repr(data) + ')', silent=True)

                cnt += len(data)
                loop_index_f = (cnt/sz)*self.bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = "{:.2f}/{:.2f} KB".format(cnt/(1024), sz/(1024))
                percentage = cnt / sz
                t_elapsed = time.time() - t_start
                t_speed = "{:^2.2f}".format((cnt/(1024))/t_elapsed)
                ett = sz / (cnt / t_elapsed)
                if self.pb:
                    self.do_pg_bar(loop_index, self.wheel,
                                   nb_of_total, t_speed, t_elapsed,
                                   loop_index_l, percentage, ett)
        print('\n')
        self.dev.cmd("f.close()", silent=True)
        self.dev.flush()
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
                    abs_dst_file = '/{}'.format(dst_file)
                print("{} -> {}:{}\n".format(src_file, dev_name, abs_dst_file))
                self.put(src_file, dst_file)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: put Operation Cancelled')
                self.dev.cmd("f.close()", silent=True)
        return True

    def upip_install(self, args, dev_name):
        try:
            dir_lib = 'lib'
            lib = args.f
            dev_lib = args.dir
            if not dev_lib:
                dev_lib = "./"
            pckg_content, pckg_dir = upip_host.install_pkg(lib, ".")
            # sync local lib to device lib
            print('Installing {} to {}:/lib'.format(pckg_dir, dev_name))
            # cwd_now = self.dev.cmd('os.getcwd()', silent=True, rtn_resp=True)
            # if self.dev.dev_platform == 'pyboard':
            # self.dev.cmd("os.chdir('/flash')")
            # d_sync_recursive(dir_lib, show_tree=True, root_sync_folder=".")
            d_sync_recursive(dir_lib, devIO=self,
                             show_tree=True,
                             rootdir=dev_lib,
                             root_sync_folder=dir_lib,
                             args=args,
                             dev_name=dev_name)
            rm_lib = input('Do you want to remove local lib? (y/n): ')
            if rm_lib == 'y':
                shutil.rmtree(dir_lib)
            print("Successfully installed {} to {} :/lib".format(pckg_dir, dev_name))
            # self.dev.cmd("os.chdir('{}')".format(cwd_now))
        except Exception as e:
            print('Please indicate a library to install')


def bletool(args, dev_name):
    if not args.f and not args.fre:
        print('args -f or -fre required:')
        see_help(args.m)
        sys.exit()
    try:
        dev = Device(args.t, args.p, init=True)
        bleio = BleFileIO(dev)
        if args.m == 'put':
            if not args.f and not args.fre:
                print('args -f or -fre required:')
                see_help(args.m)
                sys.exit()
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
                        if args.s:
                            is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                            is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                            # dev.disconnect()
                            if dev._traceback.decode() in dev.response:
                                try:
                                    raise DeviceException(dev.response)
                                except Exception as e:
                                    print(e)
                                    print('Directory {}:{} does NOT exist'.format(dev_name, source))
                                    result = False
                            else:
                                if is_dir:
                                    print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                                    src_file = file
                                    dst_file = args.s + file_in_upy
                                    print("{} -> {}:{}\n".format(src_file, dev_name, dst_file))
                                    result = bleio.put(file, dst_file)
                        else:
                            print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                            src_file = file
                            if not source:
                                source = '/'
                            dst_file = source + file_in_upy
                            print("{} -> {}:{}\n".format(src_file, dev_name, dst_file))
                            result = bleio.put(file, file_in_upy)

                        # Reset:
                        if result:
                            if args.rst is None:
                                time.sleep(0.4)
                                dev.reset(reconnect=False)
                                time.sleep(0.4)
                    else:
                        print('FileNotFoundError: {} is a directory'.format(file))
                except FileNotFoundError as e:
                    print('FileNotFoundError:', e)
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: put Operation Cancelled')
            else:
                # Handle special cases:
                # CASE [cwd]:
                if args.fre[0] == 'cwd' or args.fre[0] == '.':
                    args.fre = [fname for fname in os.listdir('./') if os.path.isfile(fname) and not fname.startswith('.')]
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
                            print('- {} [{:.2f} KB]'.format(file, filesize/1024))
                        else:
                            filesize = 'IsDirectory'
                            print('- {} [{}]'.format(file, filesize))
                    except Exception as e:
                        filesize = 'FileNotFoundError'
                        print('- {} [{}]'.format(file, filesize))
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
                        is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                        is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                        if dev._traceback.decode() in dev.response:
                            try:
                                raise DeviceException(dev.response)
                            except Exception as e:
                                print(e)
                                print('Directory {}:{} does NOT exist'.format(dev_name, source))
                                result = False
                        else:
                            if is_dir:
                                print('\nUploading files @ {}...\n'.format(dev_name))
                                result = bleio.put_files(args, dev_name)
                    else:
                        args.s = source
                        print('\nUploading files @ {}...\n'.format(dev_name))
                        result = bleio.put_files(args, dev_name)

                    # Reset:
                    if result:
                        if args.rst is None:
                            time.sleep(0.4)
                            dev.reset(reconnect=False)
                            time.sleep(0.4)
                            # dev.disconnect()
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: put Operation Cancelled')
        elif args.m == 'get':
            if not args.f and not args.fre:
                print('args -f or -fre required:')
                see_help(args.m)
                sys.exit()
            if not args.fre:
                if args.s is None and args.dir is None:
                    print('Looking for file in {}:/ dir ...'.format(dev_name))
                    cmd_str = "import uos;'{}' in uos.listdir()".format(args.f)
                    dir = ''
                if args.dir is not None or args.s is not None:
                    if args.s is not None:
                        args.dir = '{}/{}'.format(args.s, args.dir)
                    print('Looking for file in {}:/{} dir'.format(dev_name, args.dir))
                    cmd_str = "import uos; '{}' in uos.listdir('/{}')".format(args.f, args.dir)
                    dir = '/{}'.format(args.dir)

                try:
                    file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print('Directory {}:{} does NOT exist'.format(dev_name, dir))
                            result = False
                    else:
                        if file_exists is True:
                            cmd_str = "import uos; not uos.stat('{}')[0] & 0x4000 ".format(dir + '/' + args.f)
                            is_file = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if file_exists is True and is_file:
                        print('Downloading file {} @ {}...'.format(args.f, dev_name))
                        file_to_get = args.f
                        if args.s == 'sd':
                            file_to_get = '/sd/{}'.format(args.f)
                        if args.dir is not None:
                            file_to_get = '/{}/{}'.format(args.dir, args.f)
                        # if not args.wss:
                        #     copyfile_str = 'upytool -p {} {}:{} .{}'.format(
                        #         passwd, target, file_to_get, id_file)
                        dst_file = args.f
                        # if dir == '':
                        #     dir = '/'
                        src_file = file_to_get
                        if not src_file.startswith('/'):
                            src_file = '/'.join([dir, dst_file])
                        print("{}:{} -> ./{}\n".format(dev_name, src_file, dst_file))
                        result = bleio.get(file_to_get, dst_file)
                        print('Done!')
                    else:
                        if file_exists is False:
                            if dir == '':
                                dir = '/'
                            print('File Not found in {}:{} directory'.format(dev_name, dir))
                        elif file_exists is True:
                            if is_file is not True:
                                print('{}:{} is a directory'.format(dev_name, dir + '/' + args.f))
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: get Operation Cancelled')

            else:
                if args.s is None and args.dir is None:
                    print('Looking for files in {}:/ dir ...'.format(dev_name))
                    cmd_str = "import uos;[file for file in uos.listdir() if not uos.stat(file)[0] & 0x4000]"
                    dir = ''
                elif args.dir is not None or args.s is not None:
                    if args.s is not None:
                        args.dir = '{}/{}'.format(args.s, args.dir)
                    print('Looking for files in {}:/{} dir'.format(dev_name, args.dir))
                    cmd_str = "import uos;[file for file in uos.listdir('/{0}') if not uos.stat('/{0}/'+file)[0] & 0x4000]".format(args.dir)
                    dir = '/{}'.format(args.dir)
                try:
                    file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print('Directory {}:{} does NOT exist'.format(dev_name, dir))
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
                                args.fre = [file for file in file_exists if file.startswith(start_exp) and file.endswith(end_exp)]
                        if dir == '':
                            dir = '/'
                        print('Files in {}:{} to get: '.format(dev_name, dir))
                        for file in args.fre:
                            if file in file_exists:
                                files_to_get.append(file)
                                print('- {} '.format(file))
                            elif '*' in file:
                                start_exp, end_exp = file.split('*')
                                for reg_file in file_exists:
                                    if reg_file.startswith(start_exp) and reg_file.endswith(end_exp):
                                        files_to_get.append(reg_file)
                                        print('- {} '.format(reg_file))
                            else:
                                filesize = 'FileNotFoundError'
                                print('- {} [{}]'.format(file, filesize))
                        if files_to_get:
                            print('Downloading files @ {}...'.format(dev_name))
                            # file_to_get = args.f
                            if args.dir is not None:
                                args.fre = ['/{}/{}'.format(args.dir, file) for file in files_to_get]
                            else:
                                args.fre = files_to_get
                            result = bleio.get_files(args, dev_name)
                            print('Done!')
                        else:
                            if dir == '':
                                dir = '/'
                            print('Files Not found in {}:{} directory'.format(dev_name, dir))
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: get Operation Cancelled')
    except DeviceNotFound as e:
        print('ERROR {}'.format(e))

    if dev.is_connected():
        dev.disconnect()
        time.sleep(0.1)

    return
