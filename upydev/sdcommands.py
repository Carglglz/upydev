from upydevice import DeviceException
from upydev.commandlib import _CMDDICT_


def sd_command(dev, cmd, args):

    # SD_ENABLE
    if cmd == 'enable':
        po = args.po
        enabled = dev.wr_cmd(_CMDDICT_['SD_ENABLE'].format(po),
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
            # dev.disconnect()
        # sys.exit()
        return

    # SD_INIT
    elif cmd == 'init':
        # dev = Device(*args, **kargs)
        # SPI
        dev.wr_cmd("from machine import SPI,Pin;"
                   f"spi = SPI(1, baudrate=10000000, sck=Pin({args.sck}),"
                   f"mosi=Pin({args.mosi}), miso=Pin({args.miso}))")
        dev.wr_cmd(f"cs = Pin({args.cs}, Pin.OUT)")
        print('Initialzing SD card...')
        sd_mounted = dev.wr_cmd(_CMDDICT_['SD_INIT'],
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
        # dev.disconnect()
        return

    # SD_DEINIT

    elif cmd == 'deinit':
        # dev = Device(*args, **kargs)
        print('Deinitialzing SD card...')
        sd_mounted = dev.wr_cmd(_CMDDICT_['SD_DEINIT'],
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
        # dev.disconnect()
        # sys.exit()
        return
    #
    # SD_AUTO

    elif cmd == 'auto':
        # dev = Device(*args, **kargs)
        print('Autodetect SD Card mode enabled')
        dev.wr_cmd(_CMDDICT_['SD_AUTO'], follow=True)
        # dev.disconnect()
        # sys.exit()
        return
