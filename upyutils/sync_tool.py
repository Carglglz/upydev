#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-09T19:42:05+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-09T23:09:51+01:00

import usocket as socket
import os

buffer_chunk = bytearray(2000)


def connect_SOC(host, port):
    cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc_addr = socket.getaddrinfo(host, port)[0][-1]
    cli_soc.connect(soc_addr)
    return cli_soc


def print_sizefile(path, file_name, tabs=0):
    files = [filename for filename in os.listdir(
        path) if filename == file_name]
    for file in files:
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))


def read_sd_file_sync(file_in_sd, soc):  # for files wrote with new line separator(\n)
    with open(file_in_sd, 'r') as log:
        while True:
            try:
                line = log.readline()
                if line is not '':
                    # in python use 'i'
                    soc.sendall(line[:-1])
                else:
                    print('END OF FILE')
                    # soc.sendall
                    break
            except Exception as e:
                print(e)
                pass


# for files wrote with new line separator(\n)
def read_sd_file_sync_raw(file_in_sd, soc, buff=buffer_chunk):
    # final_file = b''
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
                    print('END OF FILE')
                    # soc.sendall
                    break
            except Exception as e:
                print(e)
                pass
