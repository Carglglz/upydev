#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-09T19:42:05+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-17T04:28:54+00:00

import usocket as socket
import os
import gc
import time

buffer_chunk = bytearray(2000)


def connect_SOC(host, port):
    cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc_addr = socket.getaddrinfo(host, port)[0][-1]
    cli_soc.connect(soc_addr)
    return cli_soc


def print_sizefile(path, file_name, tabs=0, rtl=False):
    files = [filename for filename in os.listdir(
        path) if filename == file_name]
    for file in files:
        try:
            stats = os.stat(path + "/" + file)
        except Exception as e:
            try:
                stats = os.stat(file)
            except Exception as e:
                print('File not found.')
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        _kB = 1000
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f kB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
    if rtl:
        return filesize


def read_sd_file_sync(file_in_sd, soc):  # for files wrote with new line separator(\n)
    with open(file_in_sd, 'r') as log:
        while True:
            try:
                line = log.readline()
                if line is not '':
                    # in python use 'i'
                    soc.sendall(line[:-1])
                else:
                    break
            except Exception as e:
                print(e)
                pass


# for files wrote with new line separator(\n)
def read_sd_file_sync_raw(file_in_sd, soc, buff=buffer_chunk):
    # final_file = b''
    if os.getcwd() == '/sd':
        file_in_sd = file_in_sd.split('/')[-1]
    with open(file_in_sd, 'rb') as log:
        while True:
            try:
                buff[:] = log.read(2000)  # 2 KB
                # print(len(chunk))
                if buff != b'':
                    # in python use 'i'
                    soc.sendall(buff)
                    # final_file += chunk
                else:
                    # print('END OF FILE')
                    # soc.sendall(b'EOF\x8a\xb1\x1a\xcb\x11')
                    # soc.close()
                    gc.collect()
                    break
            except Exception as e:
                print(e)
                pass


def sync_to_filesys(filetoget, host, port, buff=buffer_chunk):
    # final_file = b''
    soc = connect_SOC(host, port)
    soc.settimeout(2)
    with open(filetoget, 'wb') as log:
        pass
    while True:
        try:
            chunk = soc.recv(2000)  # 2 KB
            if chunk != b'':
                with open(filetoget, 'ab') as log:
                    log.write(chunk)
            else:
                print('END OF FILE')
                break
        except Exception as e:
            if e == KeyboardInterrupt:
                break
    gc.collect()
    # soc.close()


def w_stream_writer(host, port, chunk=20000, total=10000000):
    soc = connect_SOC(host, port)
    print('Connected!')
    print('Streaming...\n')
    n_times_chunk = int(total/chunk)
    buff = os.urandom(chunk)
    try:
        for _ in range(n_times_chunk):
            soc.sendall(buff)  # 20 kB
    except Exception as e:
        print(e)
        if e == KeyboardInterrupt:
            print(e)

    time.sleep(0.1)
    print('\nupydevice Done!')
    # soc.close()
    gc.collect()
