Mode/Tools
==========



Help
----
  ACTIONS: ``help``, ``h``, ``dm``, ``fio``, ``fw``, ``kg``, ``rp``, ``sh``, ``db``, ``gp``, ``gc``, ``wu``, ``sd``, ``pro``, ``docs``, ``udocs``, ``mdocs``.

        - help:
              to see help about upydev. (Same as ``h``, or use ``-h`` to see information about optional args too)

        - dm:
              to see help about device management.

        - fio:
              to see help on file input/ouput operations.

        - fw:
              to see help on firmware operations.

        - kg:
              to see help on keygen operations.

        - rp:
              to see to see help on REPL modes.

        - sh:
              to see help on SHELL-REPL modes.

        - db:
              to see help on debugging operations.

        - gp:
              to see help on group mode options.

        - gc:
              to see General commmands help.

        - wu:
              to see Wifi utils commands help.

        - sd:
              to see SD utils commands help.

        - pro:
              to see Prototype utils commands help.

.. note::

          To see help about a any ACTION/COMMAND
          Use ``%`` before that ACTION/COMMAND as : ``$ upydev %ACTION``


.. note::

         To see docs about ``upydev``, ``upydevice`` or ``MicroPython`` use ``docs``, ``udocs``,
         ``mdocs``, respectively. Use a keyword as second argument for keyword search.



Device Management
-----------------

    ACTIONS : ``config``, ``check``, ``set``, ``register``, ``make_group``, ``mg_group``, ``make_sgroup``, ``see``, ``gg``


      - config:
          To save upy device settings (see ``-t``, ``-p``, ``-g``, ``-@``, ``-gg``), so the target and password arguments wont be required any more. A ``-gg`` flag will add the device to the global group (``UPY_G``)
          (``-t`` target ``-p`` password ``-g`` global directory ``-@`` device name ``-gg`` global group)


      - check:
          To check current device information or with ``-@`` entry point if stored in the global group. Use ``-i`` flag if device is online/connected to get more info.

      - set:
          To set current device configuration from a device saved in the global group with ``-@`` entry point

      - register:
          To register a device name as a bash function so it can be called from the command line and pass any args to ``upydev``. This adds the function in ``~/.profile`` or ``~/.brashrc`` or any other config file indicated with ``-s`` option

      - make_group:
          To make a group of devices to send commands to. Use ``-f`` for the name of the group and ``-devs`` option to indicate a name, ip and the password of each board. (To store the group settings globally use ``-g`` option)

      - mg_group:
          To manage a group of devices to send commands to. Use ``-G`` for the name
          of the group and ``-add`` option to add devices (indicate a name, ip and the
          password of each board) or ``-rm`` to remove devices (indicated by name)

      - make_sgroup:
          To make a subset group of an existing group, alias ``mksg``.  Use -f for the name
          of the subgroup, -G for the name of parent group and -devs option to indicate the names
          of the devices to include.

      - see:
          To get specific info about a devices group use ``-G`` option as ``see -G [GROUP NAME]``

      - gg:
          To see global group



File IO operations
------------------

    ACTIONS: ``put``, ``get``, ``fget``, ``dsync``, ``rsync``, ``backup``, ``install``, ``update_upyutils``


      - put:
          To upload a file to upy device (see ``-f``, ``-s``, ``-fre``, ``-dir``, ``-rst``, ``-wdl``)
          e.g. ``$ upydev put myfile.py``, ``$ upydev put cwd``, ``$ upydev put \test_\*.py``

      - get:
          To download a file from upy device (see ``-f``, ``-s``, ``-fre``, ``-dir``, ``-wdl``)

      - fget:
          For a faster transfer of large files (this needs `sync_tool.py <https://upydev.readthedocs.io/en/latest/upyutilsinfo.html>`_ in upy device) (see ``-f``, ``-s``, ``-lh``, ``-wdl``)

      - dsync:
          To recursively sync a folder in upydevice filesystem
          where second arg is the directory (can be current working directory too ``.``),
          Otherwise use ``-dir`` to indicate the folder (must be in cwd).
          To sync to an Sd card mounted as ``sd`` use ``-s sd``.
          Use ``-rf`` to remove files or directories deleted in local dir.
          Use ``-d`` flag to sync from device to host.
          Use ``-wdl`` flag to sync only modified files.

      - rsync:
          Same as ``dsync [DIR] -rf -wdl``. To recursively sync only modified files. (deleting files too)

      - backup:
          Same as ``dsync . -d`` to make a backup of the device filesystem.

      - install:
          Install libs to '/lib' path with upip; indicate lib with ``-f`` option

      - update_upyutils:
          To update the latest versions of *sync_tool.py, upylog.py,
          upynotify.py, upysecrets.py, upysh2.py, ssl_repl.py, uping.py, time_it.py,
          wss_repl.py and wss_helper.py.*


Firmware
--------

    ACTIONS: ``fwr``, ``flash``, ``ota``, ``mpyx``


    - fwr:
        To list or get available firmware versions, use ``-md`` option to indicate operation:
        to list do: ``$ upydev fwr -md list -b [BOARD]`` board can be e.g. 'esp32','esp8266' or 'PYBD'
        ``$ upydev fwr -md list latest -b [BOARD]`` to see the latest firmware available
        to get do: ``$ upydev fwr -md get [firmware file]`` or ``$ upydev fwr -md get latest -b[BOARD]``. For list or get modes the ``-n`` option will filter the results further: e.g. ``-n ota``
        to see available serial ports do: ``upydev fwr -md list serial_ports``.

    - flash:
        To flash a firmware file to the upydevice, it uses a SerialDevice configuration or indicate serial port
        e.g. ``upydev flash [firmware_file].bin``, ``upydev flash -f [firmware file] -@ myserialdevice``
        or with serial port: ``upydev flash -port [serial port] -f [firmware file]``
        Use ``-i``, flag to check device platform and firmware match (If using official firmware releases.)

    - ota:
        To do an OTA firmware update. This needs ``ota.py`` or ``otable.py``. Indicate file with ``-f``
        option or as second arg. Use ``-sec`` option for OTA over TLS.

    - mpyx:
        To froze a module/script , and save some RAM, it uses mpy-cross tool (mpy-cross must be available in $PATH)
        e.g. ``$ upydev mpyx [FILE].py``,
        ``$ upydev mpyx [FILE].py [FILE2].py``,
        ``$ upydev mpyx *.py``.


Keygen
------


    ACTIONS: ``gen_rsakey``, ``rsa_sign``, ``rsa_verify``, ``rf_wrkey``, ``sslgen_key``


    - gen_rsakey:
        To generate RSA-2048 bit key that will be shared with the device
        (it is unique for each device) use ``-tfkey`` to send this key to the
        device (use only if connected directly by USB, the AP of the device or a
        "secure" wifi e.g. local/home). Alternative alias, ``$ upydev kg rsa``,
        ``$ upydev keygen rsa``

    - rsa_sign:
        To sign a file with device RSA key, (``rsa`` lib required), use ``-f`` to indicate the file to sign or use alias form: ``$ upydev rsa sign [FILE]``

    - rsa_verify:
        To verify a signature of a file made with device RSA key, use ``-f`` to indicate the signature file to verify or use alias form: ``$ upydev rsa verify [FILE]``

    - rf_wrkey:
        To "refresh" the WebREPL password with a new random password derivated from
        the RSA key previously generated. A token then is sent to the device to generate
        the same password from the RSA key previously uploaded. This won't leave
        any clues in the TCP Websocekts packages of the current WebREPL password.
        (Only the token will be visible; check this using wireshark)
        (This needs upysecrets.py).
        Alternative alias, ``$ upydev kg wr``, ``$ upydev keygen wr``

    - sslgen_key:
        (This needs openssl available in $PATH)
        To generate ECDSA key and a self-signed certificate to enable SSL sockets
        This needs a passphrase, that will be required every time the key is loaded.
        Use ``-tfkey`` to upload this key to the device
        (use only if connected directly by USB, the AP of the device or a
        "secure" wifi e.g. local/home).
        Use ``-to [serial devname]`` flag with ``-tfkey`` to transfer keys by USB/Serial.
        Alternative alias, ``$ upydev kg ssl``, ``$ upydev keygen ssl``


REPL
-----

    ACTIONS: ``repl``, ``rpl``, ``wrepl``, ``wssrepl``, ``srepl``

    - repl/rpl:
          To enter one of the following depending of upydevice type:
            * WebSocketDevice --> wrepl/wssrepl (with ``-wss`` flag)
            * SerialDeivce --> srepl

    - wrepl:
          To enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
          To see more keybindings info do CTRL-k

    - wssrepl:
          To enter the terminal WebSecureREPL; CTRL-x to exit, CTRL-d to do soft reset
          To see more keybindings info do CTRL-k. REPL over WebSecureSockets (This needs use of
          ``sslgen_key -tfkey``, ``update_upyutils`` and enable WebSecureREPL in the device
          ``import wss_repl;wss_repl.start(ssl=True)``)

    - srepl:
          To enter the terminal serial repl using picocom, indicate port by -port option
          (to exit do CTRL-a, CTRL-x)



SHELL-REPL
----------

    ACTIONS: ``shell``, ``shl``, ``ssl_wrepl``, ``ssl``, ``sh_srepl``, ``shr``, ``wssl``, ``set_wss``, ``ble``, ``jupyterc``


    - shell/shl:
        To enter one of the following SHELL-REPLS depending of upydevice type.

        - WebSocketDevice --> ssl_wrepl/wssl (with ``-wss`` flag)
        - SerialDeivce --> sh_repl/shr
        - BleDevice --> ble

      e.g. ``$ upydev shl``, ``$ upydev shl@mydevice``

      It has autocompletion on TAB for available devices.

    - ssl_wrepl:
          To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal over SSL sockets;
          CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default)
          To see more keybindings info do CTRL-k. By default resets after exit,
          use ``-rkey`` option to refresh the WebREPL password with a new random password,
          after exit.This passowrd will be stored in the working directory or in global directory with
          ``-g`` option. (This mode needs *ssl_repl.py, upysecrets.py* for ``-rfkey``)

          Use ``-nem`` option to use just WebREPL (websockets without encryption for esp8266)
          Use ``-zt [HOST ZEROTIER IP/BRIDGE IP]`` option to for devices connected through zerotier network.
          (this can be avoided adding the ``-zt [HOST ZEROTIER IP/BRIDGE IP]`` option when configuring a device)

    - ssl:
          Alias of ``ssl_wrepl``. To access ssl_wrepl in a 'ssh' style command to be used like e.g.:
          ``$ upydev ssl@192.168.1.42`` or if a device is stored in the global group called ``UPY_G``
          the device can be accessed as ``$ upydev ssl@foo_device``

    - sh_srepl:
          To enter the serial terminal SHELL-REPL; CTRL-x to exit,
          To see more keybindings info do CTRL-k.
          By default resets after exit.

          To access without previous configuration: ``$ upydev sh_srepl -port [serial port] -b [baudrate]``
          (default baudrate is 115200)

          To access with previous configuration.
          > ``sh_srepl`` (if device configured in current working directory)
          > ``sh_srepl -@ foo_device`` (if ``foo_device`` is configured in global group ``UPY_G``)

    - shr:
          Alias of ``sh_srepl``
          To access the serial terminal SHELL-REPL in a 'ssh' style command to be used like e.g.:
          ``$ upydev shr@/dev/tty.usbmodem3370377430372`` or if a device is stored in the global group called ``UPY_G``
          The device can be accessed as ``$ upydev shr@foo_device`` (if ``foo_device`` is configured in global group ``UPY_G``)

    - wssl:
          To access ``ssl_wrepl`` if WebSecureREPL is enabled in a 'ssh' style command to be used like e.g.:
          ``$ upydev wssl@192.168.1.42`` or if a device is stored in a global group called ``UPY_G``
          the device can be accessed as ``$ upydev wssl@foo_device`` (if ``foo_device`` is configured in global group ``UPY_G``)

    - set_wss:
          To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do ``$ upydev set_wss``, to disable ``$ upydev set_wss -wss``

    - ble:
          To access the terminal BleSHELL-REPL (if BleREPL enabled) in a 'ssh' style command to be used like e.g.:
          ``$ upydev ble@[UUID]``` or if a device is stored in a global group called ``UPY_G``
          The device can be accessed as ``$ upydev ble@foo_device`` (if ``foo_device`` is configured in global group ``UPY_G``)

    - jupyterc:
          To run MicroPython upydevice kernel for jupyter console, CTRL-D to exit,
          %%lsmagic to see magic commands and how to connect to a
          device either WebREPL (%%websocketconnect) or Serial connection (%%serialconnect).
          Hit tab to autcomplete magic commands, and MicroPython/Python code.
          (This needs jupyter and MicroPython upydevice kernel to be installed)


Debugging
---------


    ACTIONS: ``ping``, ``probe``, ``scan``, ``run``, ``timeit``, ``diagnose``, ``errlog``, ``stream_test``, ``sysctl``, ``log``, ``debug``, ``pytest-setup``, ``pytest``

       - ping:
              pings the target to see if it is reachable, CTRL-C to stop

       - probe:
              To test if a device is reachable, use ``-gg`` flag for global group and ``-devs``
              to filter which ones.
       - scan:
              To scan for devices, use with ``-sr`` for serial, ``-nt`` for network, or -bl for bluetooth low energy,
              if no flag provided it will do all three scans.

       - run :
              Same as ``import [SCRIPT]``, where ``[SCRIPT]`` is indicated as second argument or by ``-f`` option
              (script must be in upydevice or in sd card indicated by ``-s`` option
              and the sd card must be already mounted as 'sd').
              *Supports CTRL-C to stop the execution and exits nicely.*
              e.g. ``$ upydev run myscript.py``

       - timeit:
                To measure execution time of a module/script indicated as second argument or by ``-f`` option
                This is an implementation of https://github.com/peterhinch/micropython-samples/tree/master/timed_function
                e.g. ``$ upydev timeit myscript.py``

       - diagnose:
                To make a diagnostic test of the device (sends useful to commands
                to get device state info), to save report to file see ``-rep``, use ``-n`` to save
                the report with a custom name (automatic name is "upyd_ID_DATETIME.txt")
                Use ``-md local`` option if connected to esp AP.

       - errlog:
                If 'error.log' is present in the upydevice, this shows the content
                same as ``$ upydev "cat('error.log')"``, if 'error.log' in sd use ``-s sd``

       - stream_test:
                To test download speed (from device to host). Default test is 10 MB of
                random bytes are sent in chunks of 20 kB and received in chunks of 32 kB.
                To change test parameters use ``-chunk_tx``, ``-chunk_rx``, and ``-total_size``.

       - sysctl :
                To start/stop a script without following the output. To follow initiate
                wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl)
                TO START: use ``-start`` [SCRIPT_NAME], TO STOP: use ``-stop`` [SCRIPT_NAME]

       - log:
              To log the output of a upydevice script, indicate script with ``-f`` option, and
              the sys.stdout log level and file log level with ``-dslev`` and ``-dflev`` (defaults
              are debug for sys.stdout and error for file). To log in background use -daemon
              option, then the log will be redirected to a file with level ``-dslev``.
              To stop the 'daemon' log mode use -stopd and indicate script with ``-f`` option.
              'Normal' file log and 'Daemon' file log are under .upydev_logs folder in $HOME
              directory, named after the name of the script. To follow an on going 'daemon'
              mode log, use ``-follow`` option and indicate the script with ``-f`` option.

       - debug:
              To execute a local script line by line in the target upydevice, use ``-f`` option
              to indicate the file. To enter next line press ENTER, to finish PRESS C
              then ENTER. To break a while loop do CTRL+C.

       - pytest-setup:
              To set ``pytest.ini`` and ``conftest.py`` in current working directory to enable selection
              of specific device with ``-@`` entry point.

       - pytest:
              To run upydevice test with pytest, do ``$ upydev pytest-setup`` first.
              e.g. ``$ upydev pytest mydevicetest.py``


Group Mode
----------

    OPTIONS: ``-G``, ``-GP``


    To send a command to multiple devices in a group (made with make_group command)

    To target specific devices within a group add ``-devs`` option as ``-devs [DEV NAME] [DEV NAME] ...``
    or use ``-@ [DEV NAME] [DEV NAME] ...`` which has autocompletion on tab and accepts group names, \* wildcards or brace expansion.

    e.g. ``$ upydev check -@ esp\*``, ``$ upydev check -@ esp{1..3}``

.. note::
    *upydev will use local working directory  group configuration unless it does
    not find any or manually indicated with -g option*



COMMAND MODE OPTION:
    -G :
      ``$ upydev ACTION -G GROUPNAME [opts]`` or ``$ upydev ACTION -gg [opts]`` for global group.
      This sends the command to one device at a time

    -GP:
      ``$ upydev ACTION -GP GROUPNAME [opts]`` or ``$ upydev ACTION -ggp [opts]`` for global group.
      For parallel/non-blocking command execution using multiprocessing
