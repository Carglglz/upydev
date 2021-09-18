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
        self.server_ip = self.get_ip()
        self.server_socket = None
        self.conn = None

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
        print('▏{}▏{:>2}{:>5} % | {} | {:>5} KB/s | {}/{} s'.format("█" * index + l_bloc + " "*((self.bar_size+1) - len("█" * index + l_bloc)),
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
        sync_connect_cmd = "cli_soc = synct.connect_SOC('{}', {})".format(self.server_ip,
                                                                          self.port)
        self.dev.wr_cmd(sync_connect_cmd, silent=True, follow=False)
        self.conn, addr = self.server_socket.accept()
        # print('Connection received from {}...'.format(addr))
        self.conn.settimeout(5)

    def sync_file(self, args, dev_name, out=None):
        self.get_pb()
        dir = ''
        if args.dir:
            dir = args.dir
        filetoget = args.f
        cmd_filesize_str = "synct.os.stat('{}' + '/' + '{}')[6]".format(
            dir, filetoget)
        # espdev.output = None
        # while espdev.output is None:
        filesize = self.dev.wr_cmd(cmd_filesize_str, silent=True, follow=False,
                                   rtn_resp=True)
        print('File size: {:>40.2f} kB'.format(filesize/1024))
        time_h.sleep(1)
        sync_tool_cmd = "synct.read_sd_file_sync_raw({},cli_soc)".format(
            "'{}/{}'".format(dir, filetoget))
        self.dev.cmd_nb(sync_tool_cmd)
        print('Syncing file {} from {}'.format(filetoget, dev_name))
        print('Saving {} file'.format(filetoget))
        print('Progress:\n')
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
                    nb_of_total = "{:.2f}/{:.2f} MB".format(
                        len(buff)/(1024**2), filesize/(1024**2))
                    percentage = len(buff)/filesize
                    tdiff = time_h.time() - t_0
                    t_elapsed = time_h.time() - t_start
                    t_speed = "{:^2.2f}".format((len(buff)/(1024**2))/t_elapsed)
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
        print('\n\nDone in {} seconds'.format(round(t_elapsed, 2)))
        print('Total data received: {:>30.2f} kB'.format(filesize/1024))
        return True

    def sync_files(self, args, dev_name):
        files_to_get = args.fre
        for file in files_to_get:
            src_file = file
            dst_file = './{}'.format(file.split('/')[-1])
            try:
                if not src_file.startswith('/'):
                    src_file = '/{}'.format(src_file)
                print("{}:{} -> {}\n".format(dev_name, src_file, dst_file))
                args.f = file
                self.sync_file(args, dev_name)
                self.dev.output_queue.get()
                print('')
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: get Operation Cancelled')
            # time_h.sleep(1)
        return True

    def disconnect(self):
        self.conn.close()
        self.dev.wr_cmd('cli_soc.close()', silent=True)
        self.dev.disconnect()


def synctool(args, dev_name):
    try:
        dev = Device(args.t, args.p, init=True, autodetect=True)
        rsyncio = SyncFileIO(dev, port=8005)
        if args.m == 'fget':
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
                    cmd_str = "import uos; '{}' in uos.listdir('/{}')".format(
                        args.f, args.dir)
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
                            cmd_str = "import uos; not uos.stat('{}')[0] & 0x4000 ".format(
                                dir + '/' + args.f)
                            is_file = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                    if file_exists is True and is_file:
                        rsyncio.connect(args)
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
                        args.f = file_to_get
                        result = rsyncio.sync_file(args, dev_name)
                        print('Done!')
                        rsyncio.disconnect()
                    else:
                        if file_exists is False:
                            if dir == '':
                                dir = '/'
                            print('File Not found in {}:{} directory'.format(dev_name, dir))
                        elif file_exists is True:
                            if is_file is not True:
                                print('{}:{} is a directory'.format(
                                    dev_name, dir + '/' + args.f))
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
                    cmd_str = "import uos;[file for file in uos.listdir('/{0}') if not uos.stat('/{0}/'+file)[0] & 0x4000]".format(
                        args.dir)
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
                                args.fre = [file for file in file_exists if file.startswith(
                                    start_exp) and file.endswith(end_exp)]
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
                            rsyncio.connect(args)
                            print('Downloading files @ {}...'.format(dev_name))
                            # file_to_get = args.f
                            if args.dir is not None:
                                args.fre = ['/{}/{}'.format(args.dir, file)
                                            for file in files_to_get]
                            else:
                                args.fre = files_to_get
                            result = rsyncio.sync_files(args, dev_name)
                            print('Done!')
                            rsyncio.disconnect()
                        else:
                            if dir == '':
                                dir = '/'
                            print('Files Not found in {}:{} directory'.format(dev_name, dir))
                except KeyboardInterrupt as e:
                    print('KeyboardInterrupt: get Operation Cancelled')
    except DeviceNotFound as e:
        print('ERROR {}'.format(e))

    return
