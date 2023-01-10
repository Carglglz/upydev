
Examples
=========

Using Config module
-------------------

The :ref:`config <upyutilsinfo:config>` module allows to create and modify configuration
dinamically in the device using ``*_config.py`` files.

.. note::

  Config parameter values accept numbers, *strings* and booleans ``True``, ``False``.
  To use strings, they must be double + single quoted e.g. ``a="'INFO'"``.


Using config module as upydev command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``$ upydev uconfig``, (see help with ``$ upydev uconfig -h``)

.. warning::
   Note the ``u`` to avoid aliasing with ``config`` command.

.. warning::

  config module expects ``/`` to be the root path of the device, if this is not the case add a
  ``root_path.py`` file with this content:

    .. code-block:: python

      RPATH = '/flash'  # change flash for the root path of your device

e.g.

.. code-block:: console

  $ # Add a configuration named test
  $ upydev uconfig add test

  $ # Add parameters and values to test configuration.
  $ upydev uconfig test: a=1 b=True c="'DEBUG'"
  test -> a=1, b=True, c='DEBUG'

  $ # Check configuration files now
  $ upydev uconfig
  test

  $ # Check test configuration file
  $ upydev uconfig test -y  # pretty print flag
  test:
    b: True
    c: DEBUG
    a: 1

After this there should be a file in device cwd ``./`` named ``test_config.py``

To access ``test`` device configuration, e.g. in ``main.py`` or REPL.

.. code-block:: python

    >>> from test_config import TEST
    >>> dir(TEST)
    ['__class__', 'b', 'c', 'a']

    >>> TEST.a
    1
    >>> TEST.b
    True
    >>> TEST.c
    'DEBUG'


Using config module in shell-repl mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Same as above but this time is ``config`` command, e.g

.. code-block:: console

 $ upydev shl
  shell-repl @ pybV1.1
  SerialREPL connected

  MicroPython v1.19.1-217-g5234e1f1e on 2022-07-29; PYBv1.1 with STM32F405RG
  Type "help()" for more information.

  - CTRL-k to see keybindings or -h to see help
  - CTRL-s to toggle shell/repl mode
  - CTRL-x or "exit" to exit
 pyboard@pybV1.1:~ $ config add foo
 pyboard@pybV1.1:~ $ config foo: a=1 b=2 c=3
 foo -> a=1, b=2, c=3
 pyboard@pybV1.1:~ $ config

 foo
 pyboard@pybV1.1:~ $ config foo -y
 foo:
    b: 2
    c: 3
    a: 1


Using config module in a device script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a configuration (only needed one time)

.. code-block:: python

  from config import add_param
  add_param('foo')

This adds a function named ``set_foo`` in ``config.params`` module.

To set ``foo`` configuration parameters

.. code-block:: python

  from config.params import set_foo
  set_foo(a=1, b=2, c=3)

Which creates a ``foo_config.py`` file with a ``FOO`` named tuple.

.. code-block:: python

  >>> from foo_config import FOO
  >>> print(FOO)
  FOOCONFIG(a=1, c=3, b=2)
  >>> FOO.a
  1
  >>> FOO.b
  2
  >>> FOO.c
  3


Using config module in device development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using config module in device ``main.py`` allows to set for example
different run-time modes e.g.

.. code-block:: console

  pyboard@pybV1.1:~ $ config add mode
  pyboard@pybV1.1:~ $ config mode: app=False


Now in device ``main.py``

.. code-block:: python

  from mode_config import MODE
  import my_app

  if MODE.app:
    my_app.run()

  else:
    # this is debug mode
    print('Device ready to debug')
    # or
    my_app.run_debug()

Or set log levels e.g. in combination with ``upylog.py``


.. code-block:: console

  pyboard@pybV1.1:~ $ config add log
  pyboard@pybV1.1:~ $ config log: level="'INFO'"


Now in device ``main.py``

.. code-block:: python

  import upylog
  from log_config import LOG

  upylog.basicConfig(level=LOG.level, format="TIME_LVL_MSG")
  log = upylog.getLogger("pyb", log_to_file=True, rotate=1000)
  log.logfile = "debug.log"

  log.info(f"Device ready")
  log.debug("Just some debug info") # this will not print anything


After a soft reset:

.. code-block:: console

  MPY: sync filesystems
  MPY: soft reboot
  2022-08-16 16:18:39 [pyb] [INFO] Device ready
  MicroPython v1.19.1-217-g5234e1f1e on 2022-07-29; PYBv1.1 with STM32F405RG
  Type "help()" for more information.



Using dsync command
-------------------
.. note::

  To enable ``dsync`` command use ``$ upydev update_upyutils shasum.py upysh.py upysh2.py``
  otherwise only ``dsync -f`` option would be avaible (which will force sync host current
  working directory into device current working directory)

``dsync`` expects current working directory ``./`` to be at the same level of device current
working directory ``./`` which by default is usually  root ``/`` directory.
So let's consider this example project: ``my_project`` with the following structure

.. code-block:: console

  my_project$ tree
  .
  ├── README.md
  ├── configfiles.config
  └── src
      ├── boot.py
      ├── main.py
      └── lib
           └── foo.py

And device filesystem

.. code-block:: console

  .
  ├── boot.py
  ├── main.py
  └── lib
       ├── shasum.py
       └── upysh.py

So to sync ``src`` with device filesystem cd into src and use ``$ upydev dsync``

.. note::
  - Use ``-n`` to make a dry-run so you can see what would be synced.
  - Use ``-i file/pattern file/pattern..`` to ignore any unwanted file.
  - Use ``-p`` to see diff between modified files. (requires ``git`` to be available in $PATH)
  - Use ``-rf`` to remove any file/dir in device filesystem that is not in current host dir structure. (requires ``upysh2.py`` in device)


  If using ``dsync`` from shell-repl mode ``-n`` flag will save the list of files/dirs
  to sync so it can be viewed again with ``dsync -s``, or ``dsync -s -app`` to show and apply.


.. code-block:: console

  my_project$ cd src
  src$ upydev dsync
  dsync: syncing path ./:
  dsync: dirs: OK[✔]
  dsync: syncing new files (1):
  - ./lib/foo.py [0.02 kB]

  ./lib/foo.py -> mydevice:./lib/foo.py

  ./lib/foo.py [0.02 kB]
  ▏███████████████████████████████████████████▏ -  100 % | 0.02/0.02 kB |  0.02 kB/s | 00:01/00:01 s

  1 new file, 0 files changed, 0 files deleted


To sync from device to host use ``-d`` flag.

.. code-block:: console

  src$ upydev dsync -d
  dsync: path ./:
  dsync: dirs: OK[✔]

  dsync: syncing new files (2):
  - ./lib/shasum.py [5.83 kB]
  - ./lib/upysh.py [10.00 kB]

  mydevice:./lib/shasum.py -> ./lib/shasum.py

  ./lib/shasum.py [5.83 kB]
  ▏███████████████████████████████████████████▏ -  100 % | 5.83/5.83 kB |  9.23 kB/s | 00:00/00:00 s

  mydevice:./lib/upysh.py -> ./lib/upysh.py

  ./lib/upysh.py [10.00 kB]
  ▏███████████████████████████████████████████▏ -  100 % | 10.00/10.00 kB | 16.48 kB/s | 00:00/00:00 s

  2 new files, 0 files changed, 0 files deleted

Now host and device filesystem are fully synced.

.. code-block:: console

  src $ tree
      .
      ├── boot.py
      ├── main.py
      └── lib
           ├── foo.py
           ├── shasum.py
           └── upysh.py


.. code-block:: console

  src $ upydev tree
      .
      ├── boot.py
      ├── main.py
      └── lib
           ├── foo.py
           ├── shasum.py
           └── upysh.py

.. note::
  ``tree`` command needs module ``upysh2.py``, that can be uploaded with
  ``$ upydev update_upyutils upysh2.py``. And in this case was already frozen
  in firmware so that's why it doesn't appear in device filesystem.


``dsync`` accepts multiple files/dirs/ or pattern that will filter what to sync
and speed up the syncing process, e.g.

.. code-block:: console

  # only sync lib dir
  src $ upydev dsync lib
  dsync: syncing path ./lib:
  dsync: dirs: OK[✔]
  dsync: files: OK[✔]

  # only sync .py and .html files
  src $ upydev dsync "*.py" "*.html"
  dsync: syncing path ./*.py, ./*.html:
  dsync: dirs: none
  dsync: dirs: none
  dsync: files: OK[✔]


Using tasks files
-----------------
It is possible to create custom tasks yaml files so they can be played like in `ansible <https://github.com/ansible/ansible>`_.
using ``play`` command, check some examples in `upydev/playbooks <https://github.com/Carglglz/upydev/tree/develop/playbooks>`_
e.g. consider this task file ``mytask.yaml``:

.. code-block:: yaml

  ---
  - name: Example playbook
    hosts: espdev, gkesp32, pybV1.1, oble
    tasks:
      - name: Load upysh
        command: "import upysh"
      - name: Check device filesystem
        command: "ls"
      - name: Check memory
        command: "mem"
      - name: Check info
        command: "info && id"
      - name: Raw MP command
        command: "import time;print('hello');led.on();time.sleep(1);led.off()"
        command_nb: "led.on();time.sleep(1);led.off()"
      - name: Test load script
        wait: 5
        load: sample.py

And script ``sample.py``

.. code-block:: python3

  import time

  for i in range(10):
    print(f"This is a loaded script: {i}")
    time.sleep(0.5)

First set the name of the file, in this case ``Example playbook``, then set the devices
or hosts in which the tasks will be run.

.. note:: devices must be already saved in the global group (see :ref:`save device in global group <gettingstarted:Create a configuration file>`)

Finally add tasks using name, and the command to be run.

.. admonition:: Directives

  Accepted directives are:
    - **name**: To indicate the playbook name or a task name
    - **hosts**: List of hosts (devices) (if none, it will use upydev config)
    - **tasks**: To indicate the list of tasks to execute
    - **command**: A command to be executed as in ``shell-repl`` mode or REPL command.
    - **command_nb**: A raw MicroPython command to be executed in non-blocking way.
    - **command_pl**: A command to be executed in parallel (if using multiple devices).
    - **reset**: To reset the device before executing the task.
    - **wait**: To wait x seconds before executing the task.
    - **load**: To load a local script (in cwd or task file directory) and execute in device.
    - **load_pl**: To load a local script and execute in parallel (if using multiple devices).
    - **include**: To filter which hosts will be included in that task.
    - **ignore**: To filter which hosts will be ignored in that task.



.. tip::
  - ``command``:
        This directive accepts commands that are available in ``shell-repl`` mode (see :ref:`shell-repl <shell_repl:shell-repl>`), so several commands can be concatenated with ``&&``.
        Note that it can also accept raw MicroPython commands.
  - ``command_nb``:
        This directive means *non-blocking* so it will send the command and won't wait for the output. Also only raw MicroPython
        commands are accepted.
  - ``command_pl`` and ``load_pl``:
        Won't work with ``BleDevices``
        so they will be ignored or may raise an error. Only exception is for ``pytest`` command
        which will work for all devices.
  - ``hosts``:
        If directive not present, ``play`` will use current upydev config e.g.

        .. code-block:: yaml
          :caption: mytask_no_hosts.yaml

          ---
            - name: Example playbook with no hosts indicated
              tasks:
              - name: Load upysh
                command: "from upysh import ls"
              - name: Check device filesystem
                command: "ls"
              - name: Check memory
                command: "mem"


        .. code-block:: console

            $ upydev play mytask_no_hosts.yaml -@ pybv1.1
            $ # OR
            $ pyb play mytask_no_hosts.yaml
            $ # OR
            $ mydevgroup play mytask_no_hosts.yaml
            $ # OR
            $ upydev play mytask_no_hosts.yaml -@ pybv1.1 espdev gkesp32


To run the tasks file do:

.. code-block:: console

    $ upydev play playbooks/mytask.yaml

    PLAY [Example playbook]
    **********************************************************************************************************************************

    TASK [Gathering Facts]
    **********************************************************************************************************************************

    ok [✔]: [pybV1.1]
    ok [✔]: [gkesp32]
    ok [✔]: [espdev]
    ok [✔]: [oble]

    TASK [Load upysh]
    **********************************************************************************************************************************

    [pybV1.1]: import upysh

    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: import upysh

    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: import upysh

    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: import upysh

    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************


    TASK [Check device filesystem]
    **********************************************************************************************************************************

    [pybV1.1]: ls

    _tmp_script.py                           boot.py                                  debug.log
    debug.log.1                              DIR_TEST                                 dstest
    dummy.py                                 hostname.py                              lib
    log_config.py                            main.py                                  mpy_test.py
    nemastepper.py                           new_dir                                  new_file.py
    pospid.py                                pospid_steppr.py                         README.txt
    root_path.py                             servo_serial.py                          settings_config.py
    stepper.py                               test_code.py                             test_file.txt
    test_main.py                             test_secp256k1.py                        test_to_fail.py
    testnew.py                               udummy.py                                upy_host_pub_rsa6361726c6f73.key
    upy_pub_rsa3c003d000247373038373333.key  upy_pv_rsa3c003d000247373038373333.key
    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: ls

    appble.py                         base_animations.py                ble_flag.py
    boot.py                           dummy.py                          ec-cacert.pem
    error.log                         hostname.py                       http_client_ssl.py
    http_server_ssl.py                http_server_ssl_ecc_pem.py        http_ssl_test.py
    lib                               localname.py                      main.py
    microdot.mpy                      myfile.txt                        myfile.txt.sign
    ROOT_CA_cert.pem                  server.der                        size_config.py
    ssl_auth.py                       SSL_cert_exp.pem                  SSL_certificate7c9ebd3d9df4.der
    SSL_certificate7c9ebd569e5c.der   ssl_config.py                     ssl_context_rsa.py
    ssl_ecc_auth.py                   ssl_flag.py                       SSL_key7c9ebd3d9df4.der
    ssl_rsa_auth.py                   test_code.py                      test_ssl_context_client.py
    test_to_fail.py                   udummy.py                         upy_host_pub_rsa6361726c6f73.key
    upy_host_pub_rsaacde48001122.key  upy_pub_rsa7c9ebd3d9df4.key       upy_pv_rsa7c9ebd3d9df4.key
    webrepl_cfg.py                    wpa_supplicant.config             wpa_supplicant.py

    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: ls

    ap_.config                       appble.py                        blemode_config.py
    boot.py                          buzzertools.py                   dummy.py
    ec-cacert.pem                    ec-cakey.pem                     error.log
    hello_tls_context.py             hostname.py                      lib
    main.py                          main.py.sha256                   microdot.mpy
    remote_wifi_.config              ROOT_CA_cert.pem                 rsa_cert.der
    size_config.py                   src_boot.py                      src_main.py
    SSL_cert_exp.pem                 SSL_certificate30aea4233564.der  ssl_config.py
    SSL_key30aea4233564.der          SSL_key_exp.der                  SSL_key_exp.pem
    test_code.py                     test_config.py                   test_ssl_context_client.py
    test_to_fail.py                  webrepl_cfg.py                   wifi_.config
    wpa_supplicant.config            wpa_supplicant.py
    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: ls

    _tmp_script.py              ble_flag.py                 boot.py                     dummy.py
    error.log                   lib                         localname.py                main.py
    main2.py                    nofile.py                   nofile2.py                  size_config.py
    test_code.py                test_to_fail.py             testble.py
    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************


    TASK [Check memory]
    **********************************************************************************************************************************

    [pybV1.1]: mem

    Memory          Size        Used       Avail        Use%
    RAM          102.336 kB  11.728 kB   90.608 kB    11.5 %
    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: mem

    Memory          Size        Used       Avail        Use%
    RAM          123.136 kB  18.576 kB   104.560 kB   15.1 %
    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: mem

    Memory          Size        Used       Avail        Use%
    RAM          111.168 kB  52.576 kB   58.592 kB    47.3 %
    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: mem

    Memory          Size        Used       Avail        Use%
    RAM          111.168 kB  23.120 kB   88.048 kB    20.8 %
    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************


    TASK [Check info]
    **********************************************************************************************************************************

    [pybV1.1]: info && id

    SerialDevice @ /dev/tty.usbmodem3370377430372, Type: pyboard, Class: SerialDevice
    Firmware: MicroPython v1.19.1-217-g5234e1f1e on 2022-07-29; PYBv1.1 with STM32F405RG
    Pyboard Virtual Comm Port in FS Mode, Manufacturer: MicroPython
    (MAC: 3c:00:3d:00:02:47:37:30:38:37:33:33)
    ID: 3c003d000247373038373333
    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: info && id

    WebSocketDevice @ wss://192.168.1.66:8833, Type: esp32, Class: WebSocketDevice
    Firmware: MicroPython v1.19.1-321-gb9b5404bb on 2022-08-24; 4MB/OTA SSL module with ESP32
    (MAC: 7c:9e:bd:3d:9d:f4, Host Name: gkesp32, RSSI: -69 dBm)
    ID: 7c9ebd3d9df4
    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: info && id

    WebSocketDevice @ wss://192.168.1.53:8833, Type: esp32, Class: WebSocketDevice
    Firmware: MicroPython v1.19.1-304-g5b7abc757-dirty on 2022-08-23; ESP32 module with ESP32
    (MAC: 30:ae:a4:23:35:64, Host Name: espdev, RSSI: -49 dBm)
    ID: 30aea4233564
    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: info && id

    BleDevice @ 00FEFE2D-5983-4D6C-9679-01F732CBA9D9, Type: esp32 , Class: BleDevice
    Firmware: MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; 4MB/OTA BLE module with ESP32
    (MAC: ec:94:cb:54:8e:14, Local Name: oble, RSSI: -63 dBm)
    ID: ec94cb548e14
    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************


    TASK [Raw MP command]
    **********************************************************************************************************************************

    [pybV1.1]: import time;print('hello');led.on();time.sleep(1);led.off()

    hello
    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: import time;print('hello');led.on();time.sleep(1);led.off()

    hello
    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: import time;print('hello');led.on();time.sleep(1);led.off()

    hello
    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: import time;print('hello');led.on();time.sleep(1);led.off()

    hello
    ----------------------------------------------------------------------------------------------------------------------------------
    [pybV1.1]: led.on();time.sleep(1);led.off()

    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: led.on();time.sleep(1);led.off()

    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: led.on();time.sleep(1);led.off()

    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: led.on();time.sleep(1);led.off()

    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************


    TASK [Test load script]
    **********************************************************************************************************************************

    WAIT: DONE
    ----------------------------------------------------------------------------------------------------------------------------------
    [pybV1.1]: loading playbooks/sample.py

    This is a loaded script: 0
    This is a loaded script: 1
    This is a loaded script: 2
    This is a loaded script: 3
    This is a loaded script: 4
    This is a loaded script: 5
    This is a loaded script: 6
    This is a loaded script: 7
    This is a loaded script: 8
    This is a loaded script: 9
    Done!
    ----------------------------------------------------------------------------------------------------------------------------------
    [gkesp32]: loading playbooks/sample.py

    This is a loaded script: 0
    This is a loaded script: 1
    This is a loaded script: 2
    This is a loaded script: 3
    This is a loaded script: 4
    This is a loaded script: 5
    This is a loaded script: 6
    This is a loaded script: 7
    This is a loaded script: 8
    This is a loaded script: 9

    Done!
    ----------------------------------------------------------------------------------------------------------------------------------
    [espdev]: loading playbooks/sample.py

    This is a loaded script: 0
    This is a loaded script: 1
    This is a loaded script: 2
    This is a loaded script: 3
    This is a loaded script: 4
    This is a loaded script: 5
    This is a loaded script: 6
    This is a loaded script: 7
    This is a loaded script: 8
    This is a loaded script: 9

    Done!
    ----------------------------------------------------------------------------------------------------------------------------------
    [oble]: loading playbooks/sample.py


    This is a loaded script: 0
    This is a loaded script: 1
    This is a loaded script: 2
    This is a loaded script: 3
    This is a loaded script: 4
    This is a loaded script: 5
    This is a loaded script: 6
    This is a loaded script: 7
    This is a loaded script: 8
    This is a loaded script: 9

    Done!
    ----------------------------------------------------------------------------------------------------------------------------------
    **********************************************************************************************************************************

It is also possible to filter which tasks to run on each device using
``include`` or ``ignore`` directives, e.g.

.. code-block:: yaml
  :caption: mytask_pll.yaml

  ---
    - name: Example playbook
      hosts: espdev, gkesp32, pybV1.1, oble
      tasks:
        - name: Raw MP Command
          command: "import time;print('hello');led.on();time.sleep(1);led.off()"
          include: pybV1.1
        - name: Raw MP Command Parallel
          command_nb: "led.on();time.sleep(2);led.off()"
          ignore: pybV1.1



.. code-block:: console

    $ upydev play playbooks/mytask_pll.yaml
    PLAY [Example playbook]
    *******************************************************************************************************************************

    TASK [Gathering Facts]
    *******************************************************************************************************************************

    ok [✔]: [pybV1.1]
    ok [✔]: [gkesp32]
    ok [✔]: [espdev]
    ok [✔]: [oble]

    TASK [Raw MP Command]
    *******************************************************************************************************************************

    [pybV1.1]: import time;print('hello');led.on();time.sleep(1);led.off()

    hello
    -------------------------------------------------------------------------------------------------------------------------------
    *******************************************************************************************************************************


    TASK [Raw MP Command Parallel]
    *******************************************************************************************************************************

    [gkesp32]: led.on();time.sleep(2);led.off()

    -------------------------------------------------------------------------------------------------------------------------------
    [espdev]: led.on();time.sleep(2);led.off()

    -------------------------------------------------------------------------------------------------------------------------------
    [oble]: led.on();time.sleep(2);led.off()

    -------------------------------------------------------------------------------------------------------------------------------
    *******************************************************************************************************************************

.. tip:: It is possible to add these tasks and its loaded scripts so they can be run from anywhere, using ``add``, ``rm`` and ``list``.

      - **add**: add a task file (``.yaml``) or script (``.py``) to upydev, e.g.
      - **rm**: remove a task or script file from upydev.
      - **list**: list available tasks in upydev.

      *tasks files and scripts are stored in ~/.upydev_playbooks*


Let's consider this example with ``battery.yaml`` and ``battery.py``

.. code-block:: yaml
  :caption: battery.yaml

  ---
    - name: Check Battery State
      tasks:
        - name: Battery
          load: battery.py
          command: "battery"


.. code-block:: python
  :caption: battery.py

  from machine import ADC
  bat = ADC(Pin(35))
  bat.atten(ADC.ATTN_11DB)

  class Battery:
      def __init__(self, bat=bat):
          self.bat = bat

      def __repr__(self):
          volt =((self.bat.read()*2)/4095)*3.6
          percentage = round((volt - 3.3) / (4.23 - 3.3) * 100, 1)
          return f"Battery Voltage : {round(volt, 2)}, V; Level:{percentage} %"

  battery = Battery()


Adding this to upydev tasks

.. code-block:: console

  $ upydev play add battery.*
  battery.yaml added to upydev tasks.
  battery.py added to upydev tasks scripts.
  $ upydev play battery # will run battery.yaml which loads battery.py in device and get battery state
  PLAY [Check Battery State]
  *******************************************************************************************************************************

  HOSTS TARGET: [espdev]
  HOSTS FOUND : [espdev]
  *******************************************************************************************************************************

  TASK [Gathering Facts]
  *******************************************************************************************************************************

  ok [✔]: [espdev]

  TASK [Battery]
  *******************************************************************************************************************************

  [espdev]: loading battery.py


  Done!
  -------------------------------------------------------------------------------------------------------------------------------
  [espdev]: battery

  Battery Voltage : 4.2, V; Level:96.8 %
  -------------------------------------------------------------------------------------------------------------------------------
  *******************************************************************************************************************************

And after that it is possible to do:

.. code-block:: console

  $ upydev battery
  Battery Voltage : 4.19, V; Level:95.9 %


