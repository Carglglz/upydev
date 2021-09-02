from upydevice import Device, DeviceException
from upydev.commandlib import _CMDDICT_
import sys
import ast
from datetime import datetime, date
from binascii import hexlify
import time

AUTHMODE_DICT = {0: 'NONE', 1: 'WEP', 2: 'WPA PSK', 3: 'WPA2 PSK',
                    4: 'WPA/WAP2 PSK'}

KEY_N_ARGS = {'du': ['f', 's'], 'df': ['s'], 'netstat_conn': ['wp'],
              'apconfig': ['ap'], 'i2c_config': ['i2c'],
              'spi_config': ['spi'], 'set_ntptime': ['utc'], 'tree': ['f']}

VALS_N_ARGS = ['f', 's', 'wp', 'ap', 'i2c', 'spi', 'utc']


GENERAL_COMMANDS_HELP = """
> GENERAL COMMANDS: Usage '$ upydev COMMAND [opts]'
    COMMAND:
        - info : for upy device system info
        - id : for upy device unique id
        - upysh : to enable the upy shell in the upy device (then do 'upydev man' to
                access upysh manual info)
        - reset : to do a soft reset in upy device
        - kbi : sends CTRL-C signal to stop an ongoing loop, to be able to access repl again
        - uhelp : just calls micropython help
        - umodules: just calls micropython help('modules')
        - meminfo : for upy device RAM memory info; call it once to check actual memory,
                    call it twice and it will free some memory
        - du : to get the size of file in root dir (default) or sd with '-s sd' option;
                    if no file name indicated with -f option, prints all files
        - df : to get memory info of the file system, (total capacity, free, used),
                    (default root dir, -s option to change)
        - tree: to get directory structure in tree format (requires upysh2.py)
        - netinfo : for upy device network info if station is enabled and connected to an AP
        - netinfot : same as netinfo but in table format
        - netscan : for upy device network scan
        - netstat_on : to enable STA
        - netstat_off : to disable STA
        - netstat_conn : to connect to an AP , must provide essid and password (see -wp)
        - netstat : STA state ; returns True if enabled, False if disabled
        - ap_on : to enable AP
        - ap_off : to disable AP
        - apstat : AP state ; returns True if enabled, False if disabled
        - apconfig : AP configuration of essid and password with authmode WPA/WPA2/PSK,
                    (see -ap), needs first that the AP is enabled (do 'upydev ap_on')
        - apscan : scan devices connected to AP; returns number of devices and mac address
        - i2c_config : to configure the i2c pins (see -i2c, defaults are SCL=22, SDA=23)
        - i2c_scan : to scan i2c devices (must config i2c pins first)
        - spi_config: to configure the spi pins (see -spi, defaults are SCK=5,MISO=19,MOSI=18,CS=21)
        - set_localtime: to pass host localtime and set upy device rtc
        - set_ntptime: to set rtc from server, (see -utc for time zone)
        - get_datetime: to get date and time (must be set first, see above commands)"""


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


def print_sizefile_all(fileslist, tabs=0, frep=None):
    for filedata in fileslist:
        namefile = filedata[0]
        filesize = filedata[1]

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
        prettyprintname += namefile
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
        if frep is not None:
            frep.append('{0:<40} Size: {1:>10}'.format(
                prettyprintname, sizestr))


def print_filesys_info(filesize):
    _kB = 1024
    if filesize < _kB:
        sizestr = str(filesize) + " by"
    elif filesize < _kB**2:
        sizestr = "%0.1f KB" % (filesize / _kB)
    elif filesize < _kB**3:
        sizestr = "%0.1f MB" % (filesize / _kB**2)
    else:
        sizestr = "%0.1f GB" % (filesize / _kB**3)
    return sizestr


def _dt_format(number):
        rtc_n = str(number)
        if len(rtc_n) == 1:
            rtc_n = "0{}".format(rtc_n)
            return rtc_n
        else:
            return rtc_n


def _ft_datetime(t_now):
    return([_dt_format(i) for i in t_now])


def gen_command(cmd, *args, **kargs):

    # FILTER KARGS
    if cmd not in KEY_N_ARGS:
        for varg in VALS_N_ARGS:
            if varg in kargs:
                kargs.pop(varg)
    else:
        for varg in VALS_N_ARGS:
            if varg in kargs and varg not in KEY_N_ARGS[cmd]:
                kargs.pop(varg)
    # INFO :
    if cmd == 'info':
        try:
            dev = Device(*args, **kargs)
            print(dev)
            dev.disconnect()
        except Exception as e:
            print(e)
            pass
        return
    # ID:
    elif cmd == 'id':
        dev = Device(*args, **kargs)
        uid = dev.cmd(_CMDDICT_['UID'], silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('ID: {}'.format(uid.decode()))
        dev.disconnect()
        return
    # UPYSH
    elif cmd == 'upysh':
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['UPYSH'], long_string=True)
        dev.disconnect()
        return
    # RESET
    elif cmd == 'reset':
        dev = Device(*args, **kargs)
        dev.reset(reconnect=False)
        time.sleep(0.5)
        dev.disconnect()
        return

    # KEYBOARD Interrupt

    elif cmd == 'kbi':
        dev = Device(*args, **kargs)
        dev.kbi()
        dev.disconnect()
        return

    # UHELP

    elif cmd == 'uhelp':
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['HELP'], long_string=True)
        dev.disconnect()
        return

    # UMODULES

    elif cmd == 'umodules':
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['MOD'], long_string=True)
        dev.disconnect()
        return

    # MEM_INFO

    elif cmd == 'meminfo':
        dev = Device(*args, **kargs)
        RAM = dev.cmd(_CMDDICT_['MEM'], silent=True, rtn_resp=True,
                      long_string=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            mem_info = RAM.splitlines()[1]
            mem = {elem.strip().split(':')[0]: int(elem.strip().split(':')[
                              1]) for elem in mem_info[4:].split(',')}
            print("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}".format(*['Memory',
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
        dev.disconnect()
        return

    # FILESIZE

    elif cmd == 'du':
        file_name = kargs.pop('f')
        source = kargs.pop('s')
        dev = Device(*args, **kargs)
        # check upysh2:
        is_upysh2 = dev.cmd(_CMDDICT_['CHECK_UPYSH2'], silent=True, rtn_resp=True)
        if is_upysh2:
            if file_name:
                cmd_str = "from upysh2 import du; du('{}')".format(file_name)
            else:
                cmd_str = "from upysh2 import du; du"
            dev.wr_cmd(cmd_str, follow=True)
        else:

            if source is not None:
                file_name = '/{}/{}'.format(source, file_name)
            cmd_str = _CMDDICT_['OS_STAT'].format(file_name)
            if file_name is None:
                dir = ''
                if source is not None:
                    dir = '/{}/'.format(source)
                cmd_str = _CMDDICT_['FILE_STAT'].format(dir)
            du_info = dev.cmd(cmd_str, silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
            else:
                if len(du_info) > 0:
                    if file_name is not None:
                        size = du_info[6]
                        print_sizefile(file_name, size)
                    else:
                        print_sizefile_all(du_info)
        dev.disconnect()
        return

    # FILESYS_INFO

    elif cmd == 'df':
        source = kargs.pop('s')
        dev = Device(*args, **kargs)
        filesys = ''
        filesys_check = True
        if source is not None:
            filesys = '/{}'.format(source)
            filesys_check = dev.cmd(_CMDDICT_['CHECK_DIR'].format(filesys.split('/')[1]),
                                    silent=True,
                                    rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
        cmd_str = _CMDDICT_['STAT_FS'].format(filesys)
        if filesys == '':
            filesys = 'Flash'
        if filesys_check:
            resp = dev.cmd(cmd_str, silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
            else:
                size_info = resp
                total_b = size_info[0] * size_info[2]
                used_b = (size_info[0] * size_info[2]) - (size_info[0] * size_info[3])
                total_mem = print_filesys_info(total_b)
                free_mem = print_filesys_info(size_info[0] * size_info[3])
                used_mem = print_filesys_info(used_b)
                if filesys == 'Flash':
                    mounted_on = '/'
                else:
                    mounted_on = filesys
                print("{0:12}{1:^12}{2:^12}{3:^12}{4:^12}{5:^12}".format(*['Filesystem',
                                                                           'Size', 'Used',
                                                                           'Avail',
                                                                           'Use%', 'Mounted on']))
                print('{0:12}{1:^12}{2:^12}{3:^12}{4:>8}{5:>5}{6:12}'.format(filesys, total_mem,
                                                                             used_mem, free_mem,
                                                                             "{:.1f} %".format((used_b/total_b)*100), ' ', mounted_on))
        else:
            print('{} not mounted'.format(filesys))
        dev.disconnect()
        return

    # TREE
    elif cmd == 'tree':
        dir_name = kargs.pop('f')
        dev = Device(*args, **kargs)
        # check upysh2:
        is_upysh2 = dev.cmd(_CMDDICT_['CHECK_UPYSH2'], silent=True, rtn_resp=True)
        if is_upysh2:
            if dir_name:
                cmd_str = "from upysh2 import tree; tree('{}')".format(dir_name)
            else:
                cmd_str = "from upysh2 import tree; tree"
            dev.wr_cmd(cmd_str, follow=True)
        else:
            pass
        dev.disconnect()
        return

    # NETINFO
    elif cmd == 'netinfo':
        dev = Device(*args, **kargs)
        net_info_list = dev.cmd(_CMDDICT_['NET_INFO'], silent=True,
                                rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if len(net_info_list) > 0:
                print('IF CONFIG: {}'.format(net_info_list[0]))
                print('SSID: {}'.format(net_info_list[1]))
                vals = hexlify(net_info_list[2]).decode()
                bssid = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
                print('BSSID: {}'.format(bssid))
                print('RSSI: {} dBm'.format(net_info_list[3]))
        dev.disconnect()
        return

    # NETINFOT
    elif cmd == 'netinfot':
        dev = Device(*args, **kargs)
        net_info_list = dev.cmd(_CMDDICT_['NET_INFO'], silent=True,
                                rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
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
        dev.disconnect()
        return

    # NETSCAN
    elif cmd == 'netscan':
        dev = Device(*args, **kargs)
        if dev.dev_class == 'SerialDevice':
            dev.cmd(_CMDDICT_['NET_STAT_ON'], silent=True)
        net_scan_list = dev.cmd(_CMDDICT_['NET_SCAN'],
                                silent=True,
                                rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            # FIX FOR SERIAL ESP DEBUGGING INFO
            if isinstance(net_scan_list, str):
                try:
                    net_scan_list = ast.literal_eval(net_scan_list.split('[0m')[1])
                except Exception as e:
                    net_scan_list = []
            print('┏{0}━┳━{1}━┳━{2}━┳━{3}━┳━{4}━┳━{5}━┓'.format(
                            '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))
            print('┃{0:^20} ┃ {1:^25} ┃ {2:^10} ┃ {3:^15} ┃ {4:^15} ┃ {5:^10} ┃'.format(
                'SSID', 'BSSID', 'CHANNEL', 'RSSI', 'AUTHMODE', 'HIDDEN'))
            print('┣{0}━╋━{1}━╋━{2}━╋━{3}━╋━{4}━╋━{5}━┫'.format(
                            '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))
            for net in net_scan_list:
                netscan = net
                auth = AUTHMODE_DICT[netscan[4]]
                vals = hexlify(netscan[1]).decode()
                ap_name = netscan[0].decode()
                if len(ap_name) > 20:
                    ap_name = ap_name[:17] + '...'
                bssid = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
                print('┃{0:^20} ┃ {1:^25} ┃ {2:^10} ┃ {3:^15} ┃ {4:^15} ┃ {5:^10} ┃'.format(
                    ap_name, bssid, netscan[2], netscan[3],
                    auth, str(netscan[5])))
            print('┗{0}━┻━{1}━┻━{2}━┻━{3}━┻━{4}━┻━{5}━┛'.format(
                        '━'*20, '━'*25, '━'*10, '━'*15, '━'*15, '━'*10))
        dev.disconnect()
        return

    # NETSTAT_ON

    elif cmd == 'netstat_on':
        dev = Device(*args, **kargs)
        stat_on = dev.cmd(_CMDDICT_['NET_STAT_ON'], silent=True,
                          rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if stat_on:
                print('Station Enabled')
        dev.disconnect()
        return

    # NETSTAT_OFF

    elif cmd == 'netstat_off':
        dev = Device(*args, **kargs)
        stat_off = dev.cmd(_CMDDICT_['NET_STAT_OFF']+'\r'*5, silent=True,
                           rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('Station Disabled')
        dev.disconnect()
        return

    # NETSTAT_CONN

    elif cmd == 'netstat_conn':
        ssid, passwd = kargs.pop('wp')
        print('Connecting to {}...'.format(ssid))
        connect_to = _CMDDICT_['NET_STAT_CONN'].format(ssid, passwd)
        dev = Device(*args, **kargs)
        dev.cmd(connect_to, silent=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            pass
        dev.disconnect()
        return

    # NETSTAT
    elif cmd == 'netstat':
        dev = Device(*args, **kargs)
        netstat = dev.cmd(_CMDDICT_['NET_STAT'], silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if netstat:
                print('Station Enabled')
            else:
                print('Station Disabled')
            pass
        dev.disconnect()
        return

    # AP_ON

    elif cmd == 'ap_on':
        dev = Device(*args, **kargs)
        ap_on = dev.cmd(_CMDDICT_['AP_ON'], silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if ap_on:
                print('access Point Enabled')
            else:
                print('access Point Disabled')
            pass
        dev.disconnect()
        return
    #
    # AP_OFF

    elif cmd == 'ap_off':
        dev = Device(*args, **kargs)
        ap_off = dev.cmd(_CMDDICT_['AP_OFF'], silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if not ap_off:
                print('access Point Disabled')
            else:
                print('access Point Enabled')
            pass
        dev.disconnect()
        return

    # APSTAT

    elif cmd == 'apstat':
        dev = Device(*args, **kargs)
        apstat = dev.cmd(_CMDDICT_['APSTAT'], silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
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
        dev.disconnect()
        return

    # APCONFIG

    elif cmd == 'apconfig':
        ssid, passwd = kargs.pop('ap')
        print('Configuring {} access Point ...'.format(ssid))
        apconfig = _CMDDICT_['AP_CONFIG'].format(ssid, passwd)
        if len(passwd) < 8:
            print('[WARNING]: Password too short (less than 8 characters)')
        dev = Device(*args, **kargs)
        dev.cmd(apconfig, silent=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('{} access Point Configured'.format(ssid))
        dev.disconnect()
        return

    # APSCAN

    elif cmd == 'apscan':
        dev = Device(*args, **kargs)
        ap_scan_list = dev.cmd(_CMDDICT_['AP_SCAN'], silent=True,
                               rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if len(ap_scan_list) > 0:
                ap_devices = ap_scan_list
                print('Found {} devices:'.format(len(ap_devices)))
                for cdev in ap_devices:
                    bytdev = hexlify(cdev[0]).decode()
                    mac_ad = ':'.join([bytdev[i:i+2] for i in range(0, len(bytdev),
                                                                    2)])
                    print('MAC: {}'.format(mac_ad))
            else:
                print('No device found')
        dev.disconnect()
        return

    # I2C_CONFIG # FIX FOR PYBOARD, AUTODETECT

    elif cmd == 'i2c_config':
        scl, sda = kargs.pop('i2c')
        dev = Device(*args, **kargs, autodetect=True)
        if dev.dev_platform == 'pyboard':
            dev.cmd(_CMDDICT_['I2C_CONFIG_PYB'].format(scl, sda), silent=True)
        else:
            dev.cmd(_CMDDICT_['I2C_CONFIG'].format(scl, sda), silent=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('I2C configured:\nSCL = Pin({}), SDA = Pin({})'.format(scl,
                                                                         sda))
        dev.disconnect()
        return

    # I2C_SCAN

    elif cmd == 'i2c_scan':
        dev = Device(*args, **kargs)
        i2c_scan_list = dev.cmd(_CMDDICT_['I2C_SCAN'], silent=True,
                                rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if len(i2c_scan_list) > 0:
                i2c_devices = i2c_scan_list
                print('Found {} devices:'.format(len(i2c_devices)))
                print(i2c_devices)
                print('Hex:')
                print([hex(i2c_dev) for i2c_dev in i2c_devices])
            else:
                print('No device found')
        dev.disconnect()
        return
    #
    # SPI CONFIG
    elif cmd == 'spi_config':
        spi_conf = kargs.pop('spi')
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['SPI_CONFIG'].format(*spi_conf), silent=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('SPI configured:\nSCK = Pin({}), MISO = Pin({}), MOSI = Pin({}), CS = Pin({})'.format(
                    *spi_conf))
        dev.disconnect()
        return

    #  * RTC *

    # SET LOCAL TIME

    elif cmd == 'set_localtime':
        dev = Device(*args, **kargs)
        print('Setting local time: {}'.format(
            datetime.now().strftime("%Y-%m-%d T %H:%M:%S")))
        wkoy = date.today().isocalendar()[1]
        datetime_local = [val for val in datetime.now().timetuple()[:-3]]
        datetime_tuple = datetime_local[:3]
        datetime_tuple.append(wkoy)
        datetime_final = datetime_tuple + datetime_local[3:] + [0]
        dev.cmd(_CMDDICT_['SET_RTC_LT'].format(*datetime_final), silent=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('Done!')
        dev.disconnect()
        return
    #
    # SET NTP TIME
    elif cmd == 'set_ntptime':
        utc = kargs.pop('utc')
        print('Setting time UTC+{} from NTP Server'.format(utc))
        dev = Device(*args, **kargs)
        for ntp_cmd in _CMDDICT_['SET_RTC_NT'].format(utc).split(';'):
            dev.cmd(ntp_cmd, silent=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)

        print('Done!')
        dev.disconnect()
        return

    # GET UPY DEVICE LOCALTIME
    elif cmd == 'get_datetime':
        dev = Device(*args, **kargs)
        datetime_dev = dev.cmd(_CMDDICT_['DATETIME'],
                               silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            formatted_devtime = _ft_datetime(datetime_dev)
            print('Device RTC time: {}-{}-{} T {}:{}:{}'.format(*formatted_devtime))
        dev.disconnect()
        return

    elif cmd == 'gc':
        print(GENERAL_COMMANDS_HELP)
        sys.exit()
