

FIRMWARE_HELP = """
> FIRMWARE: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - fwr: to list or get available firmware versions, use -md option to indicate operation:
                to list do: "upydev fwr -md list -b [BOARD]" board can be e.g. 'esp32','esp8266' or 'PYBD'
                            "upydev fwr -md list latest -b [BOARD]" to see the latest firmware available
                to get do: "upydev fwr -md get [firmware file]" or "upydev fwr -md get latest -b[BOARD]"
                * for list or get modes the -n option will filter the results further: e.g. -n ota
                to see available serial ports do: "upydev fwr -md list serial_ports"

        - flash: to flash a firmware file to the upydevice, a serial port must be indicated
                    to flash do: "upydev flash -port [serial port] -f [firmware file]"

        - mpyx : to froze a module/script indicated with -f option, and save some RAM,
                 it uses mpy-cross tool (see https://gitlab.com/alelec/mpy_cross)"""
