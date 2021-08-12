
from upydev.wsio import wstool, WebSocketFileIO
from upydev.serialio import serialtool, SerialFileIO
from upydev.bleio import bletool, BleFileIO
from upydev.rsyncio import synctool
from upydev.dsyncio import d_sync_recursive, check_wdlog, dev2host_sync_recursive
from upydev.helpinfo import see_help
from upydevice import check_device_type, Device
import upydev
import os
import sys

FILEIO_HELP = """
> FILEIO: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - put: to upload a file to upy device (see -f, -s, -fre, -dir, -rst, -wdl, -gf)
                e.g. $ upydev put myfile.py, $ upydev put cwd, $ upydev put test_*.py

        - get: to download a file from upy device (see -f, -s, -fre, -dir, -gf)

        - fget: for a faster transfer of large files
            (this needs sync_tool.py in upy device) (see -f, -s, -lh, -wdl, -gf)

        - dsync: to recursively sync a folder in upydevice filesystem
                 where second arg is the directory (can be current working directory too '.',
                 Otherwise use -dir to indicate the folder (must be in cwd).
                 To sync to an Sd card mounted as 'sd' use -s sd.
                 Use -rf to remove files or directories deleted in local dir.
                 Use -d flag to sync from device to host.
                 Use -wdl flag to sync only modified files.

        - rsync: same as "dsync [DIR] -rf -wdl". To recursively sync only modified files.
                 (deleting files too)

        - backup: same as "dsync . -d" to make a backup of the device filesystem.

        - install : install libs to '/lib' path with upip; indicate lib with -f option

        - update_upyutils: to update the latest versions of sync_tool.py, upylog.py,
                        upynotify.py, upysecrets.py, upysh2.py, ssl_repl.py, uping.py, time_it.py,
                        wss_repl.py and wss_helper.py.

"""


def install_w_upip(args, dt, dev_name):
    if args.f is None:
        see_help(args.m)
        sys.exit()
    else:
        dev = Device(args.t, args.p, init=True, ssl=args.wss,
                     auth=args.wss)
        if dt == 'WebSocketDevice':
            print('Installing {} in {} ...'.format(args.f, dev_name))
            dev.wr_cmd("import upip;upip.install('{}');True".format(args.f),
                       silent=True, long_string=True)
            if 'Error' not in dev.response:
                print(dev.response.replace('(\x02ng', 'Installing').replace('True\n', ''),
                      end='')
                result = dev.cmd('_', silent=True, rtn_resp=True)
                if result:
                    print('Done!')
            else:
                print(dev.response.replace('True\n', ''), end='')
            dev.disconnect()
            return

        elif dt == 'SerialDevice':
            sdevIO = SerialFileIO(dev)
            sdevIO.upip_install(args, dev_name)

        elif dt == 'BleDevice':
            bledevIO = BleFileIO(dev)
            bledevIO.upip_install(args, dev_name)

        dev.disconnect()
    return


def update_upyutils(args, dt, dev_name):
    print('Updating device upyutils...')
    utils_dir = os.path.join(upydev.__path__[0], 'upyutils_dir')
    args.m = 'put'
    args.fre = [os.path.join(utils_dir, util) for util in os.listdir(utils_dir)
                if util.endswith('.py')]
    args.dir = 'lib'
    if dt == 'WebSocketDevice':
        wstool(args, dev_name)

    elif dt == 'SerialDevice':
        serialtool(args, dev_name)

    elif dt == 'BleDevice':
        bletool(args, dev_name)


#############################################
def fileio_action(args, **kargs):
    dev_name = kargs.get('device')
    dt = check_device_type(args.t)
    if args.m == 'put' or args.m == 'get':
        if args.wdl and args.m == 'put':
            modified_files, deleted_files = check_wdlog(save_wdlog=True)
            args.fre = modified_files
            if not args.fre:
                # sys.exit()
                return
        if dt == 'WebSocketDevice':
            wstool(args, dev_name)

        elif dt == 'SerialDevice':
            serialtool(args, dev_name)

        elif dt == 'BleDevice':
            bletool(args, dev_name)
    elif args.m == 'update_upyutils':
        update_upyutils(args, dt, dev_name)

    elif args.m == 'install':
        install_w_upip(args, dt, dev_name)

    elif args.m == 'fget':
        if dt == 'WebSocketDevice':
            synctool(args, dev_name)
        else:
            print('Use "get" instead')
    elif args.m == 'dsync' or args.m == 'backup' or args.m == 'rsync':
        if args.m == 'backup':
            args.d = True
            args.f = '.'
        if args.m == 'rsync':
            args.rf = True
            args.wdl = True
        dir_lib = args.f
        dev_lib = args.dir
        dev = Device(args.t, args.p, init=True, ssl=args.wss,
                     auth=args.wss)
        dev.wr_cmd('import os')
        if not dev_lib:
            dev_lib = "./"
        dev_to_host = args.d
        if dt == 'WebSocketDevice':
            wsdevIO = WebSocketFileIO(dev, args, devname=dev_name)
            # print('Syncing @ {} '.format(dev_name), end='\n\n')
            if not dev_to_host:
                print('Syncing to @ {} '.format(dev_name), end='\n\n')
                d_sync_recursive(dir_lib, devIO=wsdevIO,
                                 show_tree=True, rootdir=dev_lib,
                                 root_sync_folder=dir_lib,
                                 args=args,
                                 dev_name=dev_name)
            else:
                print('Syncing from @ {} '.format(dev_name), end='\n\n')
                dev2host_sync_recursive(dir_lib, devIO=wsdevIO,
                                        show_tree=True, rootdir=dev_lib,
                                        root_sync_folder=dir_lib,
                                        args=args,
                                        dev_name=dev_name)
        elif dt == 'SerialDevice':
            sdevIO = SerialFileIO(dev)
            # print('Syncing @ {} '.format(dev_name), end='\n\n')
            if not dev_to_host:
                print('Syncing to @ {} '.format(dev_name), end='\n\n')
                d_sync_recursive(dir_lib, devIO=sdevIO,
                                 show_tree=True,
                                 rootdir=dev_lib,
                                 root_sync_folder=dir_lib,
                                 args=args,
                                 dev_name=dev_name)
            else:
                print('Syncing from @ {} '.format(dev_name), end='\n\n')
                dev2host_sync_recursive(dir_lib, devIO=sdevIO,
                                        show_tree=True,
                                        rootdir=dev_lib,
                                        root_sync_folder=dir_lib,
                                        args=args,
                                        dev_name=dev_name)

        elif dt == 'BleDevice':
            bledevIO = BleFileIO(dev)
            # print('Syncing @ {} '.format(dev_name), end='\n\n')
            if not dev_to_host:
                print('Syncing to @ {} '.format(dev_name), end='\n\n')
                d_sync_recursive(dir_lib, devIO=bledevIO,
                                 show_tree=True,
                                 rootdir=dev_lib,
                                 root_sync_folder=dir_lib,
                                 args=args,
                                 dev_name=dev_name)
            else:
                print('Syncing from @ {} '.format(dev_name), end='\n\n')
                dev2host_sync_recursive(dir_lib, devIO=bledevIO,
                                        show_tree=True,
                                        rootdir=dev_lib,
                                        root_sync_folder=dir_lib,
                                        args=args,
                                        dev_name=dev_name)
