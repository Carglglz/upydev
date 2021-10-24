from upydevice import Device, check_device_type, serial_scan, ble_scan, net_scan
import sys
from upydev.helpinfo import see_help
from upydev.firmwaretools import get_fw_versions
from upydev.gencommands import print_filesys_info, print_sizefile_all
from upydev.commandlib import _CMDDICT_
import os
import json
import upydev
from bleak.uuids import uuidstr_to_str
import subprocess
import shlex
import time
import socket
from datetime import timedelta, datetime
import netifaces
import logging
import shutil
import signal
from binascii import hexlify
import nmap

UPYDEV_PATH = upydev.__path__[0]

CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'
OK = '\033[92mOK\x1b[0m'
FAIL = '\u001b[31;1mF\u001b[0m'

# TERMINAL SIZE
bloc_progress = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
columns, rows = os.get_terminal_size(0)
cnt_size = 75
if columns > cnt_size:
    bar_size = int((columns - cnt_size))
    pb = True
else:
    bar_size = 1
    pb = False

AUTHMODE_DICT = {0: 'NONE', 1: 'WEP', 2: 'WPA PSK', 3: 'WPA2 PSK',
                    4: 'WPA/WAP2 PSK'}

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


def sortSecond(val):
    return val[1]


def _dt_format(number):
        rtc_n = str(number)
        if len(rtc_n) == 1:
            rtc_n = "0{}".format(rtc_n)
            return rtc_n
        else:
            return rtc_n


def _ft_datetime(t_now):
    return([_dt_format(i) for i in t_now])


def print_sizefile(file_name, filesize, tabs=0):
    _kB = 1024
    if filesize < _kB:
        sizestr = str(filesize) + " by"
    elif filesize < _kB**2:
        sizestr = "%0.1f KB" % (filesize / _kB)
    elif filesize < _kB**3:
        sizestr = "%0.1f MB" % (filesize / _kB**2)
    else:
        sizestr = "%0.1f GB" % (filesize / _kB**3)

    prettyprintname = ""
    for _ in range(tabs):
        prettyprintname += "   "
    prettyprintname += file_name
    print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))


def get_cmd(raw):
    shcmd = shlex.split(raw)
    output = subprocess.check_output(shcmd).decode()
    return output


def stop_by_pid(raw='ps ax', proc_name='upydev log'):  # upydev log, web_repl_cmd_r
    shcmd = shlex.split(raw)
    output = subprocess.check_output(shcmd).decode()
    pline = [line for line in output.split('\n') if proc_name in line]
    if len(pline) > 0:
        pid = pline[0].strip().split(' ')[0]
        k = get_cmd('kill {}'.format(pid))
        return 'Daemon process {} with PID: {} stopped'.format(proc_name, pid)
    else:
        return('NO DAEMON PROCESS FOUND')


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


def ping_diagnose(ip, rep_file=None):
    ping_cmd_str = 'ping -c 5 {}'.format(ip)
    ping_cmd = shlex.split(ping_cmd_str)
    timeouts = 0
    try:
        proc = subprocess.Popen(
            ping_cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        while proc.poll() is None:
            resp = proc.stdout.readline()[:-1].decode()
            print(resp)
            if 'timeout' in resp:
                timeouts += 1
            if rep_file is not None:
                rep_file.append(resp)

        time.sleep(1)
        result = proc.stdout.readlines()
        for message in result:
            print(message[:-1].decode())
            rep_file.append(message[:-1].decode())

    except KeyboardInterrupt:
        time.sleep(1)
        result = proc.stdout.readlines()
        for message in result:
            print(message[:-1].decode())

    if timeouts >= 3:
        print('DEVICE IS DOWN OR SIGNAL RSSI IS TO LOW')
        print('WIRELESS DIAGNOSTICS NOT POSSIBLE, PLEASE RESET THE DEVICE OR PLACE IT NEARER TO THE LOCAL AP')
        return False
    else:
        return True


def diagnose(args):
    t0 = time.time()
    save_rep = args.rep
    if args.rst is None:
        args.rst = True
    else:
        args.rst = False
    local = False
    if args.apmd:
        local = True
    vers = upydev.version
    name_rep = args.n

    FILE_REPORT = []
    # FULL REPORT TEST
    print('{:<10} {} {:>10}'.format('*'*20, 'uPydev Diagnostics Test', '*'*20))
    FILE_REPORT.append('{:<10} {} {:>10}'.format(
        '*'*20, 'uPydev Diagnostics Test', '*'*20))
    print('\n')
    FILE_REPORT.append('\n')
    print('upydev version : {}'.format(vers))
    FILE_REPORT.append('upydev version : {}'.format(vers))
    # CHECK IF DEVICE IS REACHABLE
    print('\n')
    FILE_REPORT.append('\n')
    print('{:<10} {} {:>10}'.format('='*20, 'PING TEST', '='*20))
    FILE_REPORT.append('{:<10} {} {:>10}'.format('='*20, 'PING TEST', '='*20))
    device_is_on = ping_diagnose(args.t, rep_file=FILE_REPORT)
    print('\n')
    FILE_REPORT.append('\n')
    # CHECK IF PORT 8266 IS OPEN(WEBREPL)
    host_range = args.t
    nmScan = nmap.PortScanner()
    print('{:<10} {} {:>10}'.format('='*20, 'NMAP TEST', '='*20))
    FILE_REPORT.append('{:<10} {} {:>10}'.format('='*20, 'NMAP TEST', '='*20))
    print('\n')
    FILE_REPORT.append('\n')
    n_tries = 0
    while n_tries < 3:
        my_scan = nmScan.scan(hosts=host_range, arguments='-p 8266 -Pn')
        hosts_list = [{'host': x, 'state': nmScan[x]['status']['state'], 'port': list(
            nmScan[x]['tcp'].keys())[0], 'status':nmScan[x]['tcp'][8266]['state']} for x in nmScan.all_hosts()]
        devs = [host for host in hosts_list if host['status'] == 'open']
        if len(devs) > 0:
            n_tries = 3
            print('DEVICE FOUND')
            FILE_REPORT.append('DEVICE FOUND')
            N = 1
            for dev in devs:
                try:
                    print('DEVICE {}: , IP: {} , STATE: {}, PORT: {}, STATUS: {}'.format(
                        N, dev['host'], dev['state'], dev['port'], dev['status']))
                    FILE_REPORT.append('DEVICE {}: , IP: {} , STATE: {}, PORT: {}, STATUS: {}'.format(
                        N, dev['host'], dev['state'], dev['port'], dev['status']))
                    N += 1
                except Exception as e:
                    pass
        else:
            if n_tries >= 2:
                print('DEVICE NOT FOUND')
                FILE_REPORT.append('DEVICE NOT FOUND')
                n_tries += 1
            else:
                n_tries += 1
    # ISSUE A KBI
    if device_is_on:
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss,
                     autodetect=True)
        # dev.kbi()
        glo_vars = dev.cmd('dir()', silent=True, rtn_resp=True)
        # ID
        print('\n')
        FILE_REPORT.append('\n')
        print('{:<10} {} {:>10}'.format('='*10, 'MACHINE ID', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'MACHINE ID', '='*10))
        uid = dev.cmd(_CMDDICT_['UID'], silent=True, rtn_resp=True)
        print('\n')
        FILE_REPORT.append('\n')
        print("ID: {}".format(uid.decode()))
        upy_id = uid.decode()
        FILE_REPORT.append("ID: {}".format(uid.decode()))
        print('\n')
        FILE_REPORT.append('\n')
        # UNAME
        print('{:<10} {} {:>10}'.format('='*10, 'DEVICE INFO', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'DEVICE INFO', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        info_dev = str(dev)
        print(info_dev)
        FILE_REPORT.append(info_dev)
        print('\n')
        FILE_REPORT.append('\n')
        # CHECK AVAILABLE FIRMWARE
        if not local:
            print('{:<10} {} {:>10}'.format(
                '='*10, 'AVAILABLE FIRMWARE', '='*10))
            FILE_REPORT.append('{:<10} {} {:>10}'.format(
                '='*10, 'AVAILABLE FIRMWARE', '='*10))
            print('\n')
            FILE_REPORT.append('\n')
            print('Available firmware found for {}'.format(dev.dev_platform))
            FILE_REPORT.append(
                'Available firmware found for {}'.format(dev.dev_platform))
            for vers in get_fw_versions(dev.dev_platform)[1]:
                print('  - {}'.format(vers))
                FILE_REPORT.append('  - {}'.format(vers))
            print('\n')
            FILE_REPORT.append('\n')
        # RAM MEM
        print('{:<10} {} {:>10}'.format('='*10, 'RAM', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format('='*10, 'RAM', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        RAM = dev.cmd(_CMDDICT_['MEM'], silent=True, rtn_resp=True,
                      long_string=True)
        mem_info = RAM.splitlines()[1]
        mem = {elem.strip().split(':')[0]: int(elem.strip().split(':')[
                          1]) for elem in mem_info[4:].split(',')}
        print("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}".format(*['Memory',
                                                            'Size', 'Used',
                                                            'Avail',
                                                            'Use%']))
        FILE_REPORT.append("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}".format(*['Memory',
                                                                         'Size', 'Used',
                                                                         'Avail',
                                                                         'Use%']))
        total_mem = mem['total']/1024
        used_mem = mem['used']/1024
        free_mem = mem['free']/1024
        total_mem_s = "{:.3f} KB".format(total_mem)
        used_mem_s = "{:.3f} KB".format(used_mem)
        free_mem_s = "{:.3f} KB".format(free_mem)

        print('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}'.format('RAM', total_mem_s,
                                                         used_mem_s, free_mem_s,
                                                         "{:.1f} %".format((used_mem/total_mem)*100)))
        FILE_REPORT.append('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}'.format('RAM', total_mem_s,
                                                                      used_mem_s, free_mem_s,
                                                                      "{:.1f} %".format((used_mem/total_mem)*100)))

        print('\n')
        FILE_REPORT.append('\n')
        # DIR()
        print('{:<10} {} {:>10}'.format(
            '='*10, 'GLOBAL SPACE VARIABLES', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'GLOBAL SPACE VARIABLES', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        print(glo_vars)
        FILE_REPORT.append(glo_vars)
        print('\n')
        FILE_REPORT.append('\n')
        # FLASH MEM
        print('{:<10} {} {:>10}'.format('='*10, 'FLASH MEMORY', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'FLASH MEMORY', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        cmd_str = _CMDDICT_['STAT_FS'].format('')
        resp = dev.cmd(cmd_str, silent=True, rtn_resp=True)
        size_info = resp
        total_b = size_info[0] * size_info[2]
        used_b = (size_info[0] * size_info[2]) - (size_info[0] * size_info[3])
        total_mem = print_filesys_info(total_b)
        free_mem = print_filesys_info(size_info[0] * size_info[3])
        used_mem = print_filesys_info(used_b)
        filesys = 'Flash'
        if filesys == 'Flash':
            mounted_on = '/'
        else:
            mounted_on = filesys
        print("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}{5:^12}".format(*['Filesystem',
                                                                   'Size', 'Used',
                                                                   'Avail',
                                                                   'Use%', 'Mounted on']))
        FILE_REPORT.append("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}{5:^12}".format(*['Filesystem',
                                                                                'Size', 'Used',
                                                                                'Avail',
                                                                                'Use%', 'Mounted on']))
        print('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}{5:>5}{6:12}'.format(filesys, total_mem,
                                                                     used_mem, free_mem,
                                                                     "{:.1f} %".format((used_b/total_b)*100), ' ', mounted_on))
        FILE_REPORT.append('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}{5:>5}{6:12}'.format(filesys, total_mem,
                                                                                  used_mem, free_mem,
                                                                                  "{:.1f} %".format((used_b/total_b)*100), ' ', mounted_on))
        print('\n')
        FILE_REPORT.append('\n')

        ld = dev.cmd("import uos;uos.listdir('/')", silent=True, rtn_resp=True)
        if 'sd' in ld:
            sd_ismounted = True
            cmd_str = _CMDDICT_['STAT_FS'].format('sd')
            resp = dev.cmd(cmd_str, silent=True, rtn_resp=True)
            size_info = resp
            total_b = size_info[0] * size_info[2]
            used_b = (size_info[0] * size_info[2]) - (size_info[0] * size_info[3])
            total_mem = print_filesys_info(total_b)
            free_mem = print_filesys_info(size_info[0] * size_info[3])
            used_mem = print_filesys_info(used_b)
            filesys = 'sd'
            mounted_on = '/sd'
            print("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}{5:^12}".format(*['Filesystem',
                                                                       'Size', 'Used',
                                                                       'Avail',
                                                                       'Use%', 'Mounted on']))
            FILE_REPORT.append("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}{5:^12}".format(*['Filesystem',
                                                                                    'Size', 'Used',
                                                                                    'Avail',
                                                                                    'Use%', 'Mounted on']))
            print('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}{5:>5}{6:12}'.format(filesys, total_mem,
                                                                         used_mem, free_mem,
                                                                         "{:.1f} %".format((used_b/total_b)*100), ' ', mounted_on))
            FILE_REPORT.append('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}{5:>5}{6:12}'.format(filesys, total_mem,
                                                                                      used_mem, free_mem,
                                                                                      "{:.1f} %".format((used_b/total_b)*100), ' ', mounted_on))
            print('\n')
            FILE_REPORT.append('\n')
        else:
            sd_ismounted = False
            print('SD NOT FOUND')
            FILE_REPORT.append('SD NOT FOUND')
        # FILES IN FLASH + SIZE
        print('{:<10} {} {:>10}'.format(
            '='*10, 'Files in FLASH MEMORY', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'Files in FLASH MEMORY', '='*10))
        print('\n')
        FILE_REPORT.append('\n')

        du = dev.cmd("[(filename,uos.stat(''+str(filename))[6]) for filename in uos.listdir('')]",
                     silent=True, rtn_resp=True)
        filesize = du
        filesize.sort(key=sortSecond, reverse=True)
        print('Files in FLASH MEMORY:')
        FILE_REPORT.append('Files in FLASH MEMORY:')
        print_sizefile_all(filesize, frep=FILE_REPORT)
        print('\n')
        FILE_REPORT.append('\n')
        # MODULES
        print('{:<10} {} {:>10}'.format(
            '='*10, 'Frozen Modules in Firmware', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'Frozen Modules in Firmware', '='*10))
        print('\n')
        FILE_REPORT.append('\n')

        umodules = dev.cmd("help('modules')", silent=True, long_string=True,
                           rtn_resp=True)
        print(umodules)
        FILE_REPORT.append(umodules)
        print('\n')
        FILE_REPORT.append('\n')
        # /LIB
        print('{:<10} {} {:>10}'.format('='*10, 'Modules in /lib', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'Modules in /lib', '='*10))
        print('\n')
        FILE_REPORT.append('\n')

        lib = dev.cmd("import uos; uos.listdir('/lib')", silent=True, rtn_resp=True)
        for flib in lib:
            print(flib)
            FILE_REPORT.append(flib)
        print('\n')
        FILE_REPORT.append('\n')
        print('{:<10} {} {:>10}'.format(
            '='*10, 'Modules/scripts in /', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'Modules/scripts in /', '='*10))
        print('\n')
        FILE_REPORT.append('\n')

        pyfs = dev.cmd("import uos; uos.listdir('/')", silent=True, rtn_resp=True)
        pyfiles = [pyf for pyf in pyfs if '.py' in pyf]
        for pyf in pyfiles:
            print(pyf)
            FILE_REPORT.append(pyf)

        print('\n')
        FILE_REPORT.append('\n')

        # I2C SCAN (config option)
        print('{:<10} {} {:>10}'.format('='*10, 'I2C SCAN', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'I2C SCAN', '='*10))
        i2c_scl = "22"
        i2c_sda = "23"
        if dev.dev_platform == 'esp8266':
            i2c_scl = "5"
            i2c_sda = "4"
        i2c_cmd = "from machine import I2C,Pin;i2c = I2C(scl=Pin({}),sda=Pin({}));i2c.scan();gc.collect()".format(
            i2c_scl, i2c_sda)
        print('\n')
        FILE_REPORT.append('\n')

        i2c_scan = dev.cmd(i2c_cmd, silent=True, rtn_resp=True)
        print('Found {} i2c devices'.format(len(i2c_scan)))
        FILE_REPORT.append('Found {} i2c devices'.format(len(i2c_scan)))
        print('DEC: ')
        FILE_REPORT.append('DEC: ')
        print(i2c_scan)
        FILE_REPORT.append(i2c_scan)
        print('HEX:')
        FILE_REPORT.append('HEX:')
        print([hex(val) for val in i2c_scan])
        FILE_REPORT.append([hex(val) for val in i2c_scan])

        print('\n')
        FILE_REPORT.append('\n')
        # RTC CHECK LOCAL TIME - HOST TIME DIFF
        print('{:<10} {} {:>10}'.format('='*10, 'RTC DATETIME CHECK', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'RTC DATETIME CHECK', '='*10))
        get_time_cmd = "import time;tnow = time.localtime();"
        get_time2_cmd = "[tnow[0],tnow[1],tnow[2],tnow[3],tnow[4],tnow[5]];gc.collect()"
        get_datetime_cmd = get_time_cmd + get_time2_cmd
        devtime = dev.cmd(get_datetime_cmd, silent=True, rtn_resp=True)
        localtime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        print('\n')
        FILE_REPORT.append('\n')
        devicetime = "{}-{}-{}T{}:{}:{}".format(*_ft_datetime(devtime))
        print('{:<15} :  {:^15}'.format('Device DateTime', devicetime))
        FILE_REPORT.append('{:<15} :  {:^15}'.format(
            'Device DateTime', devicetime))
        print('{:<15} :  {:^15}'.format('Local DateTime', localtime))
        FILE_REPORT.append('{:<15} :  {:^15}'.format(
            'Local DateTime', localtime))
        print('\n')
        FILE_REPORT.append('\n')
        # IF NETWORK:
        is_conn_cmd = 'import network; network.WLAN(network.STA_IF).isconnected()'

        devconn = dev.cmd(is_conn_cmd, silent=True, rtn_resp=True)
        is_connected = devconn
        print('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK STA IF CONFIG', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK STA IF CONFIG', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        if is_connected:
            net_info_list = dev.cmd(_CMDDICT_['NET_INFO'], silent=True,
                                    rtn_resp=True)
            if len(net_info_list) > 0:
                vals = hexlify(net_info_list[2]).decode()
                bssid = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
                print('IF CONFIG:')
                print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┳━{4}━┳━{5}━┳━{6}━┓'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                print('┃{0:^15} ┃ {1:^15} ┃ {2:^15} ┃ {3:^15} ┃ {4:^15} ┃ {5:^20} ┃ {6:^10} ┃'.format(
                                'IP', 'SUBNET', 'GATEAWAY', 'DNS', 'SSID', 'BSSID',
                                'RSSI'))
                print('┣{0}━╋━{1}━╋━{2}━╋━{3}━╋━{4}━╋━{5}━╋━{6}━┫'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                try:
                    print('┃{0:^15} ┃ {1:^15} ┃ {2:^15} ┃ {3:^15} ┃ {4:^15} ┃ {5:^20} ┃ {6:^10} ┃'.format(
                        *net_info_list[0], net_info_list[1],
                        bssid, net_info_list[3]))
                    print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┻━{4}━┻━{5}━┻━{6}━┛'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                except Exception as e:
                    print(e)

                FILE_REPORT.append('IF CONFIG:')
                FILE_REPORT.append('┏{0}━┳━{1}━┳━{2}━┳━{3}━┳━{4}━┳━{5}━┳━{6}━┓'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                FILE_REPORT.append('┃{0:^15} ┃ {1:^15} ┃ {2:^15} ┃ {3:^15} ┃ {4:^15} ┃ {5:^20} ┃ {6:^10} ┃'.format(
                                'IP', 'SUBNET', 'GATEAWAY', 'DNS', 'SSID', 'BSSID',
                                'RSSI'))
                FILE_REPORT.append('┣{0}━╋━{1}━╋━{2}━╋━{3}━╋━{4}━╋━{5}━╋━{6}━┫'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                try:
                    FILE_REPORT.append('┃{0:^15} ┃ {1:^15} ┃ {2:^15} ┃ {3:^15} ┃ {4:^15} ┃ {5:^20} ┃ {6:^10} ┃'.format(
                        *net_info_list[0], net_info_list[1],
                        bssid, net_info_list[3]))
                    FILE_REPORT.append('┗{0}━┻━{1}━┻━{2}━┻━{3}━┻━{4}━┻━{5}━┻━{6}━┛'.format(
                                '━'*15, '━'*15, '━'*15, '━'*15, '━'*15, '━'*20,
                                '━'*10))
                except Exception as e:
                    FILE_REPORT.append(e)
        else:
            print('STA NOT CONNECTED')
            FILE_REPORT.append('STA NOT CONNECTED')
        # STA (NETSCAN)
        print('\n')
        FILE_REPORT.append('\n')
        print('{:<10} {} {:>10}'.format('='*10, 'NETWORK STA SCAN', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK STA SCAN', '='*10))
        print('\n')
        FILE_REPORT.append('\n')

        net_scan_list = dev.cmd(_CMDDICT_['NET_SCAN'], silent=True, rtn_resp=True)
        print('=' * 110)
        FILE_REPORT.append('=' * 110)
        print('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
            'ESSID', 'BSSID', 'CHANNEL', 'RSSI (dB)', 'AUTHMODE', 'HIDDEN'))
        FILE_REPORT.append('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
            'ESSID', 'BSSID', 'CHANNEL', 'RSSI (dB)', 'AUTHMODE', 'HIDDEN'))
        print('=' * 110)
        FILE_REPORT.append('=' * 110)
        for netscan in net_scan_list:
            auth = AUTHMODE_DICT[netscan[4]]
            ap_name = netscan[0].decode()
            if len(ap_name) > 20:
                ap_name = ap_name[:17] + '...'
            vals = hexlify(netscan[1]).decode()
            bssid = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
            print('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
                ap_name, bssid, netscan[2], netscan[3],
                auth, str(netscan[5])))
            FILE_REPORT.append('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
                ap_name, bssid, netscan[2], netscan[3],
                auth, str(netscan[5])))
        print('\n')
        FILE_REPORT.append('\n')
        # AP (APSTAT)
        print('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK AP IF CONFIG', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK AP IF CONFIG', '='*10))
        apstat = dev.cmd(_CMDDICT_['APSTAT'], silent=True, rtn_resp=True)
        print('\n')
        FILE_REPORT.append('\n')
        if len(apstat) > 0:
            auth = AUTHMODE_DICT[int(apstat[-2])]
            print('AP INFO:')
            print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┓'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                'AP ENABLED', 'ESSID', 'CHANNEL', 'AUTHMODE'))
            print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                *apstat[:-2], auth))
            print('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                'IP', 'SUBNET', 'GATEAWAY', 'DNS'))
            try:
                print('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                    *apstat[-1]))
                print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┛'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            except Exception as e:
                print(e)
                pass
            FILE_REPORT.append('AP INFO:')
            FILE_REPORT.append('┏{0}━┳━{1}━┳━{2}━┳━{3}━┓'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            FILE_REPORT.append('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                'AP ENABLED', 'ESSID', 'CHANNEL', 'AUTHMODE'))
            FILE_REPORT.append('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                *apstat[:-2], auth))
            FILE_REPORT.append('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            FILE_REPORT.append('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                'IP', 'SUBNET', 'GATEAWAY', 'DNS'))
            try:
                FILE_REPORT.append('┃{0:^20} ┃ {1:^20} ┃ {2:^20} ┃ {3:^20} ┃'.format(
                    *apstat[-1]))
                FILE_REPORT.append('┗{0}━┻━{1}━┻━{2}━┻━{3}━┛'.format(
                            '━'*20, '━'*20, '━'*20, '━'*20))
            except Exception as e:
                FILE_REPORT.append(e)
                pass

        print('\n')
        FILE_REPORT.append('\n')

        # AP (APSCAN)
        print('{:<10} {} {:>10}'.format('='*10, 'NETWORK AP SCAN', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'NETWORK AP SCAN', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        apscan_cmd = _CMDDICT_['AP_SCAN']
        if apstat[:-2][0] != 0:
            if dev.dev_platform != 'esp8266':

                ap_scan_list = dev.cmd(apscan_cmd, silent=True, rtn_resp=True)
                if isinstance(ap_scan_list, list):
                    if len(ap_scan_list) > 0:
                        ap_devices = ap_scan_list
                        print('Found {} devices:'.format(len(ap_devices)))
                        FILE_REPORT.append('Found {} devices:'.format(len(ap_devices)))
                        for cdev in ap_devices:
                            bytdev = hexlify(cdev[0]).decode()
                            mac_ad = ':'.join([bytdev[i:i+2] for i in range(0, len(bytdev),
                                                                            2)])
                            print('MAC: {}'.format(mac_ad))
                            FILE_REPORT.append('MAC: {}'.format(mac_ad))
                    else:
                        print('No device found')
                        FILE_REPORT.append('No device found')
                else:
                    print('No device found')
                    FILE_REPORT.append('No device found')
            else:
                print('ESP8266 NOT SUPPORTED')
                FILE_REPORT.append('ESP8266 NOT SUPPORTED')
        else:
            print('AP DISABLED')
            FILE_REPORT.append('AP DISABLED')
        # CAT 'BOOT.PY'
        print('\n')
        FILE_REPORT.append('\n')
        print('{:<10} {} {:>10}'.format('='*10, 'boot.py CONTENT', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'boot.py CONTENT', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        dev.cmd('from upysh import *', silent=True)
        boot = dev.cmd("cat('boot.py')", silent=True, long_string=True, rtn_resp=True)
        print(boot)
        FILE_REPORT.append(boot)
        print('\n')
        FILE_REPORT.append('\n')
        # CAT 'MAIN.PY'

        print('{:<10} {} {:>10}'.format('='*10, 'main.py CONTENT', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'main.py CONTENT', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        mainpy = dev.cmd("cat('main.py');gc.collect()", silent=True, long_string=True,
                         rtn_resp=True)
        print(mainpy)
        FILE_REPORT.append(mainpy)
        print('\n')
        FILE_REPORT.append('\n')
        # CAT 'ERROR.LOG'

        print('{:<10} {} {:>10}'.format('='*10, 'error.log CONTENT', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'error.log CONTENT', '='*10))
        print('\n')
        FILE_REPORT.append('\n')
        is_err_log = dev.cmd("import uos;uos.listdir('/')", silent=True, rtn_resp=True)
        if 'error.log' in is_err_log:
            try:

                errlog = dev.cmd("cat('error.log');gc.collect()",
                                 silent=True, long_string=True, rtn_resp=True)

                print(errlog)
                FILE_REPORT.append(errlog)
            except Exception as e:
                pass
        else:
            print('error.log NOT FOUND')
            FILE_REPORT.append('error.log NOT FOUND')
        print('\n')
        FILE_REPORT.append('\n')
        if sd_ismounted:
            print('Looking for error.log in SD:')
            print('\n')
            FILE_REPORT.append('\n')

            is_err_log = dev.cmd("import uos;uos.listdir('/sd')", silent=True,
                                 rtn_resp=True)
            if 'error.log' in is_err_log:
                try:

                    errlog = dev.cmd("cat('/sd/error.log');gc.collect()",
                                     silent=True, long_string=True, rtn_resp=True)
                    print(errlog)
                    FILE_REPORT.append(errlog)
                    print('\n')
                    FILE_REPORT.append('\n')
                except Exception as e:
                    pass
            else:
                print('error.log NOT FOUND')
                FILE_REPORT.append('error.log NOT FOUND')

        # HW
        # PINS STATE
        print('\n')
        FILE_REPORT.append('\n')
        print('{:<10} {} {:>10}'.format('='*10, 'PINS STATE', '='*10))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '='*10, 'PINS STATE', '='*10))
        pinlist = "[16, 17, 26, 25, 34, 39, 36, 4, 21, 13, 12, 27, 33, 15, 32, 14, 22, 23, 5, 18, 19]"
        if dev.dev_platform == 'esp8266':
            pinlist = "[0,2,4,5,12,13,14,15]"
        machine_pin = "pins=[machine.Pin(i, machine.Pin.IN) for i in pin_list]"
        status = "dict(zip([str(p) for p in pins],[p.value() for p in pins]))"
        pin_status_cmd = "import machine;pin_list={};{};{};gc.collect()".format(
            pinlist, machine_pin, status)

        pin_dict = dev.cmd(pin_status_cmd, silent=True, rtn_resp=True)
        pin_list = list(pin_dict.keys())
        pin_list.sort()
        for key in pin_list:
            if pin_dict[key] == 1:
                print('{0:^10} | {1:^5} | HIGH'.format(key, pin_dict[key]))
                FILE_REPORT.append(
                    '{0:^10} | {1:^5} | HIGH'.format(key, pin_dict[key]))
            else:
                print('{0:^10} | {1:^5} |'.format(key, pin_dict[key]))
                FILE_REPORT.append(
                    '{0:^10} | {1:^5} |'.format(key, pin_dict[key]))
        print('\n')
        FILE_REPORT.append('\n')

        tdiff = time.time()-t0
        print('{:<10} {} {:>10}'.format(
            '*'*20, 'uPydev Diagnostics Test Finished!', '*'*20))
        FILE_REPORT.append('{:<10} {} {:>10}'.format(
            '*'*20, 'uPydev Diagnostics Test Finished!', '*'*20))
        print('TOTAL TIME: {} s'.format(round(tdiff, 2)))
        FILE_REPORT.append('TOTAL TIME: {} s'.format(round(tdiff, 2)))

        if save_rep:
            name_file = 'upyd_{}_{}_report.txt'.format(
                upy_id, datetime.now().strftime("%m-%d-%Y_at_%H-%M-%S"))
            if name_rep is not None:
                name_file = "{}.txt".format(name_rep)
            with open(name_file, 'w') as rfile:
                for line in FILE_REPORT:
                    if isinstance(line, str):
                        rfile.write(line)
                        rfile.write('\n')
                    else:
                        rfile.write("{}".format(line))
                        rfile.write('\n')
        if args.rst:
            dev.reset(reconnect=False)


def get_error_log(args):
    source = '/'
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss,
                 autodetect=True)
    print('{:<10} {} {:>10}'.format('='*10, 'error.log CONTENT', '='*10))
    print('\n')
    if dev.dev_platform == 'pyboard':
        source = '/flash'
    if args.s:
        source = args.s
    print('Looking for error.log in {}:'.format(source))
    dev.output = None
    dev.cmd("from upysh import cat;import uos,gc;uos.listdir('{}')".format(source),
            silent=True)
    if 'error.log' in dev.output:
        if source == '/':
            dev.wr_cmd("cat('error.log');gc.collect()", follow=True)
        else:
            dev.wr_cmd("cat('{}/error.log');gc.collect()".format(source), follow=True)
    else:
        print('error.log NOT FOUND')
    dev.disconnect()


def get_ip():
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


def do_pg_bar(index, wheel, nb_of_total, speed, time_e,
              loop_l, percentage, size_bar=bar_size):
    l_bloc = bloc_progress[loop_l]
    if index == bar_size:
        l_bloc = "█"
    sys.stdout.write("\033[K")
    print('▏{}▏{:>2}{:>5} % | DATA: {} | SPEED: {:>5} MB/s | TIME: {} s'.format("█" * index + l_bloc + " "*((bar_size+1) - len("█" * index + l_bloc)),
                                                                                wheel[index %
                                                                                      4],
                                                                                int((
                                                                                    percentage)*100),
                                                                                nb_of_total, speed, str(timedelta(seconds=time_e)).split('.')[0][2:]), end='\r')
    sys.stdout.flush()


def w_stream_reader(soc, total_size, chunk_rx):
    buff = bytearray(0)
    loop_index = 0
    wheel = ['|', '/', '-', "\\"]
    t_start = time.time()
    while True:
        t0 = time.time()
        try:
            chunk = soc.recv(chunk_rx)  # 32 KB
            if chunk != b'':
                buff += chunk
                loop_index_f = ((len(buff))/total_size)*bar_size
                loop_index = int(loop_index_f)
                loop_index_l = int(round(loop_index_f-loop_index, 1)*6)
                nb_of_total = "{:.2f}/{:.2f} MB".format(
                    len(buff)/(1024**2), total_size/(1024**2))
                percentage = len(buff)/total_size
                t_elapsed = time.time() - t_start
                t_speed = "{:^2.2f}".format((len(buff)/(1024**2))/t_elapsed)
                if pb:
                    do_pg_bar(loop_index, wheel, nb_of_total, t_speed,
                              t_elapsed, loop_index_l, percentage)
                if len(buff) == total_size:
                    break
            else:
                pass
                #print('END OF FILE')
                # soc.close()
                # break
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            else:
                print('END OF FILE')
                break
    return buff


def w_stream_writer(soc):
    buff = os.urandom(20000)
    try:
        soc.sendall(buff)  # 20 kB
    except Exception as e:
        if e == KeyboardInterrupt:
            print(e)


def stream_test(args, dev, mode='download'):
    if mode == 'download':
        # START A LOCAL SERVER
        chunk_size_kb = args.chunk_tx
        _kB = 1024
        _MB = 1024*_kB
        print('DOWNLOAD SPEED TEST:')
        print('CHUNK TX DATA SIZE: {:>40.2f} kB'.format(chunk_size_kb))
        print('CHUNK RX DATA SIZE: {:>40.2f} kB'.format(args.chunk_rx))
        print('TOTAL TX DATA SIZE: {:>40.2f} MB\n'.format(args.total_size))
        local_ip = get_ip()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((local_ip, 8005))
        server_socket.listen(1)
        dev.cmd_nb("w_stream_writer('{}', 8005, {}, {})".format(local_ip,
                                                                args.chunk_tx*_kB,
                                                                args.total_size*_MB),
                   follow=True)
        conn, addr = server_socket.accept()
        soc_timeout = 1
        conn.settimeout(soc_timeout)
        # time.sleep(1)
        t0 = time.time()
        data_chunk = w_stream_reader(conn, args.total_size*_MB, args.chunk_rx*_kB)
        dt = (time.time()-t0)-soc_timeout
        conn.close()
        return (data_chunk, dt)


def get_stream_test(args, device, mode='download'):
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print('*'*10, ' {} STREAM TEST '.format(device), '*'*10)
    dev.output = None
    dev.cmd('from sync_tool import w_stream_writer; [1]', silent=True)
    data, total_time = stream_test(args, dev, mode=mode)
    print('\n\nDone!')
    print('TEST RESULTS ARE:')
    print('TEST DURATION : {:.3f} (s)'.format(total_time))
    N_Bytes = len(data)
    print_sizefile('TEST DATA', N_Bytes)
    kBs = (N_Bytes/total_time)/1024
    print('DATA TRANSFER RATE (kBps): {:.3f} kB/s'.format(kBs))
    print('DATA TRANSFER RATE (Mbps): {:.3f} Mbps'.format((kBs*8)/1000))
    dev.disconnect()


def sysctl(args):
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    sys_cmd = "import {}"
    if args.start is not None:
        print('Loading {} script...'.format(args.start))
        sys_cmd = sys_cmd.format(args.start)
        dev.cmd_nb(sys_cmd, block_dev=False)
        print('Done!')
    elif args.stop is not None:
        reload = "del(sys.modules['{}'])".format(args.stop)
        print('Stopping {} script...'.format(args.stop))
        dev.kbi()
        print('Unloading {} script...'.format(args.stop))
        reload_cmd = "import sys,gc;{};gc.collect();print('Script unloaded!')".format(reload)
        time.sleep(1)
        dev.cmd(reload_cmd)
        print('Done!')
    dev.disconnect()


def log_script(args, dev='', log=None):

    def pipe_log(msg, log=log, std='stdout'):
        if std == 'stderr':
            log.error(msg)
        else:
            log.info(msg)
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
    log.info('Running {}...'.format(args.f))
    dev.wr_cmd(run_cmd, follow=True, pipe=pipe_log)

    time.sleep(0.2)
    reload_cmd = "import sys,gc;{};gc.collect()".format(reload)
    if args.s is not None:
        reload_syspath = "sys.path.remove('/{}')".format(dir)
        reload_cmd = "{};{};gc.collect()".format(reload, reload_syspath)

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    log.info('Done!')


def get_log_script(args, dev_name):
    script_filepy = args.f
    script_name = script_filepy.split('.')[0]
    filelog_path = os.path.join(os.environ['HOME'], '.upydev_logs')
    filelog_daemon = os.path.join(filelog_path, '{}_daemon.log'.format(script_name))
    if not args.daemon:
        if not args.stopd:
            if '.upydev_logs' not in os.listdir("{}".format(os.environ['HOME'])):
                os.mkdir(filelog_path)

            # Logging Setup
            # filelog_path = "{}/.upydev_logs/".format(os.environ['HOME'])
            # filelog_daemon = ''.join([filelog_path, '{}_daemon.log'.format(script_name)])
            log_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
                          'warning': logging.WARNING, 'error': logging.ERROR,
                          'critical': logging.CRITICAL}
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_levels[args.dslev])
            logging.basicConfig(
                level=log_levels['debug'],
                format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
                handlers=[handler])
            # setup one logger per device
            log = logging.getLogger('{}_{}'.format(dev_name, script_name))
            # log.setLevel(log_levels[args.dslev]) # MASTER LOG LEVEL
            # Filehandler for error
            fh_err = logging.FileHandler(os.path.join(
                filelog_path, '{}_error.log'.format(script_name)))
            fh_err.setLevel(log_levels[args.dflev])
            # Formatter for errors
            fmt_err = logging.Formatter(
                "%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s")
            fh_err.setFormatter(fmt_err)
            log.addHandler(fh_err)

            log_script(args, log=log)
        else:
            print('Stopping daemon log...')
            print(stop_by_pid(proc_name='upydev log'))
            time.sleep(1)
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            print('Stopping script...')
            dev.kbi()
            time.sleep(1)
            reload = "import sys;del(sys.modules['{}']);[1]".format(script_name)
            dev.cmd(reload, silent=True)
            print('Done!')
            dev.disconnect()

    else:
        single_command = []
        for i in range(len(sys.argv[2:])):
            if sys.argv[2:][i] != '-daemon':
                single_command.append(sys.argv[2:][i])
        gcommand = ' '.join(single_command)
        daemon_cmd = "nohup upydev log {} > {} &".format(gcommand, filelog_daemon)
        subprocess.call(daemon_cmd, shell=True)  # is this still safe?
        print('Running upydev log daemon-like mode')
        print('Logging to {} with level: {}'.format(
            '{}_daemon.log'.format(script_name), args.dslev))
        print("Do '$ upydev log -stopd -f {}' to stop the daemon".format(script_name))


# from https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
def follow_daemon_log(args):
    script_filepy = args.f
    script_name = script_filepy.split('.')[0]
    filelog_path = os.path.join(os.environ['HOME'], ".upydev_logs")
    filelog_daemon = os.path.join(filelog_path, '{}_daemon.log'.format(script_name))

    follow_tail = subprocess.Popen(['tail', '-F', filelog_daemon],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        try:
            line = follow_tail.stdout.readline()
            print(line[:-1].decode())
        except KeyboardInterrupt:
            print(
                "Unfollowing, do '$ upydev log -stopd -f {}' to stop the daemon".format(script_name))
            break


def debug_upyscript(args):
    print('Loading {} ...'.format(args.f))
    print('ENTER: EXECUTE NEXT LINE, C: BREAK')
    dbug_wrepl_tool_cmd = 'dbg_wrepl -f{} -t {} -p {}'.format(args.f, args.t, args.p)
    dbg_cmd = shlex.split(dbug_wrepl_tool_cmd)
    try:
        subprocess.call(dbg_cmd)
    except KeyboardInterrupt:
        time.sleep(1)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.kbi()
        dev.disconnect()


def pytest(args, devname):
    if args.f is not None:
        test = args.f
    elif args.fre is not None:
        test = ' '.join(args.fre)
    else:
        test = ''
    pytest_cmd_str = 'pytest {} -s --dev {}'.format(test, devname)
    if args.md:
        pytest_cmd_str = ' '.join([pytest_cmd_str, args.md[0]])
    pytest_cmd = shlex.split(pytest_cmd_str)
    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

    def preexec_function(action=old_action):
        signal.signal(signal.SIGINT, action)
    try:
        pytest_session = subprocess.call(pytest_cmd, preexec_fn=preexec_function)
        signal.signal(signal.SIGINT, old_action)
    except KeyboardInterrupt:
        pass
        print('')


def probe_device(addr, passwd):
    dt = check_device_type(addr)
    if dt == 'SerialDevice':
        if addr.replace('tty', 'cu') in serial_scan():
            return True
        elif addr in serial_scan():
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


#############################################
def debugging_action(args, **kargs):
    dev_name = kargs.get('device')

    if args.m == 'probe':
        if args.gg or args.G:
            if not args.devs:
                print('Reaching {} group...'.format(args.G))
            else:
                print('Reaching : {} ...'.format(', '.join(args.devs)))
            group_file = '{}.config'.format(args.G)
            if args.gg and group_file not in os.listdir(UPYDEV_PATH):
                print('No global group available')
                sys.exit()
            elif not args.gg and group_file not in os.listdir():
                print('No group available')
                sys.exit()
            else:
                if args.gg:
                    with open(os.path.join(UPYDEV_PATH, group_file), 'r') as group:
                        group_devs = (json.loads(group.read()))
                else:
                    with open(group_file, 'r') as group:
                        group_devs = (json.loads(group.read()))
                print('# {}:'.format(args.G))
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
                    return
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
                                    services = [uuidstr_to_str(serv)
                                                for serv in dev.metadata['uuids']]
                                except Exception as e:
                                    services = ['']

                    print('┃{0:^20} ┃ {1:^40} ┃ {2:^10} ┃ {3:^40} ┃'.format(dev.name, dev.address,
                                                                            int(dev.rssi), ','.join(services)))
                    if dev != devs[-1]:
                        print('┣{0}━╋━{1}━╋━{2}━╋━{3}━┫'.format(
                            '━'*20, '━'*40, '━'*10, '━'*40))
                print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┛'.format(
                    '━'*20, '━'*40, '━'*10, '━'*40))
        else:
            scan_sr = 'upydev scan -sr'
            scan_sr_cmd = shlex.split(scan_sr)
            scan_nt = 'upydev scan -nt'
            scan_nt_cmd = shlex.split(scan_nt)
            scan_bl = 'upydev scan -bl'
            scan_bl_cmd = shlex.split(scan_bl)
            all_scan = [scan_sr_cmd, scan_nt_cmd, scan_bl_cmd]
            for scan in all_scan:
                try:
                    subprocess.call(scan)

                except Exception as e:
                    print(e)

    elif args.m == 'ping':
        dt = check_device_type(args.t)
        if dt == 'WebSocketDevice':
            ping(args.t)
        else:
            print('Reaching {}...'.format(dev_name))
            is_reachable = probe_device(args.t, args.p)
            if is_reachable:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           OK, CHECK))
            else:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           FAIL, XF))

    elif args.m == 'run':
        run_script(args)

    elif args.m == 'timeit':
        timeit_script(args)

    elif args.m == 'diagnose':
        diagnose(args)

    elif args.m == 'errlog':
        get_error_log(args)

    elif args.m == 'stream_test':
        dt = check_device_type(args.t)
        if dt == 'WebSocketDevice':
            get_stream_test(args, dev_name)
        else:
            print('{} is a {}, stream_test not available'.format(dev_name, dt))

    elif args.m == 'sysctl':
        sysctl(args)

    elif args.m == 'log':
        if not args.follow:
            get_log_script(args, dev_name)
        else:
            follow_daemon_log(args)

    elif args.m == 'debug':
        debug_upyscript(args)

    elif args.m == 'pytest-setup':
        shutil.copy(os.path.join(upydev.__path__[0], 'conftest.py'), '.')
        shutil.copy(os.path.join(upydev.__path__[0], 'pytest.ini'), '.')
        print('pytest.ini and conftest.py saved in current working directory.')

    elif args.m == 'pytest':
        print('Running pytest with Device: {}'.format(dev_name))
        pytest(args, dev_name)

    return
