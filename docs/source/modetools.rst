Mode/Tools
==========



Help
----
  ACTIONS: ``help``, ``h``, ``dm``, ``fio``, ``fw``, ``kg``, ``rp``, ``sh``, ``db``, ``gp``, ``gc``, ``docs``, ``udocs``, ``mdocs``.

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


.. note::

          To see help about a any ACTION/COMMAND,
          use ``-h`` after that ACTION/COMMAND as : ``$ upydev ACTION -h``


.. note::

         To see docs about ``upydev``, ``upydevice`` or ``MicroPython`` use ``docs``, ``udocs``,
         ``mdocs``, respectively. Use a keyword as second argument for keyword search.



Device Management
-----------------

    ACTIONS : ``config``, ``check``, ``set``, ``register``, ``lsdevs``, ``mkg``, ``mgg``, ``mksg``, ``see``, ``gg``


      - config:
          To save upy device settings (see ``-t``, ``-p``, ``-g``, ``-@``, ``-gg``), so the target and password arguments wont be required any more. A ``-gg`` flag will add the device to the global group (``UPY_G``)
          (``-t`` target ``-p`` password ``-g`` global directory ``-@`` device name ``-gg`` global group)


      - check:
          To check current device information or with ``-@`` entry point if stored in the global group. Use ``-i`` flag if device is online/connected to get more info.

      - set:
          To set current device configuration from a device saved in the global group with ``-@`` entry point

      - register:
          To register a device name as a shell function so it can be called from the command line and pass any args to ``upydev``. This adds the function in ``~/.profile`` or ``~/.brashrc`` or any other config file indicated with ``-s`` option

      - lsdevs:
          To see which devices are registered, this also defines ``lsdevs`` as a shell function so it can be called directly

      - mkg:
          To make a group of devices to send commands to.

      - mgg:
          To manage a group of devices to send commands to. Use ``-G`` for the name
          of the group and ``-add`` option to add devices (indicate a name, ip and the
          password of each board) or ``-rm`` to remove devices (indicated by name)

      - mksg:
          To make a subset group of an existing group.  Use -f for the name
          of the subgroup, -G for the name of parent group and -devs option to indicate the names
          of the devices to include.

      - see:
          To get specific info about a devices group

      - gg:
          To see global group



File IO operations
------------------

    ACTIONS: ``put``, ``get``, ``dsync``, ``install``, ``update_upyutils``


      - put:
          To upload a file/files/pattern to device.

      - get:
          To download a file/files/pattern from device.

      - dsync:
          To recursively sync a folder/files/pattern from/to device filesystem.

      - install:
          Install libs to '/lib' path with upip.

      - update_upyutils:
          To update the latest versions of *sync_tool.py, nanoglob.py, shasum.py,
          upylog.py, upynotify.py, upysecrets.py, upysh2.py, uping.py, time_it.py,
          wss_repl.py and wss_helper.py.*


Firmware
--------

    ACTIONS: ``fwr``, ``flash``, ``ota``, ``mpyx``


    - fwr:
        To list or get available firmware versions.

    - flash:
        To flash a firmware file in the device.

    - ota:
        To do an OTA firmware update. This needs ``ota.py`` or ``otable.py``.

    - mpyx:
        To froze a module/script , and save some RAM, it uses mpy-cross tool (mpy-cross must be available in $PATH)
        e.g. ``$ upydev mpyx [FILE].py``,
        ``$ upydev mpyx [FILE].py [FILE2].py``,
        ``$ upydev mpyx *.py``.


Keygen
------


    ACTIONS: ``kg rsa``, ``rsa sign``, ``rsa verify``, ``rsa auth``, ``kg wr``, ``kg ssl``



    - kg rsa:
        To generate RSA-2048 bit key that will be shared with the device
        (it is unique for each device) use ``-tfkey`` to send this key to the
        device (use only if connected directly by USB, the AP of the device or a
        "secure" wifi e.g. local/home).
        Use ``-rkey`` option to remove private key from host (only store public key).
        To generate a host key pair use ``kg rsa host``. Then the public key will be sent
        to the device so it can verify or authenticate the host signature.

    - rsa sign:
        To sign a file with device RSA key, ``$ upydev rsa sign [FILE]`` .
        To sign a file with host RSA key: ``$ upydev rsa sign host [FILE]``

    - rsa verify:
        To verify a signature of a file made with device RSA key : ``$ upydev rsa verify [FILE]``.
        To verify in device a signature made with host RSA key: ``$ upydev rsa verify host [FILE]``

    - rsa auth:
        To authenticate a device with RSA encrypted challenge(Public Keys exchange must be done first)

    - kg wr:
        To "refresh" the WebREPL password with a new random password derivated from
        the RSA key previously generated. A token then is sent to the device to generate
        the same password from the RSA key previously uploaded. This won't leave
        any clues in the TCP Websocekts packages of the current WebREPL password.
        (Only the token will be visible; check this using wireshark)
        (This needs upysecrets.py).
        ``$ upydev kg wr``, ``$ upydev keygen wr``

    - kg ssl:
        To generate ECDSA key and a self-signed certificate to enable SSL sockets
        This needs a passphrase, that will be required every time the key is loaded.
        Use ``-tfkey`` to upload this key to the device
        (use only if connected directly by USB, the AP of the device or a
        "secure" wifi e.g. local/home).
        Use ``-to [serial devname]`` flag with ``-tfkey`` to transfer keys by USB/Serial.
        ``$ upydev kg ssl``


REPL
-----

    ACTIONS: ``repl``, ``rpl``,

    - repl/rpl:
          To enter one of the following depending of upydevice type:
            * WebSocketDevice --> WebREPL/WebSecREPL (with ``-wss`` flag)
            * SerialDeivce --> Serial REPL



SHELL-REPL
----------

    ACTIONS: ``shell``, ``shl``, ``shl-config``,  ``set_wss``, ``jupyterc``


    - shell/shl:
        To enter shell-repl

      e.g. ``$ upydev shl``, ``$ upydev shl@mydevice``

      It has autocompletion on TAB for available devices.

    - shl-config:
          To configure shell-repl prompt colors.

    - set_wss:
          To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do ``$ upydev set_wss``, to disable ``$ upydev set_wss -wss``

    - jupyterc:
          To run MicroPython upydevice kernel for jupyter console, CTRL-D to exit,
          %%lsmagic to see magic commands and how to connect to a
          device. Hit tab to autcomplete magic commands and MicroPython/Python code.
          (This needs jupyter and `Jupyter Upydevice kernel <https://github.com/Carglglz/jupyter_upydevice_kernel>`_ to be installed)


Debugging
---------


    ACTIONS: ``ping``, ``probe``, ``scan``, ``run``, ``timeit``, ``stream_test``, ``sysctl``, ``log``, ``pytest setup``, ``pytest``

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


       - pytest setup:
              To set ``pytest.ini`` and ``conftest.py`` in current working directory to enable selection
              of specific device with ``-@`` entry point.

       - pytest:
              To run upydevice test with pytest, do ``$ upydev pytest setup`` first.
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
