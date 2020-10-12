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
import socket
from datetime import timedelta
import netifaces
import logging
import shutil
import signal

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
    # scanoutput = subprocess.check_output(["ipconfig", "getifaddr", "en0"])
    # ip = scanoutput.decode('utf-8').split('\n')[0]
    try:
        ip = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for
                    iface in netifaces.interfaces() if netifaces.AF_INET in
                    netifaces.ifaddresses(iface)][-1]
        return ip
    except Exception as e:
        try:
            ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_soc.connect(('8.8.8.8', 1))
            local_ip = ip_soc.getsockname()[0]
            ip_soc.close()
            return local_ip
        except Exception as e:
            return '0.0.0.0'


def do_pg_bar(index, wheel, nb_of_total, speed, time_e,
              loop_l, percentage, size_bar=bar_size):
    l_bloc = bloc_progress[loop_l]
    if index == bar_size:
        l_bloc = "█"
    sys.stdout.write("\033[K")
    print('▏{}▏{:>2}{:>5} % | DATA: {} | SPEED: {:>5} MB/s | TIME: {} s'.format("█" *index + l_bloc  + " "*((bar_size+1) - len("█" *index + l_bloc)),
                                                                    wheel[index % 4],
                                                                    int((percentage)*100),
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
                nb_of_total = "{:.2f}/{:.2f} MB".format(len(buff)/(1024**2), total_size/(1024**2))
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
            log = logging.getLogger('{}_{}'.format(dev_name, script_name))  # setup one logger per device
            # log.setLevel(log_levels[args.dslev]) # MASTER LOG LEVEL
            # Filehandler for error
            fh_err = logging.FileHandler(os.path.join(filelog_path, '{}_error.log'.format(script_name)))
            fh_err.setLevel(log_levels[args.dflev])
            # Formatter for errors
            fmt_err = logging.Formatter("%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s")
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
        print('Logging to {} with level: {}'.format('{}_daemon.log'.format(script_name), args.dslev))
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
            print("Unfollowing, do '$ upydev log -stopd -f {}' to stop the daemon".format(script_name))
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

    sys.exit()
