

SHELL_REPLS_HELP = """
> SHELL-REPLS: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - ssl_wrepl: To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal over SSL sockets;
                     CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default)
                     To see more keybindings info do CTRL-k. By default resets after exit,
                     use -rkey option to refresh the WebREPL password with a new random password,
                     after exit.This passowrd will be stored in the working directory or in global directory with
                     -g option. (This mode needs ssl_repl.py, upysecrets.py for -rfkey)
                     *(Use -nem option to use without encryption (for esp8266))

        - ssl: to access ssl_wrepl in a 'ssh' style command to be used like e.g.:
              "upydev ssl@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
               The device can be accessed as "upydev ssl@foo_device" or redirect any command as e.g.
               "upydev ping -@foo_device". *(For esp8266 use the option -nem (no encryption mode))

        - sh_srepl: To enter the serial terminal SHELL-REPL; CTRL-x to exit,
                    To see more keybindings info do CTRL-k. By default resets after exit.
                    To configure a serial device use -t for baudrate and -p for serial port
                    To access without previous configuration: "sh_srepl -port [serial port] -b [baudrate]"
                    (default baudrate is 115200)
                    To access with previous configuration:
                        - "sh_srepl" (if device configured in current working directory)
                        - "sh_srepl -@ foo_device" (if foo_device is configured in global group 'UPY_G')

        - shr: to access the serial terminal SHELL-REPL in a 'ssh' style command to be used like e.g.:
              "upydev shr@/dev/tty.usbmodem3370377430372" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g.
               "upydev make_group -g -f UPY_G -devs foo_device 115200 /dev/tty.usbmodem3370377430372")
               The device can be accessed as "upydev shr@foo_device"

        - wssl: to access ssl_wrepl if WebSecureREPL is enabled in a 'ssh' style command to be used like e.g.:
              "upydev wssl@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
               then the device can be accessed as "upydev wssl@foo_device"

        - set_wss: To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do 'set_wss', to disable 'set_wss -wss'

        - ble: to access the terminal BleSHELL-REPL (if BleREPL enabled) in a 'ssh' style command to be used like e.g.:
              "upydev ble@[UUID]" or if a device is stored in a global group called "UPY_G" (this
               needs to be created first doing e.g.
               "upydev make_group -g -f UPY_G -devs foo_device UUID PASS")
               The device can be accessed as "upydev ble@foo_device"

        - jupyterc: to run MicroPython upydevice kernel for jupyter console, CTRL-D to exit, %%lsmagic to see magic commands and
                    how to connect to a device either WebREPL (%%websocketconnect) or Serial connection (%%serialconnect).
                    Hit tab to autcomplete magic commands, and MicroPython/Python code.
                    (This needs jupyter and MicroPython upydevice kernel to be installed)"""
