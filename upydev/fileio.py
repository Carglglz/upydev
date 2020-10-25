
from upydev.wsio import wsfileio
from upydevice import check_device_type
from upydevice import Device, DeviceNotFound, DeviceException
from upydev.helpinfo import see_help
import sys
import time
import os

FILEIO_HELP = """
> FILEIO: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - put : to upload a file to upy device (see -f, -s, -fre, -dir, -rst)
                e.g. $ upydev put myfile.py, $ upydev put cwd, $ upydev put test_*.py

        - get : to download a file from upy device (see -f, -s, -fre, -dir)

        - sync : for a faster transfer of large files
            (this needs sync_tool.py in upy device) (see -f, -s and -lh)

        - d_sync: to recursively sync a folder in upydevice filesystem use -dir
                    to indicate the folder (must be in cwd), use -tree to see dir
                    structure, to sync to an Sd card mounted as 'sd' use -s sd

        - install : install libs to '/lib' path with upip; indicate lib with -f option

        - update_upyutils: to update the latest versions of sync_tool.py, upylog.py,
                        upynotify.py, upysecrets.py, upysh2.py, ssl_repl.py, uping.py, time_it.py,
                        wss_repl.py and wss_helper.py.

"""


def wstool(args, dev_name):
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
            args.s = source + '/'
            # Check if file exists:
            try:
                os.stat(file)[6]
                if args.s:
                    dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                 auth=args.wss)
                    is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                    is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                    dev.disconnect()
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print('Directory {}:{} do NOT exists'.format(dev_name, source))
                            result = False
                    else:
                        if is_dir:
                            print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                            result = wsfileio(args, file, file_in_upy, dev_name)
                else:
                    print('Uploading file {} @ {}...'.format(file_in_upy, dev_name))
                    result = wsfileio(args, file, file_in_upy, dev_name)

                # Reset:
                if result:
                    if args.rst is None:
                        time.sleep(0.1)
                        dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                     auth=args.wss)
                        time.sleep(0.1)
                        dev.reset(reconnect=False)
            except FileNotFoundError as e:
                print('FileNotFoundError:', e)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: put Operation Cancelled')
        else:
            # Handle special cases:
            # CASE [cwd]:
            if args.fre[0] == 'cwd' or args.fre[0] == '.':
                args.fre = [fname for fname in os.listdir('./') if os.path.isfile(fname) and not fname.startswith('.')]
                print('Files in ../{} to put: '.format(os.getcwd().split('/')[-1]))
            else:
                print('Files to put: ')

            files_to_put = []
            for file in args.fre:
                try:
                    filesize = os.stat(file)[6]
                    files_to_put.append(file)
                    print('- {} [{:.2f} KB]'.format(file, filesize/1024))
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
            args.s = source
            try:
                if args.s:
                    dev = Device(args.t, args.p, init=True, ssl=args.wss,
                                 auth=args.wss)
                    is_dir_cmd = "import uos, gc; uos.stat('{}')[0] & 0x4000".format(source)
                    is_dir = dev.cmd(is_dir_cmd, silent=True, rtn_resp=True)
                    dev.disconnect()
                    if dev._traceback.decode() in dev.response:
                        try:
                            raise DeviceException(dev.response)
                        except Exception as e:
                            print(e)
                            print('Directory {}:{} do NOT exists'.format(dev_name, source))
                            result = False
                    else:
                        if is_dir:
                            print('\nUploading files @ {}...\n'.format(dev_name))
                            result = wsfileio(args, 'fre', 'fre', dev_name)
                else:
                    print('\nUploading files @ {}...\n'.format(dev_name))
                    result = wsfileio(args, 'fre', 'fre', dev_name)

                # Reset:
                if result:
                    if args.rst is None:
                        time.sleep(0.1)
                        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                        time.sleep(0.1)
                        dev.reset(reconnect=False)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: put Operation Cancelled')
        sys.exit()
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
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print('Directory {}:{} do NOT exists'.format(dev_name, dir))
                        result = False
                else:
                    if file_exists is True:
                        cmd_str = "import uos; not uos.stat('{}')[0] & 0x4000 ".format(dir + '/' + args.f)
                        is_file = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if file_exists is True and is_file:
                    print('Getting file {} @ {}...'.format(args.f, dev_name))
                    file_to_get = args.f
                    if args.s == 'sd':
                        file_to_get = '/sd/{}'.format(args.f)
                    if args.dir is not None:
                        file_to_get = '/{}/{}'.format(args.dir, args.f)
                    # if not args.wss:
                    #     copyfile_str = 'upytool -p {} {}:{} .{}'.format(
                    #         passwd, target, file_to_get, id_file)
                    result = wsfileio(args, '', file_to_get, dev_name, dev=dev)
                    print('Done!')
                else:
                    if file_exists is False:
                        if dir == '':
                            dir = '/'
                        print('File Not found in {}:{} directory'.format(dev_name, dir))
                    elif file_exists is True:
                        if is_file is not True:
                            print('{}:{} is a directory'.format(dev_name, dir + '/' + args.f))
            except DeviceNotFound as e:
                print('ERROR {}'.format(e))
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
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                file_exists = dev.cmd(cmd_str, silent=True, rtn_resp=True)
                if dev._traceback.decode() in dev.response:
                    try:
                        raise DeviceException(dev.response)
                    except Exception as e:
                        print(e)
                        print('Directory {}:{} do NOT exists'.format(dev_name, dir))
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
                        print('Getting files @ {}...'.format(dev_name))
                        # file_to_get = args.f
                        if args.dir is not None:
                            args.fre = ['/{}/{}'.format(args.dir, file) for file in files_to_get]
                        else:
                            args.fre = files_to_get
                        wsfileio(args, '', '', dev_name, dev=dev)
                        print('Done!')
                    else:
                        if dir == '':
                            dir = '/'
                        print('Files Not found in {}:{} directory'.format(dev_name, dir))
            except DeviceNotFound as e:
                print('ERROR {}'.format(e))
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt: get Operation Cancelled')
        sys.exit()


#############################################
def fileio_action(args, **kargs):
    dev_name = kargs.get('device')
    dt = check_device_type(args.t)

    if dt == 'WebSocketDevice':
        wstool(args, dev_name)
