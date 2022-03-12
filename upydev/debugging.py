from upydevice import Device, check_device_type, serial_scan, net_scan
import sys
from upydev.devicemanagement import check_zt_group
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
import argparse
rawfmt = argparse.RawTextHelpFormatter


dict_arg_options = {'ping': ['t', 'zt', 'p'],
                    'probe': ['t', 'p', 'G', 'gg', 'devs', 'zt'],
                    'scan': ['nt', 'sr', 'bl'],
                    'run': ['t', 'p', 'wss', 'f', 's'],
                    'timeit': ['t', 'p', 'wss', 'f', 's'],
                    'stream_test': ['t', 'p', 'wss', 'chunk_tx',
                                    'chunk_rx', 'total_size'],
                    'sysctl': ['t', 'p', 'wss', 'fre', 's'],
                    'log': ['t', 'p', 'wss', 'f', 's',
                            'daemon', 'follow', 'dslev', 'dflev',
                            'stopd'],
                    'pytest': ['t', 'p', 'wss', 'f', 'fre']}

PING = dict(help="ping the device to test if device is"
                 " reachable, CTRL-C to stop.",
            desc="this sends ICMP ECHO_REQUEST packets to device",
            subcmd={},
            options={"-t": dict(help="device target address",
                                required=True),
                     "-p": dict(help='device password or baudrate',
                                required=True),
                     "-zt": dict(help='internal flag for zerotierone device',
                                 required=False,
                                 default=False,
                                 action='store_true')})

PROBE = dict(help="to test if a device is reachable",
             desc="ping, scan serial ports or ble scan depending on device type",
             subcmd={},
             options={"-t": dict(help="device target address",
                                 required=True),
                      "-p": dict(help='device password or baudrate',
                                 required=True),
                      "-zt": dict(help='internal flag for zerotierone device',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-G": dict(help='internal flag for group mode',
                                 required=False,
                                 default=None),
                      "-gg": dict(help='flag for global group',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                      "-devs": dict(help='flag for filtering devs in global group',
                                    required=False,
                                    nargs='*')})

SCAN = dict(help="to scan for available devices, use a flag to filter for device type",
            desc="\ndefault: if no flag provided will do all three scans.",
            subcmd={},
            options={"-sr": dict(help="scan for SerialDevice",
                                 required=False,
                                 default=False,
                                 action='store_true'),
                     "-nt": dict(help='scan for WebSocketDevice',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                     "-bl": dict(help='scan for BleDevice',
                                 required=False,
                                 default=False,
                                 action='store_true')})

RUN = dict(help="run a script in device, CTRL-C to stop",
           desc="this calls 'import [script]' in device and reloads it at the end",
           subcmd=dict(help=('indicate a script to run'),
                       metavar='script'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-s": dict(help='indicate the path of the script if in external fs'
                                    ' e.g. an sd card.',
                               required=False)})

TIMEIT = dict(help="to measure execution time of a module/script",
              desc="source: https://github.com/peterhinch/micropython-samples"
                   "/tree/master/timed_function",
              subcmd=dict(help=('indicate a script to run'),
                          metavar='script'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true'),
                       "-s": dict(help='indicate the path of the script if in external'
                                  ' fs e.g. an sd card.',
                                  required=False)})
STREAM_TEST = dict(help="to test download speed (from device to host)",
                   desc="default: 10 MB of random bytes are sent in chunks of 20 kB "
                        "and received in chunks of 32 kB.\n\n*(sync_tool.py required)",
                   subcmd={},
                   options={"-t": dict(help="device target address",
                                       required=True),
                            "-p": dict(help='device password or baudrate',
                                       required=True),
                            "-wss": dict(help='use WebSocket Secure',
                                         required=False,
                                         default=False,
                                         action='store_true'),
                            "-chunk_tx": dict(help='chunk size of data packets in kB to'
                                                   ' send',
                                              required=False, default=20, type=int),
                            "-chunk_rx": dict(help='chunk size of data packets in kB to'
                                                   ' receive',
                                              required=False, default=32, type=int),
                            "-total_size": dict(help='total size of data packets in MB',
                                                required=False, default=10, type=int)})

SYSCTL = dict(help="to start/stop a script without following the output",
              desc="to follow initiate repl",
              mode=dict(help='indicate a mode {start,stop}',
                        metavar='mode',
                        choices=['start', 'stop']),
              subcmd=dict(help='indicate a script to start/stop',
                          metavar='script'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true')})

LOG = dict(help="to log the output of a script running in device",
           desc="log levels (sys.stdout and file), run modes (normal, daemon) are"
                "available through following options",
           subcmd=dict(help=('indicate a script to run and log'),
                       metavar='script'),
           options={"-t": dict(help="device target address",
                               required=True),
                    "-p": dict(help='device password or baudrate',
                               required=True),
                    "-wss": dict(help='use WebSocket Secure',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                    "-s": dict(help='indicate the path of the script if in external fs'
                                    ' e.g. an sd card.',
                               required=False),
                    "-dflev": dict(help='debug file mode level; default: error',
                                   default='error',
                                   choices=['debug', 'info', 'warning', 'error',
                                            'critical']),
                    "-dslev": dict(help='debug sys.stdout mode level; default: debug',
                                   default='debug',
                                   choices=['debug', 'info', 'warning', 'error',
                                            'critical']),
                    "-daemon": dict(help='enable "daemon mode", uses nohup so this '
                                         'means running in background, output if any is'
                                         ' redirected to [SCRIPT_NAME]_daemon.log',
                                    default=False, action='store_true'),
                    "-stopd": dict(help='To stop a log daemon script',
                                   default=False, action='store_true'),
                    "-F": dict(help='To follow a daemon log script file',
                               action='store_true',
                               default=False)})

PYTEST = dict(help="run tests on device with pytest (use pytest setup first)",
              subcmd=dict(help='indicate a test script to run, any optional '
                               'arg is passed to pytest',
                          default=[''],
                          metavar='test',
                          nargs='*'),
              options={"-t": dict(help="device target address",
                                  required=True),
                       "-p": dict(help='device password or baudrate',
                                  required=True),
                       "-wss": dict(help='use WebSocket Secure',
                                    required=False,
                                    default=False,
                                    action='store_true')})


DB_CMD_DICT_PARSER = {"ping": PING, "probe": PROBE, "scan": SCAN, "run": RUN,
                      "timeit": TIMEIT, "stream_test": STREAM_TEST, "sysctl": SYSCTL,
                      "log": LOG, "pytest": PYTEST}


usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('debugging tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in DB_CMD_DICT_PARSER.items():
    if 'desc' in subcmd.keys():
        _desc = f"{subcmd['help']}\n\n{subcmd['desc']}"
    else:
        _desc = subcmd['help']
    _subparser = subparser_cmd.add_parser(command, help=subcmd['help'],
                                          description=_desc,
                                          formatter_class=rawfmt)
    for pos_arg in subcmd.keys():
        if pos_arg not in ['subcmd', 'help', 'desc', 'options', 'alt_ops']:
            _subparser.add_argument(pos_arg, **subcmd[pos_arg])
    if subcmd['subcmd']:
        _subparser.add_argument('subcmd', **subcmd['subcmd'])
    for option, op_kargs in subcmd['options'].items():
        _subparser.add_argument(option, **op_kargs)


def parseap(command_args):
    try:
        return parser.parse_known_args(command_args)
    except SystemExit:  # argparse throws these because it assumes you only want
        # to do the command line
        return None  # should be a default one


def sh_cmd(cmd_inp):
    # parse args
    command_line = shlex.split(cmd_inp)

    all_args = parseap(command_line)

    if not all_args:
        return
    else:
        args, unknown_args = all_args

    return args, unknown_args


def filter_bool_opt(k, v):
    if v and isinstance(v, bool):
        return f"{k}"
    else:
        return ""


def expand_margs(v):
    if isinstance(v, list):
        return ' '.join(v)
    else:
        return v


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


def ping(ip, zt=False):
    if ':' in ip:
        ip, _ = ip.split(':')
    if zt:

        ping_cmd_str = f'ssh {zt["fwd"]} ping {zt["dev"]}'
    else:
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


def run_script(args, script):
    dir = ''
    script_filepy = script
    script_name = script_filepy.split('.')[0]
    reload = f"del(sys.modules['{script_name}'])"
    run_cmd = f"import {script_name};"
    # print(run_cmd)
    if args.s is not None:
        dir = args.s
        sd_path = f"import sys;sys.path.append('/{dir}')"
        run_cmd = f"{sd_path};import {script_name}"

    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print(f'Running {script}...')
    dev.wr_cmd(run_cmd, follow=True)

    time.sleep(0.2)
    reload_cmd = f"import sys,gc;{reload};gc.collect()"
    if args.s is not None:
        reload_syspath = f"sys.path.remove('/{dir}')"
        reload_cmd = f"{reload};{reload_syspath};gc.collect()"

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    print('Done!')


def timeit_script(args, script):
    timeit_import = "from time_it import tzero, tdiff, result;"
    dir = ''
    script_filepy = script
    script_name = script_filepy.split('.')[0]
    reload = f"del(sys.modules['{script_name}'])"
    timeit_cmd = (f"t_0 = tzero();import {script_name};"
                  f"diff=tdiff(t_0);result('{script_name}',diff);")
    timeit_final_cmd = timeit_import + timeit_cmd
    if args.s is not None:
        dir = args.s
        sd_path = f"import sys;sys.path.append('/{dir}')"
        timeit_final_cmd = f"{sd_path};{timeit_final_cmd}"

    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    print(f'Running {script}...')
    dev.wr_cmd(timeit_final_cmd, follow=True)

    time.sleep(0.2)
    reload_cmd = f"import sys;{reload};gc.collect()"
    if args.s is not None:
        reload_syspath = f"sys.path.remove('/{dir}')"
        reload_cmd = f"{reload};{reload_syspath};gc.collect()"

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    print('Done!')


def ping_diagnose(ip, rep_file=None):
    if ':' in ip:
        ip, _ = ip.split(':')
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
                    len(buff)/(1000**2), total_size/(1000**2))
                percentage = len(buff)/total_size
                t_elapsed = time.time() - t_start
                t_speed = "{:^2.2f}".format((len(buff)/(1000**2))/t_elapsed)
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
        _kB = 1000
        _MB = 1000*_kB
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
    kBs = (N_Bytes/total_time)/1000
    print('DATA TRANSFER RATE (kBps): {:.3f} kB/s'.format(kBs))
    print('DATA TRANSFER RATE (Mbps): {:.3f} Mbps'.format((kBs*8)/1000))
    dev.disconnect()


def sysctl(args, script):
    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    mode = args.mode
    _script = script.replace('.py', '')
    sys_cmd = "import {}"
    if mode == 'start':
        print(f'Loading {script} script...')
        sys_cmd = sys_cmd.format(_script)
        dev.cmd_nb(sys_cmd, block_dev=False)
        time.sleep(2)
        print('Done!')
    elif mode == 'stop':
        reload = f"del(sys.modules['{_script}'])"
        print(f'Stopping {script} script...')
        dev.kbi()
        print(f'Unloading {script} script...')
        reload_cmd = (f"import sys,gc;{reload};gc.collect();"
                      "print('systctl: script unloaded')")
        time.sleep(1)
        dev.cmd(reload_cmd)
        print('Done!')
    dev.disconnect()


def log_script(args, script, dev='', log=None):

    def pipe_log(msg, log=log, std='stdout'):
        if std == 'stderr':
            log.error(msg)
        else:
            log.info(msg)
    dir = ''
    script_filepy = script
    script_name = script_filepy.split('.')[0]
    reload = f"del(sys.modules['{script_name}'])"
    run_cmd = f"import {script_name};"
    # print(run_cmd)
    if args.s is not None:
        dir = args.s
        sd_path = f"import sys;sys.path.append('/{dir}')"
        run_cmd = f"{sd_path};import {script_name}"

    dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
    log.info(f'Running {script}...')
    dev.wr_cmd(run_cmd, follow=True, pipe=pipe_log)

    time.sleep(0.2)
    reload_cmd = f"import sys,gc;{reload};gc.collect()"
    if args.s is not None:
        reload_syspath = f"sys.path.remove('/{dir}')"
        reload_cmd = f"{reload};{reload_syspath};gc.collect()"

    dev.cmd(reload_cmd, silent=True)
    dev.disconnect()
    log.info('Done!')


def get_log_script(args, script, dev_name):
    script_filepy = script
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

            log_script(args, script, log=log)
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
        print(daemon_cmd)  # does not work in subprocess --> shell
        # subprocess.Popen(daemon_cmd, shell=True)  # is this still safe?
        # time.sleep(3)
        # print('Running upydev log daemon-like mode')
        # print('Logging to {} with level: {}'.format(
        #     '{}_daemon.log'.format(script_name), args.dslev))
        # print("Do '$ upydev log {} -stopd ' to stop the daemon".format(script_name))


# from https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
def follow_daemon_log(args, script):
    script_filepy = script
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
            print(f"Unfollowing, do '$ upydev log {script_name} "
                  "-stopd ' to stop the daemon")
            break


def pytest(args, scripts, unkwargs, devname):

    test = ' '.join(scripts)
    pytest_cmd_str = 'pytest {} -s --dev {}'.format(test, devname)
    # if args.mode:
    #     pytest_cmd_str = ' '.join([pytest_cmd_str, args.mode])
    pytest_cmd = shlex.split(pytest_cmd_str)
    if unkwargs:
        pytest_cmd += unkwargs
    old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

    def preexec_function(action=old_action):
        signal.signal(signal.SIGINT, action)
    try:
        subprocess.call(pytest_cmd, preexec_fn=preexec_function)
        signal.signal(signal.SIGINT, old_action)
    except KeyboardInterrupt:
        pass
        print('')


def probe_device(addr, passwd, args):
    dt = check_device_type(addr)
    if dt == 'SerialDevice':
        if addr.replace('tty', 'cu') in serial_scan():
            return True
        elif addr in serial_scan():
            return True
        else:
            return False
    elif dt == 'WebSocketDevice':
        try:
            dev = Device(addr, passwd)
            status = dev.is_reachable(zt=args.zt)
            if status:
                return True
            else:
                return False
        except Exception:
            return False

    elif dt == 'BleDevice':
        from upydevice.bledevice import ble_scan
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
def debugging_action(args, unkwargs, **kargs):
    dev_name = kargs.get('device')
    args_dict = {f"-{k}": v for k, v in vars(args).items()
                 if k in dict_arg_options[args.m]}
    args_list = [f"{k} {expand_margs(v)}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    cmd_inp = f"{args.m} {' '.join(unkwargs)} {' '.join(args_list)}"
    # print(cmd_inp)
    # sys.exit()
    # debug command:
    if cmd_inp.startswith('!'):
        args = parseap(shlex.split(cmd_inp[1:]))
        print(args)
        return
    if '-h' in unkwargs:
        sh_cmd(f"{args.m} -h")
        sys.exit()

    result = sh_cmd(cmd_inp)
    if not result:
        sys.exit()
    else:
        args, unknown_args = result
    if hasattr(args, 'subcmd'):
        command, rest_args = args.m, args.subcmd
        if rest_args is None:
            rest_args = []
    else:
        command, rest_args = args.m, []
    # print(f"{command}: {args} {rest_args} {unknown_args}")

    if command == 'probe':
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
                    # check if device in ZeroTier group.
                    args.zt = check_zt_group(key, args)
                    is_reachable = probe_device(dev_add, dev_pass, args)
                    if isinstance(args.zt, dict):
                        dev_add = f'{dev_add}/{args.zt["dev"]}'
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
            # check if device in ZeroTier group.
            args.zt = check_zt_group(dev_name, args)
            print('Reaching {}...'.format(dev_name))
            is_reachable = probe_device(args.t, args.p, args)
            dt = check_device_type(args.t)
            if isinstance(args.zt, dict):
                args.t = f'{args.t}/{args.zt["dev"]}'
            if is_reachable:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           OK, CHECK))
            else:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           FAIL, XF))

    elif command == 'scan':
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
                    if not man:
                        man = 'Unknown'
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
            from upydevice.bledevice import ble_scan
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
                                except Exception:
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

    elif command == 'ping':
        dt = check_device_type(args.t)
        if dt == 'WebSocketDevice':
            # check if device in ZeroTier group.
            zt_file_conf = '_zt_upydev_.config'
            zt_file_path = os.path.join(UPYDEV_PATH, zt_file_conf)
            if zt_file_conf in os.listdir(UPYDEV_PATH):
                with open(zt_file_path, 'r', encoding='utf-8') as zt_conf:
                    zt_devices = json.loads(zt_conf.read())
                    if dev_name in zt_devices:
                        args.zt = zt_devices[dev_name]

            ping(args.t, args.zt)
        else:
            print('Reaching {}...'.format(dev_name))
            is_reachable = probe_device(args.t, args.p, args)
            if is_reachable:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           OK, CHECK))
            else:
                print('{:10} -> {:} @ {:} -> {} {}'.format(dev_name, dt, args.t,
                                                           FAIL, XF))

    elif command == 'run':
        run_script(args, rest_args)

    elif command == 'timeit':
        timeit_script(args, rest_args)

    elif command == 'stream_test':
        dt = check_device_type(args.t)
        if dt == 'WebSocketDevice':
            get_stream_test(args, dev_name)
        else:
            print('{} is a {}, stream_test not available'.format(dev_name, dt))

    elif command == 'sysctl':
        sysctl(args, rest_args)

    elif command == 'log':
        if not args.F:
            get_log_script(args, rest_args, dev_name)
        else:
            follow_daemon_log(args, rest_args)

    elif command == 'pytest':
        if rest_args[0] == 'setup':
            shutil.copy(os.path.join(upydev.__path__[0], 'conftest.py'), '.')
            shutil.copy(os.path.join(upydev.__path__[0], 'pytest.ini'), '.')
            print('pytest.ini and conftest.py saved in current working directory.')
        else:
            for uk in ['-f', '-fre']:
                if uk in unknown_args:
                    unknown_args.remove(uk)
            print('Running pytest with Device: {}'.format(dev_name))
            pytest(args, rest_args, unknown_args, dev_name)

    return
