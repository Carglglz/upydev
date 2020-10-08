from upydevice import Device, DeviceException
from upydev.commandlib import _CMDDICT_
import sys
from upydev.helpinfo import see_help

KEY_N_ARGS = {'sd_enable': ['po']}

VALS_N_ARGS = ['po']


SD_COMMANDS_HELP = """
> SD: Usage '$ upydev COMMAND [opts]'
    * COMMAND:
        - sd_enable: to enable/disable the LDO 3.3V regulator that powers the SD module
                     use -po option to indicate the Pin.
        - sd_init: to initialize the sd card; (spi must be configured first)
                   create sd object and mounts as a filesystem, needs sdcard.py see
                   https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md#sd_init
        - sd_deinit: to unmount sd card
        - sd_auto: experimental command, needs a sd module with sd detection pin
                   and the SD_AM.py script. Enable an Interrupt
                   with the sd detection pin, so it mounts the sd when is detected,
                   and unmount the sd card when is extracted. See more info in:
                   https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md#sd_auto
"""


def sd_command(cmd, *args, **kargs):

    # FILTER KARGS
    if cmd not in KEY_N_ARGS:
        for varg in VALS_N_ARGS:
            if varg in kargs:
                kargs.pop(varg)
    else:
        for varg in VALS_N_ARGS:
            if varg in kargs and varg not in KEY_N_ARGS[cmd]:
                kargs.pop(varg)

    if cmd == 'sd':
        print(SD_COMMANDS_HELP)

    # SD_ENABLE
    elif cmd == 'sd_enable':
        po = kargs.pop('po')
        if po is None:
            print('Pin required, indicate it with -po option')
            see_help(cmd)
        else:
            po = po[0]
            dev = Device(*args, **kargs)
            enabled = dev.cmd(_CMDDICT_['SD_ENABLE'].format(po),
                              silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
            else:
                if enabled:
                    print('SD Enabled')
                else:
                    print('SD not Enabled')
            dev.disconnect()
        sys.exit()

    # SD_INIT
    elif cmd == 'sd_init':
        dev = Device(*args, **kargs)
        print('Initialzing SD card...')
        sd_mounted = dev.cmd(_CMDDICT_['SD_INIT'],
                             silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if sd_mounted:
                print('SD initiated and mounted Successfully!')
            else:
                print('SD could not be initiated.')
        dev.disconnect()
        sys.exit()

    # SD_DEINIT

    elif cmd == 'sd_deinit':
        dev = Device(*args, **kargs)
        print('Deinitialzing SD card...')
        sd_mounted = dev.cmd(_CMDDICT_['SD_DEINIT'],
                             silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        else:
            if not sd_mounted:
                print('SD deinitiated Successfully!')
            else:
                print('SD could not be deinitiated.')
        dev.disconnect()
        sys.exit()
    #
    # SD_AUTO

    elif cmd == 'sd_auto':
        dev = Device(*args, **kargs)
        print('Autodetect SD Card mode enabled')
        dev.wr_cmd(_CMDDICT_['SD_AUTO'], follow=True)
        dev.disconnect()
        sys.exit()
