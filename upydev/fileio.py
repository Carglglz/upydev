
from upydev.wsio import wstool
from upydev.serialio import serialtool
from upydev.bleio import bletool
from upydevice import check_device_type
# from upydevice import Device, DeviceNotFound, DeviceException
# from upydev.helpinfo import see_help
# import sys
# import time
# import os

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


#############################################
def fileio_action(args, **kargs):
    dev_name = kargs.get('device')
    dt = check_device_type(args.t)

    if dt == 'WebSocketDevice':
        wstool(args, dev_name)

    elif dt == 'SerialDevice':
        serialtool(args, dev_name)

    elif dt == 'BleDevice':
        bletool(args, dev_name)
