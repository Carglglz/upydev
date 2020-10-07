from upydevice import Device, DeviceException
from upydev.commandlib import _CMDDICT_
import sys

KEY_N_ARGS = {'du': ['f', 's'], 'df': ['s'], 'netstat_conn': ['wp'],
              'apconfig': ['ap'], 'i2c_config': ['i2c'],
              'spi_config': ['spi'], 'set_ntptime': ['utc']}

VALS_N_ARGS = ['f', 's', 'wp', 'ap', 'i2c', 'spi', 'utc']


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
    if cmd == 'sd':
        print(SD_COMMANDS_HELP)
