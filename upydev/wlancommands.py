from upydevice import Device, DeviceException
from upydev.commandlib import _CMDDICT_
import sys

KEY_N_ARGS = {'wsta_config': ['wp'],
              'wap_config': ['ap']}

VALS_N_ARGS = ['wp', 'ap']

WLAN_UTILS_COMMANDS_HELP = """
> WIFI UTILS: Usage: '$ upydev COMMAND [opts]'
    * (needs wifiutils.py in upydevice, see upyutils in upydev github repo)
    * COMMAND:
        - wlan_init: Initiates wlan util (call this before the following commands)
        - wsta_config: Saves a "netowrk STA" configuration json file in upydevice, use with -wp option as -wp 'ssid' 'password'
        - wap_config: Saves a "netowrk AP" configuration json file in upydevice, use with -ap option as -ap 'ssid' 'password'
        - wsta_conn: Connects to the wlan configured with the command wsta_config
        - wap_conn: Enables the upydevice AP configured with the command wap_config"""


def wlan_command(cmd, *args, **kargs):
    # WLAN UTILS COMMANDS

    # FILTER KARGS
    if cmd not in KEY_N_ARGS:
        for varg in VALS_N_ARGS:
            if varg in kargs:
                kargs.pop(varg)
    else:
        for varg in VALS_N_ARGS:
            if varg in kargs and varg not in KEY_N_ARGS[cmd]:
                kargs.pop(varg)

    # WLAN_INIT
    if cmd == 'wlan_init':
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['WLAN_INIT'])
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            pass
        dev.disconnect()
        sys.exit()

    # WSTA_CONFIG

    elif cmd == 'wsta_config':
        ssid, passwd = kargs.pop('wp')
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['WLAN_CONFIG'].format(ssid, passwd))
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('Wlan {} configured'.format(ssid))
        dev.disconnect()
        sys.exit()

    # WAP_CONFIG

    elif cmd == 'wap_config':
        ssid, passwd = kargs.pop('ap')
        dev = Device(*args, **kargs)
        dev.cmd(_CMDDICT_['WLAN_AP_CONFIG'].format(ssid, passwd))
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            print('access Point {} configured'.format(ssid))
        dev.disconnect()
        sys.exit()

    # WSTA_CONN

    elif cmd == 'wsta_conn':
        dev = Device(*args, **kargs)
        dev.wr_cmd(_CMDDICT_['WLAN_CONN'], follow=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            pass
        dev.disconnect()
        sys.exit()

    # WAP_CONN

    elif cmd == 'wap_conn':
        dev = Device(*args, **kargs)
        dev.wr_cmd(_CMDDICT_['WLAN_AP_CONN'], follow=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            pass
        dev.disconnect()
        sys.exit()

    elif cmd == 'wu':
        print(WLAN_UTILS_COMMANDS_HELP)
        sys.exit()
