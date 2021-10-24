from upydevice import Device
import sys
from upydev.helpinfo import see_help
from upydevice import check_device_type
import getpass
import os
import json
import upydev

UPYDEV_PATH = upydev.__path__[0]

DEVICE_MANAGEMENT_HELP = """
> DEVICE MANAGEMENT: Usage '$ upydev ACTION [opts]'
    ACTION:
    - config : to save upy device settings (see -t, -p, -g, -@, -gg),
                so the target and password arguments wont be required any more
                * -gg flag will add the device to the global group (UPY_G)
            (-t target -p password -g global directory -@ device name -gg global group)

    - check: to check current device information or with -@ entry point if stored in the global group.
             (Use -i option to see additional info if the device is reachable/connected)

    - set: to set current device configuration from a device saved in the global group with -@ entry point

    - make_group: to make a group of devices to send commands to. Use -f for the name
                  of the group and -devs option to indicate a name, ip and the
                  password of each board. (To store the group settings globally use -g option)

    - mg_group: to manage a group of devices to send commands to. Use -G for the name
                  of the group and -add option to add devices (indicate a name, ip and the
                  password of each board) or -rm to remove devices (indicated by name)

    - see: To get specific info about a devices group use -G option as "see -G [GROUP NAME]"

    - gg: To see global group
"""


KEY_N_ARGS = {}

VALS_N_ARGS = []


def address_entry_point(entry_point, group_file='', args=None):
    if group_file == '':
        group_file = 'UPY_G'
    # print(group_file)
    if '{}.config'.format(group_file) not in os.listdir() or args.g:
        group_file = os.path.join(UPYDEV_PATH, group_file)
    with open('{}.config'.format(group_file), 'r', encoding='utf-8') as group:
        devices = json.loads(group.read())
        # print(devices)
    devs = devices.keys()
    # NAME ENTRY POINT
    if entry_point in devs:
        dev_address = devices[entry_point][0]
        dev_pass = devices[entry_point][1]
        device_type = check_device_type(dev_address)
        if device_type == 'WebSocketDevice':
            return (dev_address, dev_pass)
        elif device_type == 'SerialDevice':
            return (dev_address, dev_pass)
        elif device_type == 'BleDevice':
            return (dev_address, dev_pass)
    else:
        print('Device not configured in global group')
        print("Do '$ upydev gg' to see devices global group")
        sys.exit()


def see(args):
    if args.G is None:
        pass
    else:
        group_file = '{}.config'.format(args.G)
        if group_file not in os.listdir() or args.g:
            group_file = os.path.join(UPYDEV_PATH, group_file)
        with open(group_file, 'r') as group:
            group_devs = (json.loads(group.read()))
        print('GROUP NAME: {}'.format(args.G))
        print('# DEVICES: {}'.format(len(group_devs.keys())))
        for key in group_devs.keys():
            dev_add = group_devs[key][0]
            dev_type = check_device_type(dev_add)
            if not dev_type:
                dev_add = group_devs[key][1]
                dev_type = check_device_type(dev_add)
            if key != list(group_devs.keys())[-1]:
                tree = '┣━'
            else:
                tree = '┗━'

            print('{} {:10} -> {:} @ {:} '.format(tree, key, dev_type, dev_add))


def devicemanagement_action(args, **kargs):
    # FILTER KARGS
    if args.m not in KEY_N_ARGS:
        for varg in VALS_N_ARGS:
            if varg in kargs:
                kargs.pop(varg)
    else:
        for varg in VALS_N_ARGS:
            if varg in kargs and varg not in KEY_N_ARGS[args.m]:
                kargs.pop(varg)
    _dev_name = kargs.get("device")
    # CONFIG:
    if args.m == 'config':
        if args.t is None or args.p is None:
            if args.sec:
                print('Secure config mode:')
                args.t = input('IP of device: ')
                args.p = getpass.getpass(prompt='Password: ', stream=None)
            else:
                if args.t is None:
                    print('Target Address required, see -t')
                    see_help(args.m)
                    sys.exit()
                else:
                    dt = check_device_type(args.t)
                    if dt == 'WebSocketDevice':
                        print('Target Address and Password required, see -t, -p or -sec')
                        see_help(args.m)
                        sys.exit()
                    elif dt == 'SerialDevice':
                        args.p = 115200
                    else:
                        args.p = 'pass'
        upydev_addr = args.t
        upydev_mdata = args.p
        if vars(args)['@'] is not None:
                upydev_name = vars(args)['@']
        else:
            upydev_name = 'upydevice'
        upy_conf = {'addr': upydev_addr, 'passwd': upydev_mdata, 'name': upydev_name}
        file_conf = 'upydev_.config'
        dt = check_device_type(args.t)
        if args.gg:
            group_file = 'UPY_G.config'
            group_file_path = os.path.join(UPYDEV_PATH, group_file)
            if group_file not in os.listdir(UPYDEV_PATH):
                with open(group_file_path, 'w', encoding='utf-8') as group:
                    group.write(json.dumps({}))
            with open(group_file_path, 'r', encoding='utf-8') as group:
                devices = json.loads(group.read())
                devices.update({upydev_name: [upydev_addr, upydev_mdata]})
            with open(group_file_path, 'w', encoding='utf-8') as group:
                group.write(json.dumps(devices))
            print('{} {} settings saved in global group!'.format(dt, upydev_name))
        else:
            if args.g:
                file_conf = os.path.join(UPYDEV_PATH, file_conf)
            with open(file_conf, 'w') as config_file:
                config_file.write(json.dumps(upy_conf))
            if args.g:
                print('{} {} settings saved globally!'.format(dt, upydev_name))
            else:
                print('{} {} settings saved in working directory!'.format(dt, upydev_name))

        # ZeroTier SSL shell-repl mode IP/REMOTE IP RPY bridge
        if args.zt:
            zt_file_conf = '_zt_upydev_.config'
            zt_file_path = os.path.join(UPYDEV_PATH, zt_file_conf)
            if zt_file_conf not in os.listdir(UPYDEV_PATH):
                with open(zt_file_path, 'w', encoding='utf-8') as zt_conf:
                    zt_conf.write(json.dumps({}))
            with open(zt_file_path, 'r', encoding='utf-8') as zt_conf:
                zt_devices = json.loads(zt_conf.read())
                zt_devices.update({upydev_name: args.zt})
            with open(zt_file_path, 'w', encoding='utf-8') as zt_conf:
                zt_conf.write(json.dumps(zt_devices))
            print('{} {} settings saved in ZeroTier group!'.format(dt, upydev_name))

        sys.exit()

    # UPYDEV LOOKS FOR UPYDEV_.CONFIG FILE
    if args.t is None:
        try:
            file_conf = 'upydev_.config'
            if file_conf not in os.listdir() or args.g:
                file_conf = os.path.join(UPYDEV_PATH, file_conf)

            with open(file_conf, 'r') as config_file:
                upy_conf = json.loads(config_file.read())
            args.t = upy_conf.get('addr')
            if not args.t:
                args.t = upy_conf.get('ip')
            args.p = upy_conf['passwd']
            if 'name' in upy_conf:
                _dev_name = upy_conf['name']
            else:
                _dev_name = 'upydevice'
            # @ ENTRY POINT
            if args.b is not None:
                if "@" in args.b:
                    gf, entryp = args.b.split('@')
                    args.t, args.p = address_entry_point(entryp, gf, args=args)
            if vars(args)['@'] is not None:
                    entryp = vars(args)['@']
                    args.t, args.p = address_entry_point(entryp, args=args)
            if args.apmd:
                args.t = '192.168.4.1'
            if args.st:
                print('Target:{}'.format(args.t))
        except Exception as e:
            print('upydev_.config file not found, please provide target and password or\
             create config file with command "config"')
            see_help('config')
            sys.exit()

    # CHECK

    if args.m == 'check':
        if vars(args)['@'] is not None:
            print('Device: {}'.format(entryp))
        else:
            print('Device: {}'.format(_dev_name))
        dt = check_device_type(args.t)
        if not args.i:
            print('Address: {}, Device Type: {}'.format(args.t, dt))
        else:
            if not args.wss:
                dev = Device(args.t, args.p, init=True)
            else:
                dev = Device(args.t, args.p, init=True, ssl=True)
            print(dev)
        sys.exit()

    # SET
    elif args.m == 'set':
        dt = check_device_type(args.t)
        if vars(args)['@'] is not None:
            print('Setting {}: {}'.format(dt, entryp))
        else:
            print('Setting {}: {}'.format(dt, _dev_name))
        upydev_ip = args.t
        upydev_pass = args.p
        if vars(args)['@'] is not None:
                upydev_name = vars(args)['@']
        else:
            upydev_name = _dev_name
        upy_conf = {'addr': upydev_ip, 'passwd': upydev_pass, 'name': upydev_name}
        file_conf = 'upydev_.config'
        if args.g:
            file_conf = os.path.join(UPYDEV_PATH, file_conf)
        with open(file_conf, 'w') as config_file:
            config_file.write(json.dumps(upy_conf))
        if args.g:
            print('{} {} settings saved globally!'.format(dt, upydev_name))
        else:
            print('{} {} settings saved in working directory!'.format(dt, upydev_name))
        sys.exit()

    # MAKE_GROUP
    elif args.m == 'make_group':
        if not args.f:
            print('Group Name required, indicate with -f option')
            see_help(args.m)
            sys.exit()
        else:
            group_file = '{}.config'.format(args.f)
            group_dict = {}
        if args.devs:
            group_dict = dict(zip(args.devs[::3], [
                              [args.devs[i], args.devs[i+1]] for i in range(1, len(args.devs)-1, 3)]))
        if args.g:
            group_file = os.path.join(UPYDEV_PATH, args.f)
        with open(group_file, 'w') as group:
            group.write(json.dumps(group_dict))

        if args.g:
            print('Group settings saved globally!')
        else:
            print('Group settings saved in working directory!')
        print('Upy devices group created!')
        print('GROUP NAME: {}'.format(args.f))
        print('# DEVICES: {}'.format(len(group_dict.keys())))
        for key in group_dict.keys():
            dt = check_device_type(group_dict[key][0])
            print('{} -> {} @ {}'.format(key, dt, group_dict[key][0]))
        sys.exit()

    # MANAGE GROUP
    # UPYDEV GROUP COMMAND
    if args.m == 'gg':
        args.G = 'UPY_G'
        args.m = 'see'

    if args.gg:
        args.G = 'UPY_G'
        args.g = True

    if args.G is not None:
        try:
            group_file = args.G
            # print(group_file)
            if '{}.config'.format(group_file) not in os.listdir() or args.g:
                group_file = os.path.join(UPYDEV_PATH, group_file)
            if args.m == 'see':
                see(args)
                sys.exit()
            if args.m == 'mg_group':
                if args.add is not None:
                    group_dict = dict(zip(args.add[::3], [
                                      [args.add[i], args.add[i+1]] for i in range(1, len(args.add)-1, 3)]))
                    with open('{}.config'.format(group_file), 'r', encoding='utf-8') as group:
                        devices = json.loads(group.read())
                        devices.update(group_dict)
                    with open('{}.config'.format(group_file), 'w', encoding='utf-8') as group:
                        group.write(json.dumps(devices))
                    print('Upy devices group updated!')
                    print('GROUP NAME: {}'.format(group_file.split('/')[-1]))
                    print('# DEVICES ADDED: {}'.format(len(group_dict.keys())))
                    for key in group_dict.keys():
                        dt = check_device_type(group_dict[key][0])
                        print('{} : {} @ {}'.format(key, dt, group_dict[key][0]))
                elif args.rm is not None:
                    group_dict_rm = args.rm
                    removed_devs = {}
                    with open('{}.config'.format(group_file), 'r', encoding='utf-8') as group:
                        devices = json.loads(group.read())
                        for dev in group_dict_rm:
                            # del devices[dev]
                            if dev in devices:
                                removed_devs.update({dev: devices.pop(dev)})
                            else:
                                print('Device {} not in this group'.format(dev))
                    if removed_devs:
                        with open('{}.config'.format(group_file), 'w', encoding='utf-8') as group:
                            group.write(json.dumps(devices))
                        print('Upy devices group updated!')
                        print('GROUP NAME: {}'.format(group_file.split('/')[-1]))
                        print('# DEVICES REMOVED: {}'.format(len(removed_devs.keys())))
                        for key in removed_devs.keys():
                            dt = check_device_type(removed_devs[key][0])
                            print('{} : {} @ {}'.format(key, dt, removed_devs[key][0]))

            sys.exit()
        except Exception as e:
            print(e)
            print('file not found, please create a group first')
            sys.exit()

    if args.m == 'see':
        if args.c:
            see_help(args.c)
        else:
            see_help(args.m)

    sys.exit()
