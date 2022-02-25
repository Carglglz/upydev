#!/usr/bin/env python
# Do sync , d_sync and backup
# @Author: carlosgilgonzalez
# @Date:   2019-07-09T20:49:15+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-13T22:18:43+01:00

import socket
import time as time_h
import os
import netifaces
import sys
from datetime import timedelta
from upydevice import Device, DeviceNotFound, DeviceException
from upydev.helpinfo import see_help


class SyncFileIO:
    def __init__(self, dev, args=None, devname='', port=None):
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
        self.server_ip = self.get_ip()
        self.server_socket = None
        self.conn = None
        self.args = args
        self.dev_name = devname

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

    def get_ip(self):
        try:
            ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_soc.connect(('8.8.8.8', 1))
            local_ip = ip_soc.getsockname()[0]
            ip_soc.close()
            return local_ip
        except Exception as e:
            return [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for
                    iface in netifaces.interfaces() if netifaces.AF_INET in
                    netifaces.ifaddresses(iface)][-1]

    def connect(self, args):

        self.dev.wr_cmd('import sync_tool as synct', silent=True, follow=False)

        time_h.sleep(0.2)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server_ip, self.port))
        self.server_socket.listen(1)
        # print('Server listening...')
        sync_connect_cmd = (f"cli_soc = synct.connect_SOC('{self.server_ip}', "
                            f"{self.port})")
        self.dev.wr_cmd(sync_connect_cmd, silent=True, follow=False)
        self.conn, addr = self.server_socket.accept()
        # print('Connection received from {}...'.format(addr))
        self.conn.settimeout(5)

    def get(self, src, dst_file, ppath=False, dev_name=None):
        self.args.f = src
        self.sync_file(self.args, self.dev_name)

    def get_files(self, args, dev_name):
        self.sync_files(args, dev_name)

    def sync_file(self, args, dev_name, out=None):
        self.get_pb()
        filesize, filetoget = args.f
        if filesize == 0:
            print(f"{filetoget} [{filesize/1000:.2f} kB]")
            filetoget = filetoget.split('/')[-1]
            with open(filetoget, 'wb') as log:
                pass
            self.dev.cmd_nb(f"print('{filetoget}')")
            return True
        # cmd_filesize_str = f"synct.os.stat('{filetoget}')[6]"
        # # espdev.output = None
        # # while espdev.output is None:
        # filesize = self.dev.wr_cmd(cmd_filesize_str, silent=True, follow=False,
        #                            rtn_resp=True)
        # print(f'File size: {filesize/1000:>40.2f} kB')
        time_h.sleep(1)
        sync_tool_cmd = f"synct.read_sd_file_sync_raw('{filetoget}',cli_soc)"
        self.dev.cmd_nb(sync_tool_cmd)
        # print(f'Syncing file {filetoget} from {dev_name}')
        print(f"{filetoget} [{filesize/1000:.2f} kB]")
        filetoget = filetoget.split('/')[-1]
        # print(f'Saving {filetoget} file')
        # print('Progress:\n')
        t0 = 0
        buff = b''
        t_start = time_h.time()
        EOF = False
        n_EOF = 1
        EOF_count = 0
        if out is not None:
            filetoget = out
        with open(filetoget, 'wb') as log:
            pass
        while True:
            t_0 = time_h.time()
            try:
                chunk = self.conn.recv(32*(1024))  # 32 KB
                if chunk != b'':
                    buff += chunk
                    loop_index_f = ((len(buff))/filesize)*self.bar_size
                    loop_index = int(loop_index_f)
                    loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                    nb_of_total = (f"{len(buff)/(1000**1):.2f}/{filesize/(1000**1):.2f}"
                                   f" kB")
                    percentage = len(buff)/filesize
                    # tdiff = time_h.time() - t_0
                    t_elapsed = time_h.time() - t_start
                    t_speed = f"{(len(buff)/(1000**1))/t_elapsed:^2.2f}"
                    ett = filesize / (len(buff) / t_elapsed)
                    if self.pb:
                        self.do_pg_bar(loop_index, self.wheel,
                                       nb_of_total, t_speed, t_elapsed,
                                       loop_index_l, percentage, ett)
                    else:
                        sys.stdout.write("Received %d of %d bytes\r" %
                                         (len(buff), filesize))
                        sys.stdout.flush()
                    # do_pg_bar(loop_index, wheel)
                    with open(filetoget, 'ab') as log:
                        log.write(chunk)
                    if len(buff) == filesize:
                        EOF = True
                        break
                else:
                    pass

            except Exception as e:
                if e == KeyboardInterrupt:
                    break

                else:
                    if str(e) == 'timed out':
                        break
        # print(chunk)
        # print(filesize, len(buff))
        if not EOF:
            print('CONNECTION ERROR, TRYING AGAIN...')
            self.sync_file(args, dev_name, out=out)
        # print(f'\n\nDone in {round(t_elapsed, 2)} seconds')
        # print(f'Total data received: {filesize/1000:>30.2f} kB')
        print('')
        return True

    def sync_files(self, args, dev_name):
        files_to_get = args.fre
        for file in files_to_get:
            src_file = file[1]
            dst_file = f"./{file[1].split('/')[-1]}"
            try:
                if not src_file.startswith('/'):
                    src_file = f'/{src_file}'
                print(f"{dev_name}:{src_file} -> {dst_file}\n")
                args.f = file
                self.sync_file(args, dev_name)
                self.dev.output_queue.get()
                print('')
            except KeyboardInterrupt:
                print('KeyboardInterrupt: get Operation Canceled')
            # time_h.sleep(1)
        return True

    def disconnect(self):
        self.conn.close()
        self.dev.wr_cmd('cli_soc.close()', silent=True)
        self.dev.disconnect()

# SerialSyncFileIO:
# get file with cat --> cat('file.txt') --> filter cmd then readline


def synctool(args, dev_name):
    try:
        dev = Device(args.t, args.p, init=True, ssl=args.wss,
                     auth=args.wss)
        rsyncio = SyncFileIO(dev, port=8005)
        if args.m == 'fget':
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
                        rsyncio.connect(args)
                        print(f'Downloading file {args.f} @ {dev_name}...')
                        file_to_get = (file_exists[0][0], args.f)
                        if args.s == 'sd':
                            file_to_get = (file_exists[0][0], f'/sd/{args.f}')
                        if args.dir is not None:
                            file_to_get = (file_exists[0][0], f'/{args.dir}/{args.f}')
                        # if not args.wss:
                        #     copyfile_str = 'upytool -p {} {}:{} .{}'.format(
                        #         passwd, target, file_to_get, id_file)
                        dst_file = args.f
                        # if dir == '':
                        #     dir = '/'
                        src_file = file_to_get[1]
                        if not src_file.startswith('/'):
                            src_file = '/'.join([dir, dst_file])
                        print(f"{dev_name}:{src_file} -> ./{dst_file}\n")
                        args.f = file_to_get
                        result = rsyncio.sync_file(args, dev_name)
                        print('Done!')
                        time_h.sleep(0.2)
                        rsyncio.disconnect()
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
                        cmd_str = (f"import uos;[(uos.stat('/{args.dir}/'+file)[6],"
                                   f" file) for file in uos.listdir('/{args.dir}') if "
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
                            rsyncio.connect(args)
                            print(f'\nDownloading files @ {dev_name}...')
                            # file_to_get = args.f
                            if args.dir is not None:
                                args.fre = [(file[0], f'/{args.dir}/{file[1]}')
                                            for file in files_to_get]
                            else:
                                args.fre = files_to_get
                            result = rsyncio.sync_files(args, dev_name)
                            print('Done!')
                            time_h.sleep(0.2)
                            rsyncio.disconnect()
                        else:
                            if dir == '':
                                dir = '/'
                            print(f'Files Not found in {dev_name}:{dir} directory')
                except KeyboardInterrupt:
                    print('KeyboardInterrupt: get Operation Canceled')
    except DeviceNotFound as e:
        print(f'ERROR {e}')

    return
