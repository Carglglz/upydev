Mode/Tools
==========

Description


Help
----

> HELP: '$ upydev h' or '$ upydev help' to see help (without optional args)
        '$ upydev -h' or '$ upydev --help' to see full help info.

        - To see help about a any ACTION/COMMAND
          put % before that ACTION/COMMAND as : $ upydev %ACTION

      ACTIONS: help, h, dm, fio, fw, kg, rp, sh, db, gp, gc, wu, sd, pro.



Device Management
-----------------

    ACTIONS : ``config``, ``check``, ``set``, ``make_group``, ``mg_group``, ``see``, ``gg``


      - config :
          to save upy device settings (see -t, -p, -g, -@, -gg), so the target and password arguments wont be required any more. A -gg flag will add the device to the global group (UPY_G)
          (-t target -p password -g global directory -@ device name -gg global group)


      - check:
          to check current device information or with -@ entry point if stored in the global group.

      - set:
          to set current device configuration from a device saved in the global group with -@ entry point

      - make_group:
          to make a group of devices to send commands to. Use -f for the name of the group and -devs option to indicate a name, ip and the password of each board. (To store the group settings globally use -g option)

      - mg_group:
          to manage a group of devices to send commands to. Use -G for the name
          of the group and -add option to add devices (indicate a name, ip and the
          password of each board) or -rm to remove devices (indicated by name)

      - see:
          To get specific info about a devices group use -G option as "see -G [GROUP NAME]"

      - gg:
          To see global group



File IO operations
------------------

> FILEIO: '$ upydev fio' to see help on file input/ouput operations.
    ACTIONS: put, get, sync, d_sync, install, update_upyutils

    Usage '$ upydev ACTION [opts]'
        ACTIONS:
            - put : to upload a file to upy device (see -f, -s, -fre, -dir, -rst)
                    e.g. $ upydev put myfile.py, $ upydev put cwd, $ upydev put \test_\*.py

            - get : to download a file from upy device (see -f, -s, -fre, -dir)

            - sync : for a faster transfer of large files
                (this needs sync_tool.py in upy device) (see -f, -s and -lh)

            - d_sync: to recursively sync a folder in upydevice filesystem use -dir
                        to indicate the folder (must be in cwd), use -tree to see dir
                        structure, to sync to an Sd card mounted as 'sd' use -s sd

            - install : install libs to '/lib' path with upip; indicate lib with -f option

            - update_upyutils: to update the latest versions of sync_tool.py, upylog.py,
                            upynotify.py, upysecrets.py, upysh2.py, ssl_repl.py, uping.py, time_it.py,
                            wss_repl.py and wss_helper.py.


Firmware
--------

> FIRMWARE: '$ upydev fw' to see help on firmware operations.
    ACTIONS: fwr, flash, mpyx

    Usage '$ upydev ACTION [opts]'
      ACTIONS:
          - fwr: to list or get available firmware versions, use -md option to indicate operation:
                  to list do: "upydev fwr -md list -b [BOARD]" board can be e.g. 'esp32','esp8266' or 'PYBD'
                  "upydev fwr -md list latest -b [BOARD]" to see the latest firmware available
                  to get do: "upydev fwr -md get [firmware file]" or "upydev fwr -md get latest -b[BOARD]". For list or get modes the -n option will filter the results further: e.g. -n ota
                  to see available serial ports do: "upydev fwr -md list serial_ports".

          - flash: to flash a firmware file to the upydevice, a serial port must be indicated
                      to flash do: "upydev flash -port [serial port] -f [firmware file]"


          - mpyx : to froze a module/script indicated with -f option, and save some RAM,
                   it uses mpy-cross tool


Keygen
------

> KEYGEN: '$ upydev kg' to see help on keygen operations.
    ACTIONS: gen_rsakey, rf_wrkey, sslgen_key

    Usage '$ upydev ACTION [opts]'
        ACTIONS:
            - gen_rsakey: To generate RSA-2048 bit key that will be shared with the device
                          (it is unique for each device) use -tfkey to send this key to the
                          device (use only if connected directly to the AP of the device or a
                          "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                          upload the key (it is stored in ``upydev.__path__``) by USB/Serial connection.

            - rf_wrkey: To "refresh" the WebREPL password with a new random password derivated from
                        the RSA key previously generated. A token then is sent to the device to generate
                        the same password from the RSA key previously uploaded. This won't leave
                        any clues in the TCP Websocekts packages of the current WebREPL password.
                        (Only the token will be visible; check this using wireshark)
                        (This needs upysecrets.py)

            - sslgen_key: (This needs openssl available in $PATH)
                           To generate ECDSA key and a self-signed certificate to enable SSL sockets
                           This needs a passphrase, that will be required every time the key is loaded.
                           Use -tfkey to upload this key to the device
                           (use only if connected directly to the AP of the device or a
                           "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                           upload the key (it is stored in ``upydev.__path__``) by USB/Serial connection.


REPL
-----

> REPLS: '$ upydev rp' to see help on repls modes.
    ACTIONS: repl, rpl, wrepl, wssrepl, srepl

    Usage '$ upydev ACTION [opts]'
        ACTIONS:
            - repl/rpl: to enter one of the following depending of upydevice type:
                    * WebSocketDevice --> wrepl/wssrepl (with -wss flag)
                    * SerialDeivce --> srepl

            - wrepl : to enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
                    To see more keybindings info do CTRL-k
                    (Added custom keybindings and autocompletion on tab to the previous work
                    see: https://github.com/Hermann-SW/webrepl for the original work)

            - wssrepl : to enter the terminal WebSecureREPL; CTRL-x to exit, CTRL-d to do soft reset
                    To see more keybindings info do CTRL-k. REPL over WebSecureSockets (This needs use of
                    'sslgen_key -tfkey', 'update_upyutils' and enable WebSecureREPL in the device
                    "import wss_repl;wss_repl.start(ssl=True)")

            - srepl : to enter the terminal serial repl using picocom, indicate port by -port option
                    (to exit do CTRL-a, CTRL-x)



SHELL-REPL
----------

> SHELL-REPLS: '$ upydev sh' to see help on shell-repls modes.
    ACTIONS: shell, shl, ssl_wrepl, ssl, sh_srepl, shr, wssl, set_wss, ble, jupyterc


    Usage '$ upydev ACTION [opts]'
    ACTIONS:
    - shell/shl:
    To enter one of the following SHELL-REPLS depending of upydevice type.

        - WebSocketDevice --> ssl_wrepl/wssl (with -wss flag)
        - SerialDeivce --> sh_repl/shr
        - BleDevice --> ble

    - ssl_wrepl: To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal over SSL sockets;
                 CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default)
                 To see more keybindings info do CTRL-k. By default resets after exit,
                 use -rkey option to refresh the WebREPL password with a new random password,
                 after exit.This passowrd will be stored in the working directory or in global directory with
                 -g option. (This mode needs ssl_repl.py, upysecrets.py for -rfkey)
                 *(Use -nem option to use without encryption (for esp8266))*

    - ssl: to access ssl_wrepl in a 'ssh' style command to be used like e.g.:
          "upydev ssl@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this
           needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
           The device can be accessed as "upydev ssl@foo_device" or redirect any command as e.g.
           "upydev ping -@foo_device". *(For esp8266 use the option -nem (no encryption mode))*

    - sh_srepl: To enter the serial terminal SHELL-REPL; CTRL-x to exit,
                To see more keybindings info do CTRL-k. By default resets after exit.
                To configure a serial device use -t for baudrate and -p for serial port
                To access without previous configuration: "sh_srepl -port [serial port] -b [baudrate]"
                (default baudrate is 115200)
                To access with previous configuration.
                > "sh_srepl" (if device configured in current working directory)
                > "sh_srepl -@ foo_device" (if foo_device is configured in global group 'UPY_G')

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

    - jupyterc: to run MicroPython upydevice kernel for jupyter console, CTRL-D to exit,
                %%lsmagic to see magic commands and how to connect to a
                device either WebREPL (%%websocketconnect) or Serial connection (%%serialconnect).
                Hit tab to autcomplete magic commands, and MicroPython/Python code.
                (This needs jupyter and MicroPython upydevice kernel to be installed)


Debugging
---------

> DEBUGGING: '$ upydev db' to see help on debugging operations.
    ACTIONS: ping, probe, scan, run, timeit, diagnose, errlog, stream_test,
             sysctl, log, debug, pytest

  Usage '$ upydev ACTION [opts]'
   ACTIONS:
       - ping : pings the target to see if it is reachable, CTRL-C to stop

       - probe: to test if a device is reachable, use -gg flag for global group and -devs
                to filter which ones.
       - scan: to scan for devices, use with -sr [serial], -nt [network], or -bl [ble],
               if no flag, provided will do all three scans.

       - run : just calls import 'script', where 'script' is indicated by -f option
               (script must be in upydevice or in sd card indicated by -s option
               and the sd card must be already mounted as 'sd');
               * Supports CTRL-C to stop the execution and exits nicely.

       - timeit: to measure execution time of a module/script indicated with -f option.
                 This is an implementation of
                 https://github.com/peterhinch/micropython-samples/tree/master/timed_function

       - diagnose: to make a diagnostic test of the device (sends useful to commands
                   to get device state info), to save report to file see -rep, use -n to save
                   the report with a custom name (automatic name is "upyd_ID_DATETIME.txt")
                   Use "-md local" option if connected to esp AP.

       - errlog: if 'error.log' is present in the upydevice, this shows the content
                   (cat('error.log')), if 'error.log' in sd use -s sd

       - stream_test: to test download speed (from device to host). Default test is 10 MB of
                      random bytes are sent in chunks of 20 kB and received in chunks of 32 kB.
                      To change test parameters use -chunk_tx , -chunk_rx, and -total_size.

       - sysctl : to start/stop a script without following the output. To follow initiate
                  wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl)
                  TO START: use -start [SCRIPT_NAME], TO STOP: use -stop [SCRIPT_NAME]

       - log: to log the output of a upydevice script, indicate script with -f option, and
               the sys.stdout log level and file log level with -dslev and -dflev (defaults
               are debug for sys.stdout and error for file). To log in background use -daemon
               option, then the log will be redirected to a file with level -dslev.
               To stop the 'daemon' log mode use -stopd and indicate script with -f option.
               'Normal' file log and 'Daemon' file log are under .upydev_logs folder in $HOME
               directory, named after the name of the script. To follow an on going 'daemon'
               mode log, use -follow option and indicate the script with -f option.

       - debug: to execute a local script line by line in the target upydevice, use -f option
               to indicate the file. To enter next line press ENTER, to finish PRESS C
               then ENTER. To break a while loop do CTRL+C.

       - pytest: to run upydevice test with pytest, do "pytest-setup" first to enable selection
                of specific device with -@ entry point.



Group Mode
----------

> GROUP COMMAND MODE: '$ upydev gp' to see help on group mode options.
    OPTIONS: -G, -GP

    > GROUP COMMAND MODE:
        To send a command to multiple devices in a group (made with make_group command)

        To target specific devices within a group add -devs option as -devs [DEV NAME] [DEV NAME] ...

        *(upydev will use local working directory configuration unless it does
        not find any or manually indicated with -g option)*

        COMMAND MODE OPTION:
            -G : Usage '$ upydev ACTION -G GROUPNAME [opts]' or
                       '$ upydev ACTION -gg [opts]' for global group.
                        This sends the command to one device at a time;

            -GP: Usage '$ upydev ACTION -GP GROUPNAME [opts]' or
                       '$ upydev ACTION -ggp [opts]' for global group.
                       For parallel/non-blocking command execution using multiprocessing
