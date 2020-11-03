#
# # Do sync , d_sync and backup
# #!/usr/bin/env python
# # @Author: carlosgilgonzalez
# # @Date:   2019-07-09T20:49:15+01:00
# # @Last modified by:   carlosgilgonzalez
# # @Last modified time: 2019-07-13T22:18:43+01:00
#
# import socket
# import time as time_mac
# import os
# import argparse
# import ast
# import netifaces
# import subprocess
# import shlex
# import sys
# from datetime import timedelta
# from upydevice import W_UPYDEVICE
#
#
# parser = argparse.ArgumentParser()
# parser.add_argument("-f", help='file to sync', required=True)
# parser.add_argument("-p", help='password', required=False)
# parser.add_argument("-t", help='target', required=False)
# parser.add_argument("-lh", help='local ip', required=False)
# parser.add_argument("-o", help='output file name', required=False)
# parser.add_argument("-port", help='tcp port', required=False, default=8005, type=int)
# parser.add_argument(
#     "-s", help='source dir to look for in (default '' flash, "sd" for micro sd) ', required=False)
# args = parser.parse_args()
#
# # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# # all interfaces)
#
# # TODO: make get_ip() platform independent
# bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
#
# columns, rows = os.get_terminal_size(0)
# cnt_size = 80
# if columns > cnt_size:
#     bar_size = int((columns - cnt_size))
#     pb = True
# else:
#     bar_size = 1
#     pb = False
#
#
# def do_pg_bar(index, wheel, nb_of_total, speed, time_e, loop_l,
#               percentage, ett, size_bar=bar_size):
#     l_bloc = bloc_progress[loop_l]
#     if index == bar_size:
#         l_bloc = "█"
#     sys.stdout.write("\033[K")
#     print('▏{}▏{:>2}{:>5} % | {} | {:>5} MB/s | {}/{} s'.format("█" *index + l_bloc  + " "*((bar_size+1) - len("█" *index + l_bloc)),
#                                                                     wheel[index % 4],
#                                                                     int((percentage)*100),
#                                                                     nb_of_total, speed,
#                                                                     str(timedelta(seconds=time_e)).split('.')[0][2:],
#                                                                     str(timedelta(seconds=ett)).split('.')[0][2:]), end='\r')
#     sys.stdout.flush()
#
#
# def get_ip():
#     # scanoutput = subprocess.check_output(["ipconfig", "getifaddr", "en0"])
#     # ip = scanoutput.decode('utf-8').split('\n')[0]
#     # ip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
#     # return ip
#     try:
#         ip = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for
#                     iface in netifaces.interfaces() if netifaces.AF_INET in
#                     netifaces.ifaddresses(iface)][-1]
#         return ip
#     except Exception as e:
#         try:
#             ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             ip_soc.connect(('8.8.8.8', 1))
#             local_ip = ip_soc.getsockname()[0]
#             ip_soc.close()
#             return local_ip
#         except Exception as e:
#             return '0.0.0.0'
#
#
# # def do_pg_bar(index, wheel, nb_of_total, speed, time_e, loop_l):
# #     l_bloc = bloc_progress[loop_l]
# #     if index == 80:
# #         l_bloc = "█"
# #     sys.stdout.write("\033[K")
# #     print('▏{:<81}▏{:>5}{:>5} % | DATA: {} | SPEED: {:>5} MB/s | TIME: {} s'.format("█" *index + l_bloc,
# #                                                                     wheel[index % 4],
# #                                                                     int((index/80)*100),
# #                                                                     nb_of_total, speed, str(timedelta(seconds=time_e)).split('.')[0][3:]), end='\r')
# #     sys.stdout.flush()
#
#
# dir = ''
# if args.s is not None:
#     dir = '/sd'
#
# if args.lh is None:
#     local_ip = get_ip()
# if args.lh is not None:
#     local_ip = args.lh
#
# espdev = W_UPYDEVICE(args.t, args.p)
# espdev.open_wconn()
# # sync_cmd = 'upycmd -c "{}" -t {} -p {}'.format(
# #     'import sync_tool as synct', args.t, args.p)
# # espdev.output = None
# # while espdev.output is None:
# espdev.wr_cmd('import sync_tool as synct', silent=True, follow=False)
#
#
# # sync_tool = subprocess.call(sync_cmd, shell=True)
# time_mac.sleep(0.2)
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.bind((local_ip, args.port))
# server_socket.listen(1)
# print('Server listening...')
# sync_connect_cmd = "cli_soc = synct.connect_SOC('{}', {})".format(local_ip, args.port)
# espdev.output = None
# # while espdev.output is None:
# espdev.wr_cmd(sync_connect_cmd, silent=True, follow=False)
# conn, addr = server_socket.accept()
# print('Connection received...')
# conn.settimeout(5)
#
#
# def sync_file_raw(soc, filetoget, dir, espdev=espdev):
#     cmd_filesize_str = "synct.print_sizefile('{}','{}', rtl=True)".format(dir, filetoget)
#     # espdev.output = None
#     # while espdev.output is None:
#     espdev.wr_cmd(cmd_filesize_str, silent=True, follow=False)
#     filesize = espdev.output
#     print('File size: {:>40.2f} kB'.format(filesize/1024))
#     # flushed = 0
#     espdev.close_wconn()
#     # while flushed == 0:
#     #     try:
#     #         conn.recv(128)
#     #     except Exception as e:
#     #         flushed = 1
#     time_mac.sleep(1)
#     sync_tool_cmd = "synct.read_sd_file_sync_raw({},cli_soc)".format("'{}/{}'".format(dir, filetoget))
#     espdev.cmd_nb(sync_tool_cmd)
#     print('Syncing file {} from upy device'.format(filetoget))
#     print('Saving {} file'.format(filetoget))
#     print('Progress:\n')
#     t0 = 0
#     buff = b''
#     wheel = ['|', '/', '-', "\\"]
#     t_start = time_mac.time()
#     EOF = False
#     n_EOF = 1
#     EOF_count = 0
#     if args.o is not None:
#         filetoget = args.o
#     with open(filetoget, 'wb') as log:
#         pass
#     while True:
#         t_0 = time_mac.time()
#         try:
#             chunk = soc.recv(32*(1024))  # 32 KB
#             if chunk != b'':
#                 buff += chunk
#                 loop_index_f = ((len(buff))/filesize)*bar_size
#                 loop_index = int(loop_index_f)
#                 loop_index_l = int(round(loop_index_f-loop_index,1)*6)
#                 nb_of_total = "{:.2f}/{:.2f} MB".format(len(buff)/(1024**2), filesize/(1024**2))
#                 percentage = len(buff)/filesize
#                 tdiff = time_mac.time() - t_0
#                 t_elapsed = time_mac.time() - t_start
#                 t_speed = "{:^2.2f}".format((len(buff)/(1024**2))/t_elapsed)
#                 ett = filesize / (len(buff) / t_elapsed)
#                 if pb:
#                     do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
#                               t_elapsed, loop_index_l, percentage, ett)
#                 else:
#                     sys.stdout.write("Received %d of %d bytes\r" % (len(buff), filesize))
#                     sys.stdout.flush()
#                 # do_pg_bar(loop_index, wheel)
#                 with open(filetoget, 'ab') as log:
#                     log.write(chunk)
#                 if len(buff) == filesize:
#                     EOF = True
#                     break
#             else:
#                 pass
#                 # print('\nEND OF FILE')
#                 # soc.sendall
#                 # final_time = abs(time_mac.time()-t0)
#                 # print('\nDone in {} seconds'.format(round(final_time, 2)))
#                 # break
#             # if t0 == 0:
#             #     t0 = time_mac.time()
#
#             # final_time = abs(time_mac.time()-t_start)
#         except Exception as e:
#             if e == KeyboardInterrupt:
#                 break
#
#             else:
#                 # print(e)
#                 if str(e) == 'timed out':
#                     # print('\nDone in {} seconds'.format(round(final_time, 2)))
#                     # print('Total data received: {:>30.2f} kB'.format(filesize/1024))
#                     break
#     # print(chunk)
#     # print(filesize, len(buff))
#     if not EOF:
#         print('CONNECTION ERROR, TRYING AGAIN...')
#         espdev.cmd_nb(sync_tool_cmd)
#         print('Syncing file {} from upy device'.format(filetoget))
#         print('Saving {} file'.format(filetoget))
#         print('Progress:\n')
#         t0 = 0
#         buff = b''
#         wheel = ['|', '/', '-', "\\"]
#         t_start = time_mac.time()
#         EOF = False
#         n_EOF = 1
#         EOF_count = 0
#         if args.o is not None:
#             filetoget = args.o
#         with open(filetoget, 'wb') as log:
#             pass
#         while True:
#             t_0 = time_mac.time()
#             try:
#                 chunk = soc.recv(32*(1024))  # 32 KB
#                 if chunk != b'':
#                     buff += chunk
#                     loop_index_f = ((len(buff))/filesize)*80
#                     loop_index = int(loop_index_f)
#                     loop_index_l = int(round(loop_index_f-loop_index,1)*6)
#                     nb_of_total = "{:.2f}/{:.2f} MB".format(len(buff)/(1024**2), filesize/(1024**2))
#                     tdiff = time_mac.time() - t_0
#                     t_elapsed = time_mac.time() - t_start
#                     t_speed = "{:^2.2f}".format((len(chunk)/(1024**2))/tdiff)
#                     do_pg_bar(loop_index, wheel, nb_of_total, t_speed, t_elapsed, loop_index_l)
#                     # do_pg_bar(loop_index, wheel)
#                     with open(filetoget, 'ab') as log:
#                         log.write(chunk)
#                     if len(buff) == filesize:
#                         EOF = True
#                         break
#                 else:
#                     pass
#                     # print('\nEND OF FILE')
#                     # soc.sendall
#                     # final_time = abs(time_mac.time()-t0)
#                     # print('\nDone in {} seconds'.format(round(final_time, 2)))
#                     # break
#                 # if t0 == 0:
#                 #     t0 = time_mac.time()
#
#                 # final_time = abs(time_mac.time()-t_start)
#             except Exception as e:
#                 if e == KeyboardInterrupt:
#                     break
#
#                 else:
#                     # print(e)
#                     if str(e) == 'timed out':
#                         # print('\nDone in {} seconds'.format(round(final_time, 2)))
#                         # print('Total data received: {:>30.2f} kB'.format(filesize/1024))
#                         break
#     print('\n\nDone in {} seconds'.format(round(t_elapsed, 2)))
#     print('Total data received: {:>30.2f} kB'.format(filesize/1024))
#
#
# sync_file_raw(conn, args.f, dir)
#
# conn.close()
# espdev.cmd('cli_soc.close()')
# sys.exit()
#
#
# def sync(ip, passwd, id_file=None, PORT=8005, resp=None, getfilelist=True):
#     if getfilelist:
#         espdev = W_UPYDEVICE(ip, passwd)
#         espdev.open_wconn()
#         if args.s is None:
#             print('Looking for file in upy device root dir')
#             cmd_str = "'{}' in uos.listdir()".format(args.f)
#             dir = 'root'
#         if args.s == 'sd':
#             print('Looking in SD memory...')
#             cmd_str = "'{}' in uos.listdir('/sd')".format(args.f)
#             dir = '/sd'
#         if getfilelist:
#             if dir == '/sd':
#                 while espdev.output is None:
#                     espdev.wr_cmd("'sd' in uos.listdir()", silent=True, follow=False)
#                 if espdev.output is True:
#                     print('Found SD memory...')
#                 else:
#                     print('SD not mounted, try to mount it first')
#                     sys.exit()
#             espdev.output = None
#             while espdev.output is None:
#                 espdev.wr_cmd(cmd_str, silent=True, follow=False)
#             found_file = espdev.output
#             espdev.close_wconn()
#
#     try:
#         if resp is not None:
#             found_file = True
#         if found_file is True:
#             target = ip
#             print('Getting file {}...'.format(args.f))
#             file_to_get = args.f
#             copyfile = 'sync_server -f {} -t {} -p {} -port {}'.format(
#                 file_to_get, target, passwd, PORT)
#             if id_file is not None:
#                 copyfile = 'sync_server -f {} -t {} -p {} -o {} -port {}'.format(
#                     file_to_get, target, passwd, id_file, PORT)
#             if args.lh is not None:
#                 copyfile = 'sync_server -f {} -t {} -p {} -lh {} -port {}'.format(
#                     file_to_get, target, passwd, args.lh, PORT)
#                 if id_file is not None:
#                     copyfile = 'sync_server -f {} -t {} -p {} -lh {} -o {} -port {}'.format(
#                         file_to_get, target, passwd, args.lh, id_file, PORT)
#             if args.s == 'sd':
#                 copyfile = 'sync_server -f {} -t {} -p {} -s {} -port {}'.format(
#                     file_to_get, target, passwd, 'sd', PORT)
#                 if id_file is not None:
#                     copyfile = 'sync_server -f {} -t {} -p {} -s {} -o {} -port {}'.format(
#                         file_to_get, target, passwd, 'sd', id_file, PORT)
#                 if args.lh is not None:
#                     copyfile = 'sync_server -f {} -t {} -p {} -s {} -lh {} -port {}'.format(
#                         file_to_get, target, passwd, 'sd', args.lh, PORT)
#                     if id_file is not None:
#                         copyfile = 'sync_server -f {} -t {} -p {} -s {} -lh {} -o {} -port {}'.format(
#                             file_to_get, target, passwd, 'sd', args.lh, id_file, PORT)
#
#             # resp = run_command_rt(copyfile)
#             copyfile_cmd = shlex.split(copyfile)
#             subprocess.call(copyfile_cmd)
#             # try:
#             #     proc = subprocess.Popen(
#             #         copyfile_cmd, stdout=subprocess.PIPE,
#             #         stderr=subprocess.STDOUT)
#             #     while proc.poll() is None:
#             #         print(proc.stdout.readline()[:-1].decode())
#             # except KeyboardInterrupt:
#             #     time.sleep(1)
#             #     result = proc.stdout.readlines()
#             #     for message in result:
#             #         print(message[:-1].decode())
#         else:
#             if dir == 'root':
#                 print('File Not found in upy device {} directory'.format(dir))
#             if dir == '/sd':
#                 print(
#                     'File Not found in upy device {} directory or sd unmounted'.format(dir))
#
#     except Exception as e:
#         print(e)
#         pass
#
#
# def sync_multiple_f(ip, passwd, id_file_dev=None, device=None, PORT_M=8005):
#     # case 1: -fre is current working directory (cwd)
#     file_list = ast.literal_eval(get_files_list(ip, passwd))
#     if args.fre[0] == 'cwd':
#         print('Files in upy device cwd to get:')
#         for file in file_list:
#             print(file)
#         for file in file_list:
#             args.f = file
#             if id_file_dev is not None:
#                 id_file_dev = '{}_{}'.format(device, args.f)
#             sync(ip, passwd, id_file=id_file_dev, PORT=PORT_M, resp=file_list,
#                  getfilelist=False)
#             print('\n')
#     else:
#         # case 2: -fre is an expression to match
#         if len(args.fre) == 1:
#             print("Files in that match expression '{}' to get:".format(
#                 args.fre[0]))
#             for file in [fl for fl in file_list if args.fre[0] in fl]:
#                 print(file)
#             for file in [fl for fl in file_list if args.fre[0] in fl]:
#                 args.f = file
#                 if id_file_dev is not None:
#                     id_file_dev = '{}_{}'.format(device, args.f)
#                 sync(ip, passwd, id_file=id_file_dev, PORT=PORT_M,
#                      resp=file_list, getfilelist=False)
#                 print('\n')
#         else:
#             # case 3: -fre is a list of files
#             print('Files to get:')
#             for file in args.fre:
#                 print(file)
#             for file in args.fre:
#                 args.f = file
#                 if id_file_dev is not None:
#                     id_file_dev = '{}_{}'.format(device, args.f)
#                 sync(ip, passwd, id_file=id_file_dev, PORT=PORT_M,
#                      resp=file_list, getfilelist=False)
#                 print('\n')
