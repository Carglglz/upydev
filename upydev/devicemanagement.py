from upydevice import Device, check_device_type
import sys
from upydev.helpinfo import see_help
import getpass
import os
import json
import upydev
import argparse
import shlex
rawfmt = argparse.RawTextHelpFormatter

dict_arg_options = {'config': ['t', 'zt', 'p', 'wss', 'g', 'gg', 'G', 'sec', '@'],
                    'check': ['@', 'i', 'wss', 'g'],
                    'set': ['@', 'g'],
                    'register': ['@', 'gg', 's', 'f', 'fre', 'g'],
                    'lsdevs': ['s'],
                    'mkg': ['g', 'devs', 'f'],
                    'gg': ['g'],
                    'see': ['g', 'f'],
                    'mgg': ['g', 'f', 'rm', 'add', 'gg'],
                    'mksg': ['g', 'f', 'fre', 'devs', 'gg']}

CONFIG = dict(help="to save device settings",
              desc="this will allow set default device configuration or \n"
                   "target a specific device in a group.\n"
                   "\ndefault: a configuration file 'upydev_.config' is saved in\n"
                   "current working directory, use -[options] for custom configuration",
              subcmd={},
              options={"-t": dict(help="device target address"),
                       "-p": dict(help='device password or baudrate'),
                       "-g": dict(help='save configuration in global path',
                                  required=False,
                                  default=False,
                                  action='store_true'),
                       "-gg": dict(help='save device configuration in global group',
                                   required=False,
                                   default=False,
                                   action='store_true'),
                       "-@": dict(help='specify a device name',
                                  required=False),
                       "-zt": dict(help='zerotierone device configuration',
                                   required=False),
                       "-sec": dict(help='introduce password with no echo',
                                    required=False,
                                    default=False,
                                    action='store_true')})

CHECK = dict(help='to check device information',
             desc='shows current device information or specific device\n'
                  'indicated with -@ option if it is stored in the global group.',
             subcmd={},
             options={"-@": dict(help='specify device/s name',
                                 required=False,
                                 nargs='+'),
                      "-i": dict(help='if device is online/connected gets device info',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                      "-g": dict(help='looks for configuration in global path',
                                 required=False,
                                 default=False,
                                 action='store_true'),
                      "-wss": dict(help='use WebSocket Secure',
                                   required=False,
                                   default=False,
                                   action='store_true'),
                      "-G": dict(help='specify a group, default: global group',
                                 required=False)})

SET = dict(help='to set current device configuration',
           subcmd={},
           options={"-@": dict(help='specify device name',
                               required=False),
                    "-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-G": dict(help='specify a group, default: global group',
                               required=False)})

REGISTER = dict(help='to register a device/group as a shell function so it is callable',
                subcmd=dict(help='alias for device/s or group',
                            metavar='alias',
                            nargs='*'),
                options={"-@": dict(help='specify device name',
                                    required=False,
                                    nargs='+'),
                         "-gg": dict(help='register a group of devices',
                                     required=False,
                                     default=False,
                                     action='store_true'),
                         "-s": dict(help='specify a source file, default: ~/.profile',
                                    required=False),
                         "-g": dict(help='looks for configuration in global path',
                                    required=False,
                                    default=False,
                                    action='store_true')})

LSDEVS = dict(help='to see registered devices or groups',
              desc='this also defines a shell function with the same name in the source'
                   ' file',
              subcmd={},
              options={"-s": dict(help='specify a source file, default: ~/.profile',
                                  required=False),
                       "-G": dict(help='specify a group, default: global group',
                                  required=False)})

MKG = dict(help='make a group of devices',
           desc='this save a config file with devices settings so they can be targeted'
                ' all together',
           subcmd=dict(help='group name',
                       metavar='group'),
           options={"-g": dict(help='save configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-devs": dict(help='device configuration [name] [target] '
                                       '[password]',
                                  required=False,
                                  nargs='+')})

GG = dict(help='to see global group of devices',
          subcmd={},
          options={"-g": dict(help='looks for configuration in global path',
                              required=False,
                              default=False,
                              action='store_true')})

SEE = dict(help='to see a group of devices',
           subcmd=dict(help='indicate a group name',
                       metavar='group'),
           options={"-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true')})

MGG = dict(help='manage a group of devices',
           desc='add/remove one or more devices to/from a group',
           subcmd=dict(help='group name',
                       metavar='group',
                       default='UPY_G',
                       nargs='?'),
           options={"-g": dict(help='looks for configuration in global path',
                               required=False,
                               default=False,
                               action='store_true'),
                    "-add": dict(help='add device/s name',
                                 required=False,
                                 nargs='*'),
                    "-rm": dict(help='remove device/s name',
                                required=False,
                                nargs='*'),
                    "-gg": dict(help='manage global group',
                                required=False,
                                default=False,
                                action='store_true')})

MKSG = dict(help='manage a subgroup of devices',
            desc='make group from another group with a subset of devices',
            subcmd=dict(help='group name',
                        metavar='group',
                        default='UPY_G',
                        nargs='?'),
            sgroup=dict(help='subgroup name',
                        metavar='subgroup'),
            options={"-g": dict(help='looks for configuration in global path',
                                required=False,
                                default=False,
                                action='store_true'),
                     "-devs": dict(help='add device/s name',
                                   required=True,
                                   nargs='*'),
                     "-gg": dict(help='manage global group',
                                 required=False,
                                 default=False,
                                 action='store_true')})

DM_CMD_DICT_PARSER = {"config": CONFIG, "check": CHECK, "set": SET,
                      "register": REGISTER, "lsdevs": LSDEVS, "mkg": MKG, "gg": GG,
                      "see": SEE, "mgg": MGG, "mksg": MKSG}

usag = """%(prog)s command [options]\n
"""

_help_subcmds = "%(prog)s [command] -h to see further help of any command"

parser = argparse.ArgumentParser(prog="upydev",
                                 description=('device management tools'
                                              + '\n\n'
                                                + _help_subcmds),
                                 formatter_class=rawfmt,
                                 usage=usag, prefix_chars='-')
subparser_cmd = parser.add_subparsers(title='commands', prog='', dest='m',
                                      )

for command, subcmd in DM_CMD_DICT_PARSER.items():
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
        return ' '.join([str(val) for val in v])
    else:
        return v


def load_local_config(gconf):
    try:
        file_conf = 'upydev_.config'
        if file_conf not in os.listdir() or gconf:
            file_conf = os.path.join(UPYDEV_PATH, file_conf)

        with open(file_conf, 'r') as config_file:
            upy_conf = json.loads(config_file.read())
        target = upy_conf.get('addr')
        if not target:
            target = upy_conf.get('ip')
        passwd = upy_conf['passwd']
        if 'name' in upy_conf:
            _dev_name = upy_conf['name']
        else:
            _dev_name = 'upydevice'
    except Exception:
        print('upydev: no device configured (upydev_.config file not found)')
        sh_cmd("config -h")
        sys.exit()

    return (target, passwd, _dev_name)


UPYDEV_PATH = upydev.__path__[0]


def check_zt_group(key, args):
    # check if device in ZeroTier group.
    zt_file_conf = '_zt_upydev_.config'
    zt_file_path = os.path.join(UPYDEV_PATH, zt_file_conf)
    if zt_file_conf in os.listdir(UPYDEV_PATH):
        with open(zt_file_path, 'r', encoding='utf-8') as zt_conf:
            zt_devices = json.loads(zt_conf.read())
            if key in zt_devices:
                args.zt = zt_devices[key]
            else:
                args.zt = False
    return args.zt


def _check_zt_group(key):
    # check if device in ZeroTier group.
    zt_file_conf = '_zt_upydev_.config'
    zt_file_path = os.path.join(UPYDEV_PATH, zt_file_conf)
    zt_dev = False
    if zt_file_conf in os.listdir(UPYDEV_PATH):
        with open(zt_file_path, 'r', encoding='utf-8') as zt_conf:
            zt_devices = json.loads(zt_conf.read())
            if key in zt_devices:
                zt_dev = zt_devices[key]
            else:
                zt_dev = False
    return zt_dev


def address_entry_point(entry_point, group_file='', args=None):
    if group_file == '':
        group_file = 'UPY_G'
    if args.G is not None and args.G != 'UPY_G':
        group_file = args.G
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
        if args.G is not None and args.G != 'UPY_G':
            print(f'Device {entry_point} not configured in {args.G} group')
            print(f"Do '$ upydev see {args.G}' to see devices {args.G} group")
        else:
            print(f'Device {entry_point} not configured in global group')
            print("Do '$ upydev gg' to see devices global group")
        sys.exit()


def see(group, args):
    if not group.endswith('.config'):
        group_file = f'{group}.config'
    else:
        group_file = group
    if group_file not in os.listdir() or args.g:
        group_file = os.path.join(UPYDEV_PATH, group_file)
    with open(group_file, 'r') as _group:
        group_devs = (json.loads(_group.read()))
    print(f'GROUP NAME: {group}')
    print(f'# DEVICES: {len(group_devs.keys())}')
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

        print(f'{tree} {key:10} -> {dev_type:} @ {dev_add:} ')


def devicemanagement_action(args, unkwargs, **kargs):
    _dev_name = kargs.get("device")
    args_dict = {f"-{k}": v for k, v in vars(args).items()
                 if k in dict_arg_options[args.m]}
    args_list = [f"{k} {expand_margs(v)}" if v and not isinstance(v, bool)
                 else filter_bool_opt(k, v) for k, v in args_dict.items()]
    cmd_inp = f"{args.m} {' '.join(unkwargs)} {' '.join(args_list)} "
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
    # sys.exit()
    # CONFIG:
    if command == 'config':
        if args.t is None or args.p is None:
            if args.sec:
                print('Secure config mode:')
                args.t = input('IP of device: ')
                args.p = getpass.getpass(prompt='Password: ', stream=None)
            else:
                if args.t is None:
                    print('Target Address required, see -t')
                    sh_cmd(f"{args.m} -h")
                    sys.exit()
                else:
                    dt = check_device_type(args.t)
                    if dt == 'WebSocketDevice':
                        print('Target Address and Password required, see -t, -p or -sec')
                        sh_cmd(f"{args.m} -h")
                        # see_help(command)
                        sys.exit()
                    elif dt == 'SerialDevice':
                        args.p = 115200
                    else:
                        args.p = 'pass'
        upydev_addr = args.t
        upydev_mdata = args.p
        if vars(args)['@']:
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
                if ':' in args.zt:
                    zt_conf, fwd_dev_conf = args.zt.split(':')
                    fwd_conf, dev_conf = fwd_dev_conf.split('/')
                    zt_devices.update({upydev_name: dict(zt=zt_conf, fwd=fwd_conf,
                                                         dev=dev_conf)})
                else:
                    zt_devices.update({upydev_name: args.zt})
            with open(zt_file_path, 'w', encoding='utf-8') as zt_conf:
                zt_conf.write(json.dumps(zt_devices))
            print('{} {} settings saved in ZeroTier group!'.format(dt, upydev_name))

        sys.exit()

    # UPYDEV LOOKS FOR UPYDEV_.CONFIG FILE
    # if args.t is None:
    #     try:
    #         file_conf = 'upydev_.config'
    #         if file_conf not in os.listdir() or args.g:
    #             file_conf = os.path.join(UPYDEV_PATH, file_conf)
    #
    #         with open(file_conf, 'r') as config_file:
    #             upy_conf = json.loads(config_file.read())
    #         args.t = upy_conf.get('addr')
    #         if not args.t:
    #             args.t = upy_conf.get('ip')
    #         args.p = upy_conf['passwd']
    #         if 'name' in upy_conf:
    #             _dev_name = upy_conf['name']
    #         else:
    #             _dev_name = 'upydevice'
    #         # @ ENTRY POINT
    #         # if args.b is not None:
    #         #     if "@" in args.b:
    #         #         gf, entryp = args.b.split('@')
    #         #         args.t, args.p = address_entry_point(entryp, gf, args=args)
    #         if vars(args)['@']:
    #             entryp = vars(args)['@'][0]
    #             args.t, args.p = address_entry_point(entryp, args=args)
    #         if args.apmd:
    #             args.t = '192.168.4.1'
    #         if args.st:
    #             print('Target:{}'.format(args.t))
    #     except Exception:
    #         print('upydev_.config file not found, please provide target and password or\
    #          create config file with command "config"')
    #         see_help('config')
    #         sys.exit()

    # CHECK

    if command == 'check':
        if vars(args)['@']:
            space = ''
            for dev in vars(args)['@']:
                try:
                    target, passwd = address_entry_point(dev, args=args)
                    print('{}Device: {}'.format(space, dev))
                    dt = check_device_type(target)
                    if not args.i:
                        zt_dev = _check_zt_group(dev)
                        _target = target
                        if isinstance(zt_dev, dict):
                            _target = f"{target}/{zt_dev['dev']}"
                        print('Address: {}, Device Type: {}'.format(_target, dt))
                    else:
                        if not args.wss:
                            dev = Device(target, passwd, init=True)
                        else:
                            dev = Device(target, passwd, init=True,
                                         ssl=True, auth=args.wss)
                        print(dev)
                except Exception as e:
                    print(e)
                space = '\n'
        else:
            target, passwd, _dev_name = load_local_config(args.g)
            print('Device: {}'.format(_dev_name))
            dt = check_device_type(target)
            if not args.i:
                zt_dev = _check_zt_group(_dev_name)
                _target = target
                if isinstance(zt_dev, dict):
                    _target = f"{target}/{zt_dev['dev']}"
                print('Address: {}, Device Type: {}'.format(_target, dt))
            else:
                if not args.wss:
                    dev = Device(target, passwd, init=True)
                else:
                    dev = Device(target, passwd, init=True, ssl=True, auth=args.wss)
                print(dev)
        sys.exit()

    # SET
    elif command == 'set':
        if vars(args)['@']:
            dev = vars(args)['@']
            target, passwd = address_entry_point(dev, args=args)
            dt = check_device_type(target)
            upydev_name = dev
            print('Setting {}: {}'.format(dt, dev))
        else:
            target, passwd, _dev_name = load_local_config(args.g)
            dt = check_device_type(target)
            print('Setting {}: {}'.format(dt, _dev_name))
            upydev_name = _dev_name
        upydev_ip = target
        upydev_pass = passwd
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

    # REGISTER
    elif command == 'register':
        filename = ''
        if args.s:
            filename = args.s
        else:
            if '.profile' in os.listdir(os.environ['HOME']):
                filename = os.path.join(os.environ['HOME'], '.profile')
            elif '.bashrc' in os.listdir(os.environ['HOME']):
                filename = os.path.join(os.environ['HOME'], '.brashrc')
            else:
                filename = 'upydevs_config.sh'
        if vars(args)['@']:
            space = ''
            if not args.gg:

                if not rest_args:
                    for dev in vars(args)['@']:
                        try:
                            print(f'{space}Registering Device: {dev} ...')
                            with open(filename, 'a') as filereg:
                                filereg.write(f'\n#UPYDEV DEVICE {dev}\n')
                                sc = '{ ' + f'upydev "$@" -@ {dev}; ' + '}'
                                filereg.write(f'function {dev}() {sc}\n')
                                comp_func = "function _argcomp_upydev() { _python_argcomplete upydev; }\n"
                                comp = f"complete -o bashdefault -o default -o nospace -F _argcomp_upydev {dev}\n"
                                filereg.write(comp_func)
                                filereg.write(comp)
                            print(f'Device: {dev} registered')

                        except Exception as e:
                            print(e)
                        space = '\n'
                else:
                    for psname, dev in dict(zip(rest_args, vars(args)['@'])).items():
                        try:
                            print(f'{space}Registering Device: {dev} ...')
                            with open(filename, 'a') as filereg:
                                filereg.write(f'\n#UPYDEV DEVICE {dev}\n')
                                sc = '{ ' + f'upydev "$@" -@ {dev}; ' + '}'
                                filereg.write(f'function {psname}() {sc}\n')
                                comp_func = "function _argcomp_upydev() { _python_argcomplete upydev; }\n"
                                comp = f"complete -o bashdefault -o default -o nospace -F _argcomp_upydev {psname}\n"
                                filereg.write(comp_func)
                                filereg.write(comp)
                            print(f'Device: {dev} registered as {psname}')

                        except Exception as e:
                            print(e)
                        space = '\n'
            else:
                # register group
                group_name = rest_args[0]
                if vars(args)['@']:
                    devs_in_group = ' '.join(vars(args)['@'])
                    try:
                        print(f'{space}Registering Group: {group_name} ...')
                        with open(filename, 'a') as filereg:
                            filereg.write(f'\n#UPYDEV GROUP {group_name}\n')
                            sc = '{ ' + f'upydev "$@" -@ {devs_in_group}; ' + '}'
                            filereg.write(f'function {group_name}() {sc}\n')
                            comp_func = ("function _argcomp_upydev() "
                                         "{ _python_argcomplete upydev; }\n")
                            comp = ("complete -o bashdefault -o default -o nospace "
                                    f"-F _argcomp_upydev {group_name}\n")
                            filereg.write(comp_func)
                            filereg.write(comp)
                        print(f'Group: {group_name} registered')

                    except Exception as e:
                        print(e)
                    space = '\n'
        else:
            if rest_args:
                psname = rest_args[0]
            else:
                add, pswd, _dev_name = load_local_config(args.g)
                psname = _dev_name

            print(f'Registering Device: {_dev_name} ...')
            with open(filename, 'a') as filereg:
                filereg.write(f'\n#UPYDEV DEVICE {_dev_name}\n')
                sc = '{ ' + f'upydev "$@" -@ {_dev_name}; ' + '}'
                filereg.write(f'function {psname}() {sc}\n')
                comp_func = "function _argcomp_upydev() { _python_argcomplete upydev; }\n"
                comp = f"complete -o bashdefault -o default -o nospace -F _argcomp_upydev {psname}\n"
                filereg.write(comp_func)
                filereg.write(comp)

            if rest_args:
                print(f'Device: {_dev_name} registered as {rest_args[0]}')
            else:
                print(f'Device: {_dev_name} registered')

        print(f'Reload {os.path.split(filename)[-1]} with "$ source {filename}" '
              'or open a new terminal to apply the new command')
        sys.exit()

    # LSDEVS
    elif command == 'lsdevs':
        lsdevs_func = False
        filename = ''
        if args.s:
            filename = os.path.expanduser(args.s)
        else:
            if '.profile' in os.listdir(os.environ['HOME']):
                filename = os.path.join(os.environ['HOME'], '.profile')
            elif '.bashrc' in os.listdir(os.environ['HOME']):
                filename = os.path.join(os.environ['HOME'], '.brashrc')
            else:
                filename = 'upydevs_config.sh'
        with open(filename, 'r') as devsconfig:
            lines = devsconfig.read().splitlines()
            for ln, line in enumerate(lines):
                if '#UPYDEV DEVICE' in line:
                    dev = line.split()[-1]
                    dev_alias = lines[ln+1].split()[1].replace('()', '')
                    addr, psswd = address_entry_point(dev, args=args)
                    if dev != dev_alias:
                        print(f'Device: {dev} registered as {dev_alias}')
                    else:
                        print(f'Device: {dev}')
                    dt = check_device_type(addr)
                    print(f'Address: {addr}, Device Type: {dt}', end='\n\n')
                elif '#UPYDEV LSDEVS' in line:
                    lsdevs_func = True
                elif 'function lsdevs() { upydev lsdevs; }' in line:
                    lsdevs_func = True
                elif '#UPYDEV GROUP' in line:
                    group = line.split()[-1]
                    group_alias = lines[ln+1].split()[1].replace('()', '')
                    devs = lines[ln+1].split('-@')[-1].split(';')[0].split()
                    print(f'Group: {group}')
                    for dev in devs:
                        addr, psswd = address_entry_point(dev, args=args)
                        dt = check_device_type(addr)
                        if dev != devs[-1]:
                            tree = '┣━'
                            cont = '┃'
                        else:
                            tree = '┗━'
                            cont = ' '
                        print(f'{" ":^2}{tree}Device: {dev}')
                        print(f'{" ":^2}{cont} Address: {addr}, Device Type: {dt}',
                              end='\n')
                        print(f'{" ":^2}{cont}')

        if not lsdevs_func:
            with open(filename, 'a') as devsconfig:
                devsconfig.write('\n#UPYDEV LSDEVS\n')
                if args.s:
                    devsconfig.write(
                        'function lsdevs() { upydev lsdevs -s ' + f'{args.s}' + ' ; }\n')
                else:
                    devsconfig.write('function lsdevs() { upydev lsdevs; }\n')
        sys.exit()

    # MAKE_GROUP
    elif command == 'mkg':
        if not rest_args:
            print('Group Name required')
            sys.exit()
        else:
            group_file = '{}.config'.format(rest_args)
            group_dict = {}
        if args.devs:
            group_dict = dict(zip(args.devs[::3], [
                              [args.devs[i], args.devs[i+1]]
                              for i in range(1, len(args.devs) - 1, 3)]))
        if args.g:
            group_file = os.path.join(UPYDEV_PATH, rest_args)
        with open(group_file, 'w') as group:
            group.write(json.dumps(group_dict))

        if args.g:
            print('Group settings saved globally!')
        else:
            print('Group settings saved in working directory!')
        print('Upy devices group created!')
        print('GROUP NAME: {}'.format(rest_args))
        print('# DEVICES: {}'.format(len(group_dict.keys())))
        for key in group_dict.keys():
            dt = check_device_type(group_dict[key][0])
            print('{} -> {} @ {}'.format(key, dt, group_dict[key][0]))
        sys.exit()

    # MANAGE GROUP
    # UPYDEV GROUP COMMAND
    if command == 'gg':
        rest_args = 'UPY_G'
        command = 'see'
        see(rest_args, args)
        sys.exit()

    if command == 'see':
        see(rest_args, args)
        sys.exit()

    if args.gg:
        rest_args = 'UPY_G'
        args.g = True

    if rest_args is not None:
        try:
            group_file = rest_args
            # print(group_file)
            if f'{group_file}.config' not in os.listdir() or args.g:
                group_file = os.path.join(UPYDEV_PATH, group_file)

            if command == 'mgg':
                if args.add is not None:
                    group_dict = dict(zip(args.add[::3], [
                                      [args.add[i], args.add[i + 1]]
                                      for i in range(1, len(args.add)-1, 3)]))
                    with open(f'{group_file}.config', 'r', encoding='utf-8') as group:
                        devices = json.loads(group.read())
                        devices.update(group_dict)
                    with open(f'{group_file}.config', 'w', encoding='utf-8') as group:
                        group.write(json.dumps(devices))
                    print('Upy devices group updated!')
                    print(f"GROUP NAME: {group_file.split('/')[-1]}")
                    print(f'# DEVICES ADDED: {len(group_dict.keys())}')
                    for key in group_dict.keys():
                        dt = check_device_type(group_dict[key][0])
                        print(f'{key} : {dt} @ {group_dict[key][0]}')
                elif args.rm is not None:
                    group_dict_rm = args.rm
                    removed_devs = {}
                    with open(f'{group_file}.config', 'r', encoding='utf-8') as group:
                        devices = json.loads(group.read())
                        for dev in group_dict_rm:
                            # del devices[dev]
                            if dev in devices:
                                removed_devs.update({dev: devices.pop(dev)})
                            else:
                                print(f'Device {dev} not in this group')
                    if removed_devs:
                        with open(f'{group_file}.config', 'w') as group:
                            group.write(json.dumps(devices))
                        print('Upy devices group updated!')
                        print(f"GROUP NAME: {group_file.split('/')[-1]}")
                        print(f'# DEVICES REMOVED: {len(removed_devs.keys())}')
                        for key in removed_devs.keys():
                            dt = check_device_type(removed_devs[key][0])
                            print(f'{key} : {dt} @ {removed_devs[key][0]}')
            elif command == 'mksg':
                # LOAD CONFIG FROM -G
                with open(f'{group_file}.config', 'r', encoding='utf-8') as group:
                    devices = json.loads(group.read())
                    # print(devices)

                # SAVE subgroup
                subgroup_file = f'{args.sgroup}.config'
                subgroup_dict = {}
                if args.devs:
                    for dev in args.devs:
                        subgroup_dict[dev] = devices[dev]

                if args.g:
                    subgroup_file = os.path.join(UPYDEV_PATH, subgroup_file)
                with open(subgroup_file, 'w') as subgroup:
                    subgroup.write(json.dumps(subgroup_dict))

                if args.g:
                    print('Group settings saved globally!')
                else:
                    print('Group settings saved in working directory!')
                print('Upy devices group created!')
                print(f'GROUP NAME: {args.sgroup}')
                print(f'# DEVICES: {len(subgroup_dict.keys())}')
                for key in subgroup_dict.keys():
                    dt = check_device_type(subgroup_dict[key][0])
                    print(f'{key} -> {dt} @ {subgroup_dict[key][0]}')

            sys.exit()
        except Exception as e:
            print(e)
            print('file not found, please create a group first')
            sys.exit()

    # if args.m == 'see':
    #     if args.c:
    #         see_help(args.c)
    #     else:
    #         see_help(args.m)

    sys.exit()
