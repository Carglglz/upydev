from upydevice import Device, check_device_type, serial_scan, ble_scan, net_scan
import sys
from upydev.helpinfo import see_help
import os
import json
import upydev
from bleak.uuids import uuidstr_to_str
import subprocess
import shlex
import time

UPYDEV_PATH = upydev.__path__[0]

CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'
OK = '\033[92mOK\x1b[0m'
FAIL = '\u001b[31;1mF\u001b[0m'

DEBUGGING_HELP = """
> DEBUGGING: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - ping : pings the target to see if it is reachable, CTRL-C to stop

        - probe: to test if a device is reachable, use -gg flag for global group and -devs
                 to filter which ones.
        - scan: to scan for devices, use with -sr [serial], -nt [network], or -bl [ble],
                if no flag, provided will do all three scans.

        - run : just calls import 'script', where 'script' is indicated by -f option
                (script must be in upydevice or in sd card indicated by -s option
                and the sd card must be already mounted as 'sd');
                * Supports CTRL-C to stop the execution and exits nicely.

        - timeit: to measure execution time of a module/script indicated with -f option.
                  This is an implementation of
                  https://github.com/peterhinch/micropython-samples/tree/master/timed_function

        - diagnose: to make a diagnostic test of the device (sends useful to commands
                    to get device state info), to save report to file see -rep, use -n to save
                    the report with a custom name (automatic name is "upyd_ID_DATETIME.txt")
                    Use "-md local" option if connected to esp AP.

        - errlog: if 'error.log' is present in the upydevice, this shows the content
                    (cat('error.log')), if 'error.log' in sd use -s sd

        - stream_test: to test download speed (from device to host). Default test is 10 MB of
                       random bytes are sent in chunks of 20 kB and received in chunks of 32 kB.
                       To change test parameters use -chunk_tx , -chunk_rx, and -total_size.

        - sysctl : to start/stop a script without following the output. To follow initiate
                   wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl)
                   TO START: use -start [SCRIPT_NAME], TO STOP: use -stop [SCRIPT_NAME]

        - log: to log the output of a upydevice script, indicate script with -f option, and
                the sys.stdout log level and file log level with -dslev and -dflev (defaults
                are debug for sys.stdout and error for file). To log in background use -daemon
                option, then the log will be redirected to a file with level -dslev.
                To stop the 'daemon' log mode use -stopd and indicate script with -f option.
                'Normal' file log and 'Daemon' file log are under .upydev_logs folder in $HOME
                directory, named after the name of the script. To follow an on going 'daemon'
                mode log, use -follow option and indicate the script with -f option.

        - debug: to execute a local script line by line in the target upydevice, use -f option
                to indicate the file. To enter next line press ENTER, to finish PRESS C
                then ENTER. To break a while loop do CTRL+C.

        - pytest: to run upydevice test with pytest, do "pytest-setup" first to enable selection
                 of specific device with -@ entry point.
                 """


def ping(ip):
    ping_cmd_str = 'ping {}'.format(ip)
    ping_cmd = shlex.split(ping_cmd_str)
    try:
        proc = subprocess.Popen(
            ping_cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        while proc.poll() is None:
            print(proc.stdout.readline()[:-1].decode())
    except KeyboardInterrupt:
        time.sleep(1)
        result = proc.stdout.readlines()
        for message in result:
            print(message[:-1].decode())


def run_script(args):
    dir = ''
    script_filepy = args.f
    script_name = script_filepy.split('.')[0]
    reload = "del(sys.modules['{}'])".format(script_name)
    run_cmd = "import {};".format(script_name)
    # print(run_cmd)
    if args.s is not None:
        dir = args.s
        sd_path = "import sys;sys.path.append('/{}')".format(dir)
        run_cmd = "{};import {}".format(sd_path, script_name)

    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print('Running {}...'.format(args.f))
    dev.wr_cmd(run_cmd, follow=True)

    time.sleep(0.2)
    reload_cmd = "import sys,gc;{};gc.collect()".format(reload)
    if args.s is not None:
        reload_syspath = "sys.path.remove('/{}')".format(dir)
        reload_cmd = "{};{};gc.collect()".format(reload, reload_syspath)

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    print('Done!')


def timeit_script(args):
    timeit_import = "from time_it import tzero, tdiff, result;"
    dir = ''
    script_filepy = args.f
    script_name = script_filepy.split('.')[0]
    reload = "del(sys.modules['{}'])".format(script_name)
    timeit_cmd = "t_0 = tzero();import {};diff=tdiff(t_0);result('{}',diff);".format(
        script_name, script_name)
    timeit_final_cmd = timeit_import + timeit_cmd
    if args.s is not None:
        dir = args.s
        sd_path = "import sys;sys.path.append('/{}')".format(dir)
        timeit_final_cmd = "{};{}".format(
            sd_path, timeit_final_cmd)

    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print('Running {}...'.format(args.f))
    dev.wr_cmd(timeit_final_cmd, follow=True)

    time.sleep(0.2)
    reload_cmd = "import sys;{};gc.collect()".format(reload)
    if args.s is not None:
        reload_syspath = "sys.path.remove('/{}')".format(dir)
        reload_cmd = "{};{};gc.collect()".format(reload, reload_syspath)

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    print('Done!')


def probe_device(addr, passwd):
    dt = check_device_type(addr)
    if dt == 'SerialDevice':
        if addr.replace('tty', 'cu') in serial_scan():
            return True
        else:
            return False
    elif dt == 'WebSocketDevice':
        dev = Device(addr, passwd)
        status = dev.is_reachable()
        if status:
            return True
        else:
            return False

    elif dt == 'BleDevice':
        bledevs = ble_scan()
        if bledevs:
            bdev_reachable = False
            for bdev in bledevs:
                if addr == bdev.address:
                    bdev_reachable = True
                    break
            if bdev_reachable:
                return True
            else:
                return False

        else:
            return False


def debugging_action(args, **kargs):
    dev_name = kargs.get('device')

    if args.m == 'probe':
        if args.gg:
            if not args.devs:
                print('Reaching UPY_G group...')
            else:
                print('Reaching : {} ...'.format(', '.join(args.devs)))
            group_file = '{}.config'.format('UPY_G')
            if group_file not in os.listdir(UPYDEV_PATH):
                print('No global group available')
                sys.exit()
            else:
                with open(os.path.join(UPYDEV_PATH, group_file), 'r') as group:
                    group_devs = (json.loads(group.read()))
                print('# UPY_G:')
                if args.devs:
                    group_devs = {k: v for k, v in group_devs.items() if k in args.devs}
                for key in group_devs.keys():
                    dev_add = group_devs[key][0]
                    dev_pass = group_devs[key][1]
                    dev_type = check_device_type(dev_add)
                    if key != list(group_devs.keys())[-1]:
                        tree = '┣━'
                    else:
                        tree = '┗━'
                    is_reachable = probe_device(dev_add, dev_pass)
                    if is_reachable:
                        print('{} {:10} -> {:} @ {:} -> {} {}'.format(tree,
                                                                      key, dev_type,
                                                                      dev_add,
                                                                      OK, CHECK))
                    else:
                        print('{} {:10} -> {:} @ {:} -> {} {}'.format(tree,
                                                                      key, dev_type,
                                                                      dev_add,
                                                                      FAIL, XF))
        else:
            print('Reaching {}...'.format(dev_name))
            is_reachable = probe_device(args.t, args.p)
            dt = check_device_type(args.t)
            if is_reachable:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           OK, CHECK))
            else:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           FAIL, XF))

    elif args.m == 'scan':
        if args.sr:
            print('Serial Scan:')
            devs_dict = serial_scan(debug_info=True)
            if devs_dict:
                print('SerialDevice/s found: {}'.format(len(devs_dict)))
                print('┏{0}━┳━{1}━┳━{2}━┓'.format('━'*40, '━'*40, '━'*30))
                print('┃{0:^40} ┃ {1:^40} ┃ {2:^30} ┃'.format(
                    'PORT', 'DESCRIPTION', 'MANUFACTURER'))
                print('┣{0}━╋━{1}━╋━{2}━┫'.format(
                    '━'*40, '━'*40, '━'*30))
                for dev in devs_dict:
                    desc = devs_dict[dev][0]
                    man = devs_dict[dev][1]
                    if len(desc) > 36:
                        desc = desc[:37]

                    print('┃{0:^40} ┃ {1:^40} ┃ {2:^30} ┃ '.format(dev, desc, man))
                    if dev != list(devs_dict.keys())[-1]:
                        print('┣{0}━╋━{1}━╋━{2}━┫'.format(
                            '━'*40, '━'*40, '━'*30))
                print('┗{0}━┻━{1}━┻━{2}━┛'.format(
                    '━'*40, '━'*40, '━'*30))
            else:
                print('No SerialDevice found')

        elif args.nt:
            print('Local Area Network scan:')
            print('Scanning...')
            devs_list = net_scan(debug_info=True)
            if len(devs_list) == 0:
                print('No WebSocketDevice found')
            else:
                print('WebSocketDevice/s found: {}'.format(len(devs_list)))
                print('┏{0}━┳━{1}━┳━{2}━┓'.format('━'*20, '━'*20, '━'*20))
                print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃'.format(
                    'IP', 'PORT', 'STATUS'))
                print('┣{0}━╋━{1}━╋━{2}━┫'.format(
                    '━'*20, '━'*20, '━'*20))
                for dev in devs_list:
                    ip = dev['host']
                    port = dev['port']
                    status = dev['status']

                    print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ '.format(ip, port, status))
                    if dev != devs_list[-1]:
                        print('┣{0}━╋━{1}━╋━{2}━┫'.format(
                            '━'*20, '━'*20, '━'*20))
                print('┗{0}━┻━{1}━┻━{2}━┛'.format(
                    '━'*20, '━'*20, '━'*20))

        elif args.bl:
            devs = []
            n = 0
            print('Bluetooth Low Energy scan:')
            print('Scanning...')
            while n < 3:
                try:
                    devs = ble_scan()
                    n += 1
                    if len(devs) > 0:
                        break
                    else:
                        print('Scanning...')
                except KeyboardInterrupt:
                    sys.exit()
            if len(devs) == 0:
                print('No BleDevice found')
            else:
                print('BleDevice/s found: {}'.format(len(devs)))
                print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┓'.format(
                    '━'*20, '━'*40, '━'*10, '━'*40))
                print('┃{0:^20} ┃ {1:^40} ┃ {2:^10} ┃ {3:^40} ┃'.format(
                    'NAME', 'UUID', 'RSSI', 'Services'))
                print('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                    '━'*20, '━'*40, '━'*10, '━'*40))
                for dev in devs:
                    services = ['']
                    if hasattr(dev, 'metadata'):
                        if isinstance(dev.metadata, dict):
                            if 'uuids' in dev.metadata.keys():
                                try:
                                    services = [uuidstr_to_str(serv) for serv in dev.metadata['uuids']]
                                except Exception as e:
                                    services = ['']

                    print('┃{0:^20} ┃ {1:^40} ┃ {2:^10} ┃ {3:^40} ┃'.format(dev.name, dev.address,
                                                                 int(dev.rssi), ','.join(services)))
                    if dev != devs[-1]:
                        print('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                            '━'*20, '━'*40, '━'*10, '━'*40))
                print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┛'.format(
                    '━'*20, '━'*40, '━'*10, '━'*40))

    elif args.m == 'ping':
        ping(args.t)

    elif args.m == 'run':
        run_script(args)

    elif args.m == 'timeit':
        timeit_script(args)

    sys.exit()
