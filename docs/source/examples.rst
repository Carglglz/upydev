
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


Making Test for devices with upydev/upydevice + pytest
------------------------------------------------------

Simple tests definitions
^^^^^^^^^^^^^^^^^^^^^^^^
Using `upydevice/test/ <https://github.com/Carglglz/upydevice/tree/master/test>`_ as a template
is easy to create custom tests for a device, to be run interactively, which can range
from entire modules to single functions, e.g.

.. note:: ``pytest`` and ``pytest-benchmark`` required. Install with
          ``$ pip install pytest pytest-benchmark``

Consider test ``test_blink_led`` from ``test_esp_serial.py``
This will test led ``on()`` and ``off()`` functions:

.. code-block:: python

  def test_blink_led():
    TEST_NAME = 'BLINK LED'
    if dev.dev_platform == 'esp8266':
        _ESP_LED = 2
    elif dev.dev_platform == 'esp32':
        _ESP_LED = 13

    _led = dev.cmd("'led' in globals()", silent=True, rtn_resp=True) # define led if not already defined
    if not _led:
        dev.cmd('from machine import Pin; led = Pin({}, Pin.OUT)'.format(_ESP_LED))

    for i in range(2):
        dev.cmd('led.on();print("LED: ON")')
        time.sleep(0.2)
        dev.cmd('led.off();print("LED: OFF")')
        time.sleep(0.2)
    try:
        assert dev.cmd('not led.value()', silent=True,
                       rtn_resp=True), 'LED is on, should be off'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e

or testing a module ``test_code.py`` in device that will test ``upylog.py`` logging functions.

Consider test ``test_run_script`` from ``test_esp_serial.py``

.. code-block:: python

  def test_run_script(): # the name of the test for pytest
    TEST_NAME = 'RUN SCRIPT' # the name of the test to display in log
    log.info('{} TEST: test_code.py'.format(TEST_NAME))
    dev.wr_cmd('import test_code', follow=True)
    try:
        assert dev.cmd('test_code.RESULT', silent=True,
                       rtn_resp=True) is True, 'Script did NOT RUN'
        dev.cmd("import sys,gc;del(sys.modules['test_code']);gc.collect()") # reloads module
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e

So running this test

.. code-block:: console

  test $ upydev pytest test_esp_serial.py
  Running pytest with Device: sdev
  =========================================== test session starts ===========================================
  platform darwin -- Python 3.7.9, pytest-7.1.2, pluggy-1.0.0
  benchmark: 3.4.1 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
  rootdir: /Users/carlosgilgonzalez/Desktop/MY_PROJECTS/MICROPYTHON/TOOLS/upydevice_.nosync/test, configfile: pytest.ini
  plugins: benchmark-3.4.1
  collected 7 items

  test_esp_serial.py::test_devname PASSED
  test_esp_serial.py::test_platform
  ---------------------------------------------- live log call ----------------------------------------------
  20:09:36 [pytest] [sdev] [ESP32] : Running SerialDevice test...
  20:09:36 [pytest] [sdev] [ESP32] : DEV PLATFORM: esp32
  SerialDevice @ /dev/cu.usbserial-016418E3, Type: esp32, Class: SerialDevice
  Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
  CP2104 USB to UART Bridge Controller, Manufacturer: Silicon Labs
  (MAC: 30:ae:a4:23:35:64)
  20:09:37 [pytest] [sdev] [ESP32] : DEV PLATFORM TEST: [✔]
  Test Result: PASSED
  test_esp_serial.py::test_blink_led LED: ON
  LED: OFF
  LED: ON
  LED: OFF

  ---------------------------------------------- live log call ----------------------------------------------
  20:09:39 [pytest] [sdev] [ESP32] : BLINK LED TEST: [✔]
  Test Result: PASSED
  test_esp_serial.py::test_run_script
  ---------------------------------------------- live log call ----------------------------------------------
  20:09:39 [pytest] [sdev] [ESP32] : RUN SCRIPT TEST: test_code.py
  2022-08-17 19:09:38 [log_test] [INFO] Test message2: 100(foobar)
  2022-08-17 19:09:38 [log_test] [WARN] Test message3: %d(%s)
  2022-08-17 19:09:38 [log_test] [ERROR] Test message4
  2022-08-17 19:09:38 [log_test] [CRIT] Test message5
  2022-08-17 19:09:38 [None] [INFO] Test message6
  2022-08-17 19:09:38 [log_test] [ERROR] Exception Ocurred
  Traceback (most recent call last):
    File "test_code.py", line 14, in <module>
  ZeroDivisionError: divide by zero
  2022-08-17 19:09:38 [errorlog_test] [ERROR] Exception Ocurred
  Traceback (most recent call last):
    File "test_code.py", line 20, in <module>
  ZeroDivisionError: divide by zero
  20:09:40 [pytest] [sdev] [ESP32] : RUN SCRIPT TEST: [✔]
  Test Result: PASSED
  test_esp_serial.py::test_raise_device_exception
  ---------------------------------------------- live log call ----------------------------------------------
  20:09:40 [pytest] [sdev] [ESP32] : DEVICE EXCEPTION TEST: b = 1/0
  [DeviceError]:
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  ZeroDivisionError: divide by zero

  20:09:40 [pytest] [sdev] [ESP32] : DEVICE EXCEPTION TEST: [✔]
  Test Result: PASSED
  test_esp_serial.py::test_reset
  ---------------------------------------------- live log call ----------------------------------------------
  20:09:40 [pytest] [sdev] [ESP32] : DEVICE RESET TEST
  Rebooting device...
  Done!
  20:09:41 [pytest] [sdev] [ESP32] : DEVICE RESET TEST: [✔]
  Test Result: PASSED
  test_esp_serial.py::test_disconnect
  ---------------------------------------------- live log call ----------------------------------------------
  20:09:41 [pytest] [sdev] [ESP32] : DEVICE DISCONNECT TEST
  20:09:41 [pytest] [sdev] [ESP32] : DEVICE DISCONNECT TEST: [✔]
  Test Result: PASSED

  ============================================ 7 passed in 5.08s ============================================

Advanced tests definitions using yaml files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It is possible to use parametric test generation using yaml files e.g.
consider ``test_dev.py`` in `upydev/tests <https://github.com/Carglglz/upydev/tree/master/tests>`_.

Defining a test in a yaml file with the following directives:

.. admonition:: Test Directives

     - **name**: The name of the test
     - **hint**: Info about the test, description, context, etc.
     - **reset**: To reset the device (``soft`` or ``hard``) before running the test.
     - **load**: To load and execute a local file in device (.e.g ``test_basic_math.py``)
     - **command**: The command to run the test in device.
     - **args**: To pass argument to the test function in device.
     - **kwargs**: To pass keyword arguments to the test function in device.
     - **result**: The command to get test result.
     - **exp**: Expected result to assert.
     - **exp_type**: Expected type of result to assert.
     - **assert_op**: Assert operation if other than ``==``.
     - **assert_itr**: Assert elements of iterable result (``any``, or ``all``).
     - **benchmark**: To run a benchmark of the function (device time). (``pytest-benchmark`` plugin required)
     - **bench_host**: To capture benchmark time of device + host (total time)
     - **diff**: To compute diff between device and host benchmark times (i.e. interface latency)
     - **follow**: To follow device benchmark output only (host+device time).
     - **rounds**: Rounds to run the function if doing a benchmark.
     - **unit**: To specify units if the measure is other than time in seconds. (i.e sensors)
     - **network**: To run network tests, (currently only ``iperf3:server``, ``iperf3:client``)
     - **ip**: IP to use in network tests, (``localip``, or ``devip``)
     - **reload**: To reload a script in device so it can be run again .e.g reload ``foo_test`` module if command was ``import foo_test``.


.. note:: **load** can be a command too, .e.g ``import mytestlib`` although it won't return anything (only stdout).

.. tip:: Some directives are mutually exclusive, e.g. the 3 types of tests would be:

      - **Assert** Test: using **command**, **result**, **exp** (with options like **exp_type**, **assert_op**, **assert_itr**)
      - **Benchmark** Test: using **benchmark** with **rounds** and options like **bench_host**, **diff**, **follow**, **unit**...
      - **Network** Test: using **network**, **command**, **ip** to run network tests.

    The directives that should work with any type of test are the rest (
    **name**, **load**, **args**, **kwargs**, **hint**, **reload**, **reset**
    )

.. code-block:: yaml
    :caption: test_load_basic_math.yaml

    ---
      - name: "sum"
        load: ./dev_tests/test_basic_math.py
        command: "a = do_sum"
        args: [1, 1]
        result: a
        exp: 2

      - name: "diff"
        command: "a = do_diff"
        args: [1, 1]
        result: a
        exp: 0

      - name: "product"
        command: "a = do_product"
        args: [2, 2]
        result: a
        exp: 4

      - name: "division"
        command: "a = do_div"
        args: [1, 2]
        result: a
        exp: 0.5


.. code-block:: python
  :caption: ./dev_tests/test_basic_math.py

  def do_sum(a, b):
  return a + b

  def do_diff(a, b):
    return a - b

  def do_div(a, b):
    return a / b

  def do_product(a, b):
    return a * b


.. code-block:: console

  tests $ upydev pytest test_load_basic_math.yaml
  Running pytest with Device: pybV1.1
  ===================================================== test session starts =====================================================
  platform darwin -- Python 3.7.9, pytest-7.1.2, pluggy-1.0.0
  benchmark: 3.4.1 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
  rootdir: /Users/carlosgilgonzalez/Desktop/MY_PROJECTS/MICROPYTHON/TOOLS/upydev_.nosync/tests, configfile: pytest.ini
  plugins: benchmark-3.4.1
  collected 7 items

  test_dev.py::test_devname PASSED
  test_dev.py::test_platform
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : Running SerialDevice test...
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : DEV PLATFORM: pyboard
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : DEV PLATFORM TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[sum]
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : Running [sum] test...
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : Loading ./dev_tests/test_basic_math.py file...
  17:06:44 [pytest] [pybV1.1] [PYBOARD] : Command [a = do_sum(*[1, 1])]
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : expected: 2 --> result: 2
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : sum TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[diff]
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Running [diff] test...
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Command [a = do_diff(*[1, 1])]
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : expected: 0 --> result: 0
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : diff TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[product]
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Running [product] test...
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Command [a = do_product(*[2, 2])]
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : expected: 4 --> result: 4
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : product TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[division]
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Running [division] test...
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : Command [a = do_div(*[1, 2])]
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : expected: 0.5 --> result: 0.5
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : division TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_disconnect
  -------------------------------------------------------- live log call --------------------------------------------------------
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : DEVICE DISCONNECT TEST
  17:06:45 [pytest] [pybV1.1] [PYBOARD] : DEVICE DISCONNECT TEST: [✔]
  Test Result: PASSED

  ====================================================== 7 passed in 1.76s ======================================================

.. note::

	``pytest`` command will by default use ``test_dev.py`` if only yaml files indicated


Running Benchmarks with pytes-benchmark
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See `pytest-benchmark <https://pytest-benchmark.readthedocs.io/en/latest/index.html>`_ documentation

To write a benchmark test use **benchmark** directive to indicate a function that will be
called **rounds** times (default 5).
Consider this example:

.. code-block:: yaml
  :caption: test_pystone_bmk.yaml

    ---
    - name: System Check
      hint: "Device CPU frequency:"
      command: "import machine;machine.freq()"

    - name: Pystone Benchmark
      hint: Run 500 loops, returns time in seconds to complete a run.
      load: "import pystone_lowmem"
      benchmark: "pystone_lowmem.main"
      args: [500, True]
      reload: "pystone_lowmem"

Where the function ``pystone_lowmem.main(500,True)`` will perform a 500 loops run and
return the time that it took **in seconds**.

.. tip::

  Use of ``time.ticks_ms``/``time.ticks_us`` and ``time.ticks_diff`` to obtain the
  time that it takes to run any function and return time in seconds e.g.

  .. code-block:: python

    def benchmark_this(func, *args, **kwargs):
      t0 = time.ticks_ms()
      result = func(*args, **kwargs)
      delta = time.ticks_diff(time.ticks_ms(), t0)
      return delta/1e3 # delta/1e6 if using time.ticks_us


Running ``test_benchmark/test_pystone_bmk.yaml`` benchmark with different devices
and saving benchmark results

.. code-block:: console

    $ pyb pytest test_benchmark/test_pystones_bmk.yaml --benchmark-save=pyb_pystones
    ...
    $ gk32 pytest test_benchmark/test_pystones_bmk.yaml --benchmark-save=gk32_pystones
    ...
    $ sdev pytest test_benchmark/test_pystones_bmk.yaml --benchmark-save=sdev_pystones
    ...
    $ oble pytest test_benchmark/test_pystones_bmk.yaml --benchmark-save=oble_pystones
    ...

It is possible to compare benchmark results e.g.

.. code-block:: console

    $ pytest-benchmark compare "*pystone*"

    --------------------------------------------------------------------------------------------------- benchmark 'device': 4 tests ---------------------------------------------------------------------------------------------------
    Name (time in ms)                                                     Min                 Max                Mean            StdDev              Median               IQR            Outliers     OPS            Rounds  Iterations
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[gkesp32@esp32] (0002_gk32_py)       188.0000 (1.0)      197.0000 (1.0)      192.8000 (1.0)      4.0249 (4.50)     195.0000 (1.0)      6.7500 (5.40)          2;0  5.1867 (1.0)           5           1
    test_dev[Pystone Benchmark]:[pybV1.1@pyboard] (0001_pyb_pys)     262.0000 (1.39)     264.0000 (1.34)     263.4000 (1.37)     0.8944 (1.0)      264.0000 (1.35)     1.2500 (1.0)           1;0  3.7965 (0.73)          5           1
    test_dev[Pystone Benchmark]:[oble@esp32] (0003_oble_py)          264.0000 (1.40)     267.0000 (1.36)     265.2000 (1.38)     1.3038 (1.46)     265.0000 (1.36)     2.2500 (1.80)          1;0  3.7707 (0.73)          5           1
    test_dev[Pystone Benchmark]:[sdev@esp32] (0004_sdev_py)          282.0000 (1.50)     292.0000 (1.48)     288.4000 (1.50)     3.9115 (4.37)     289.0000 (1.48)     4.7500 (3.80)          1;0  3.4674 (0.67)          5           1
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    Legend:
    Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
    OPS: Operations Per Second, computed as 1 / Mean


To see device firmware use ``--group-by=param``

.. code-block:: console

    $ pytest-benchmark compare "*pystone*" --group-by=param

    ---------- benchmark 'Pystone Benchmark @ esp32 micropython-v1.18-128-g2ea21abae-dirty on 2022-02-19 4MB/OTA BLE module with ESP32': 1 tests -----------
    Name (time in ms)                                                Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
    --------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[oble@esp32] (0003_oble_py)     264.0000  267.0000  265.2000  1.3038  265.0000  2.2500       1;0  3.7707       5           1
    --------------------------------------------------------------------------------------------------------------------------------------------------------

    ------------ benchmark 'Pystone Benchmark @ esp32 micropython-v1.19.1-304-g5b7abc757-dirty on 2022-08-23 ESP32 module with ESP32': 1 tests -------------
    Name (time in ms)                                                Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
    --------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[sdev@esp32] (0004_sdev_py)     282.0000  292.0000  288.4000  3.9115  289.0000  4.7500       1;0  3.4674       5           1
    --------------------------------------------------------------------------------------------------------------------------------------------------------

    -------------- benchmark 'Pystone Benchmark @ esp32 micropython-v1.19.1-321-gb9b5404bb on 2022-08-24 4MB/OTA SSL module with ESP32': 1 tests --------------
    Name (time in ms)                                                   Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
    -----------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[gkesp32@esp32] (0002_gk32_py)     188.0000  197.0000  192.8000  4.0249  195.0000  6.7500       2;0  5.1867       5           1
    -----------------------------------------------------------------------------------------------------------------------------------------------------------

    ----------------- benchmark 'Pystone Benchmark @ pyboard micropython-v1.19.1-217-g5234e1f1e on 2022-07-29 PYBv1.1 with STM32F405RG': 1 tests ----------------
    Name (time in ms)                                                     Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
    -------------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[pybV1.1@pyboard] (0001_pyb_pys)     262.0000  264.0000  263.4000  0.8944  264.0000  1.2500       1;0  3.7965       5           1
    -------------------------------------------------------------------------------------------------------------------------------------------------------------

    Legend:
    Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
    OPS: Operations Per Second, computed as 1 / Mean


To see the command/hint/context of the benchmark use ``--group-by=param:cmd``

.. code-block:: console

    $ pytest-benchmark compare "*pys*" --group-by=param:cmd

    benchmark "cmd={'name': 'Pystone Benchmark', 'hint': 'Run 500 loops, returns time in seconds to complete a run.', 'load': 'import pystone_lowmem', 'benchmark': 'pystone_lowmem.main(benchtm=True)', 'reload': 'pystone_lowmem'}": 4 tests
    Name (time in ms)                                                     Min                 Max                Mean            StdDev              Median               IQR            Outliers     OPS            Rounds  Iterations
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    test_dev[Pystone Benchmark]:[gkesp32@esp32] (0002_gk32_py)       188.0000 (1.0)      197.0000 (1.0)      192.8000 (1.0)      4.0249 (4.50)     195.0000 (1.0)      6.7500 (5.40)          2;0  5.1867 (1.0)           5           1
    test_dev[Pystone Benchmark]:[pybV1.1@pyboard] (0001_pyb_pys)     262.0000 (1.39)     264.0000 (1.34)     263.4000 (1.37)     0.8944 (1.0)      264.0000 (1.35)     1.2500 (1.0)           1;0  3.7965 (0.73)          5           1
    test_dev[Pystone Benchmark]:[oble@esp32] (0003_oble_py)          264.0000 (1.40)     267.0000 (1.36)     265.2000 (1.38)     1.3038 (1.46)     265.0000 (1.36)     2.2500 (1.80)          1;0  3.7707 (0.73)          5           1
    test_dev[Pystone Benchmark]:[sdev@esp32] (0004_sdev_py)          282.0000 (1.50)     292.0000 (1.48)     288.4000 (1.50)     3.9115 (4.37)     289.0000 (1.48)     4.7500 (3.80)          1;0  3.4674 (0.67)          5           1
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    Legend:
    Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
    OPS: Operations Per Second, computed as 1 / Mean


It is possible to benchmark measurements other than time, i.e. to benchmark sensor measurements.
Use ``unit`` directive in yaml file to indicate the unit or measurement and unit, e.g.
``unit: "V"`` or ``unit: "voltage:V"``. This also can be set at the command line with
``--unit`` option.

Let's consider this example to take measurements with an ADC sensor ``ADS1115``

.. code-block:: yaml
  :caption: test_ads/test_ads_bmk.yaml

  ---
  - name: i2c_config
    load: "from machine import I2C, Pin"
    command: "i2c=I2C"
    args: "[1]"
    kwargs: "{'scl': Pin(22), 'sda': Pin(23)}"

  - name: i2c_scan
    command: "addr=i2c.scan()"
    result: "i2c.scan()"
    exp: [72]
    exp_type: list

  - name: ads_config
    command: "from ads1115 import ADS1115;sensor=ADS1115(i2c,
             addr[0], 1); sensor.set_conv(7, channel1=0)"

  - name: ads_read
    command: "mv = sensor.raw_to_v(sensor.read())"
    result: mv
    exp: 0
    assert_op: "<="
    exp_type: float

  - name: ADS1115 Benchmark
    hint: Test ADS1115 ADC sensor
    load: "import time"
    benchmark: "[(time.time_ns(), sensor.raw_to_v(sensor.read())) for i in range(100)]"
    unit: "voltage:V"
    rounds: 1


.. code-block:: console

  $ espd pytest test_ads/test_ads_bmk.yaml --benchmark-save=espd_ads1115 --benchmark-save-data
  Running pytest with Device: espdev
  Comparing against benchmarks from: Darwin-CPython-3.7-64bit/0022_espd_ads1115.json
  ===================================================================================================================== test session starts =====================================================================================================================
  platform darwin -- Python 3.7.9, pytest-7.1.2, pluggy-1.0.0
  benchmark: 3.4.1 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
  rootdir: /Users/carlosgilgonzalez/Desktop/MY_PROJECTS/MICROPYTHON/TOOLS/upydev_.nosync/tests, configfile: pytest.ini
  plugins: benchmark-3.4.1
  collected 8 items

  test_dev.py::test_devname PASSED
  test_dev.py::test_platform
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:13 [pytest] [espdev] [ESP32] : Running WebSocketDevice test...
  23:35:13 [pytest] [espdev] [ESP32] : Device: esp32
  23:35:13 [pytest] [espdev] [ESP32] : Firmware: micropython v1.19.1-304-g5b7abc757-dirty on 2022-08-23; ESP32 module with ESP32
  23:35:13 [pytest] [espdev] [ESP32] : DEV PLATFORM TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[i2c_config]
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:13 [pytest] [espdev] [ESP32] : Running [i2c_config] test...
  23:35:13 [pytest] [espdev] [ESP32] : Loading from machi... snippet
  paste mode; Ctrl-C to cancel, Ctrl-D to finish
  === from machine import I2C, Pin


  23:35:14 [pytest] [espdev] [ESP32] : Command [i2c=I2C(*[1], **{'scl': Pin(22), 'sda': Pin(23)})]
  23:35:14 [pytest] [espdev] [ESP32] : i2c_config TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[i2c_scan]
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:14 [pytest] [espdev] [ESP32] : Running [i2c_scan] test...
  23:35:14 [pytest] [espdev] [ESP32] : Command [addr=i2c.scan()]
  23:35:15 [pytest] [espdev] [ESP32] : expected: list --> result: <class 'list'>
  23:35:15 [pytest] [espdev] [ESP32] : expected: [72] == result: [72]
  23:35:15 [pytest] [espdev] [ESP32] : i2c_scan TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[ads_config]
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:15 [pytest] [espdev] [ESP32] : Running [ads_config] test...
  23:35:15 [pytest] [espdev] [ESP32] : Command [from ads1115 import ADS1115;sensor=ADS1115(i2c, addr[0], 1); sensor.set_conv(7, channel1=0)]
  23:35:16 [pytest] [espdev] [ESP32] : ads_config TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[ads_read]
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:16 [pytest] [espdev] [ESP32] : Running [ads_read] test...
  23:35:16 [pytest] [espdev] [ESP32] : Command [mv = sensor.raw_to_v(sensor.read())]
  23:35:17 [pytest] [espdev] [ESP32] : expected: float --> result: <class 'float'>
  23:35:17 [pytest] [espdev] [ESP32] : expected: 0 <= result: 0.5788927
  23:35:17 [pytest] [espdev] [ESP32] : ads_read TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_dev[ADS1115 Benchmark]
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:17 [pytest] [espdev] [ESP32] : Running [ADS1115 Benchmark] test...
  23:35:17 [pytest] [espdev] [ESP32] : Loading import tim... snippet
  paste mode; Ctrl-C to cancel, Ctrl-D to finish
  === import time


  23:35:18 [pytest] [espdev] [ESP32] : Hint: Test ADS1115 ADC sensor
  23:35:18 [pytest] [espdev] [ESP32] : Benchmark Command [[(time.time_ns(), sensor.raw_to_v(sensor.read())) for i in range(100)]]
  [(715559717849154000, 0.5791427), (715559717862555000, 0.5806427), (715559717872601000, 0.5815177), (715559717882546000, 0.5813928), (715559717892413000, 0.5820178), (715559717902349000, 0.5815177), (715559717912478000, 0.5811427), (715559717922413000, 0.5811427), (715559717932291000, 0.5812678), (715559717942212000, 0.5816427), (715559717952415000, 0.5815177), (715559717962345000, 0.5813928), (715559717972224000, 0.5813928), (715559717982118000, 0.5810177), (715559717992065000, 0.5815177), (715559718002000000, 0.5812678), (715559718011880000, 0.5811427), (715559718021805000, 0.5816427), (715559718031787000, 0.5808928), (715559718041728000, 0.5811427), (715559718051652000, 0.5815177), (715559718061669000, 0.5813928), (715559718071616000, 0.5813928), (715559718081553000, 0.5811427), (715559718091440000, 0.5811427), (715559718101334000, 0.5813928), (715559718111284000, 0.5813928), (715559718121221000, 0.5811427), (715559718131099000, 0.5808928), (715559718140997000, 0.5808928), (715559718150945000, 0.5811427), (715559718160970000, 0.5813928), (715559718170853000, 0.5817678), (715559718180773000, 0.5810177), (715559718190747000, 0.5808928), (715559718200688000, 0.5813928), (715559718210567000, 0.5807677), (715559718220463000, 0.5817678), (715559718230410000, 0.5805177), (715559718240350000, 0.5808928), (715559718250236000, 0.5810177), (715559718260293000, 0.5808928), (715559718270243000, 0.5811427), (715559718280178000, 0.5811427), (715559718290054000, 0.5811427), (715559718299951000, 0.5808928), (715559718309908000, 0.5805177), (715559718319844000, 0.5811427), (715559718329721000, 0.5806427), (715559718339619000, 0.5812678), (715559718349568000, 0.5813928), (715559718359641000, 0.5813928), (715559718370132000, 0.5813928), (715559718380101000, 0.5810177), (715559718390056000, 0.5807677), (715559718399996000, 0.5813928), (715559718409886000, 0.5810177), (715559718419775000, 0.5810177), (715559718429732000, 0.5816427), (715559718439670000, 0.5811427), (715559718449554000, 0.5808928), (715559718459455000, 0.5813928), (715559718469707000, 0.5811427), (715559718479695000, 0.5811427), (715559718489586000, 0.5815177), (715559718499520000, 0.5812678), (715559718509505000, 0.5805177), (715559718519437000, 0.5813928), (715559718529372000, 0.5808928), (715559718539332000, 0.5808928), (715559718549288000, 0.5811427), (715559718559336000, 0.5810177), (715559718569478000, 0.5807677), (715559718579373000, 0.5813928), (715559718589322000, 0.5810177), (715559718599262000, 0.5812678), (715559718609149000, 0.5806427), (715559718619041000, 0.5816427), (715559718628992000, 0.5812678), (715559718638925000, 0.5812678), (715559718648820000, 0.5812678), (715559718658717000, 0.5818928), (715559718668752000, 0.5808928), (715559718678688000, 0.5808928), (715559718688632000, 0.5807677), (715559718698531000, 0.5813928), (715559718708483000, 0.5808928), (715559718718414000, 0.5816427), (715559718728302000, 0.5808928), (715559718738192000, 0.5806427), (715559718748135000, 0.5812678), (715559718758075000, 0.5813928), (715559718768006000, 0.5807677), (715559718778015000, 0.5808928), (715559718787963000, 0.5816427), (715559718797895000, 0.5811427), (715559718807782000, 0.5812678), (715559718817676000, 0.5811427), (715559718827620000, 0.5808928), (715559718837561000, 0.5808928)]

  23:35:20 [pytest] [espdev] [ESP32] : ADS1115 Benchmark TEST: [✔]
  Test Result: PASSED
  test_dev.py::test_disconnect
  ------------------------------------------------------------------------------------------------------------------------ live log call ------------------------------------------------------------------------------------------------------------------------
  23:35:20 [pytest] [espdev] [ESP32] : DEVICE DISCONNECT TEST
  23:35:20 [pytest] [espdev] [ESP32] : DEVICE DISCONNECT TEST: [✔]
  Test Result: PASSED
  Saved benchmark data in: /Users/carlosgilgonzalez/Desktop/MY_PROJECTS/MICROPYTHON/TOOLS/upydev_.nosync/tests/.benchmarks/Darwin-CPython-3.7-64bit/0023_espd_ads1115.json



  ------------------------------------------------------- benchmark 'device': 1 tests -------------------------------------------------------
  Name (voltage in mV)                                Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
  -------------------------------------------------------------------------------------------------------------------------------------------
  test_dev[ADS1115 Benchmark]:[espdev@esp32]     579.1427  582.0178  581.1515  0.3732  581.1427  0.5000      23;1  1.7207     100           1
  -------------------------------------------------------------------------------------------------------------------------------------------

  Legend:
    Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
    OPS: Operations Per Second, computed as 1 / Mean
  ===================================================================================================================== 8 passed in 13.40s ======================================================================================================================

.. tip:: **benchmark** directive accepts single value, a list of values or a list
    of 2 values tuples, where the first value is a time value and the second is the measurement to benchmark.

.. note:: To save benchmark results (i.e not only the stats) use ``--benchmark-save=[NAME] --benchmark-save-data``
    Data will be saved in ``.benchmarks/[SYSTEM PLATFORM]/xxxx_[NAME].json``, e.g.


.. code-block:: python
  :caption: plot.py

  import json
  from matplotlib import pyplot as plt
  import sys

  file = sys.argv[1]

  with open(file, 'r') as rp:
      report = json.load(rp)

  data = report['benchmarks'][0]['stats']['data']
  time_stamp = report['benchmarks'][0]['extra_info']['vtime']
  # from absolute timestamps in ns to relative time in seconds
  t_vec = [(t-time_stamp[0])/1e9 for t in time_stamp]

  plt.plot(t_vec, data)
  plt.ylabel("Voltage ($V$)")
  plt.xlabel("Time ($s$)")
  plt.show()


.. code-block:: console

  $ ./plot.py .benchmarks/Darwin-CPython-3.7-64bit/0023_espd_ads1115.json


.. image:: img/ads1115_data_.png

Device development setups
-------------------------

SerialDevice
^^^^^^^^^^^^^
The easiest way to develop is having the device directly connected to the computer by USB.
It allows a fast develop/test/fix/deploy cycle. It is also possible to make the device act as
a peripheral so in can be integrated and controlled from the computer through a simple script,
command line tool (like upydev) or even a GUI app. This is also possible using
wireless connections, but this one has the lowest latency and the best performance.

To help with a fast development cycle, there are some tools/short-cuts/keybindings in ``shell-repl`` that allows
to load code from file into the device buffer to be executed. This is done using a tmp file ``_tmp_script.py`` in cwd.

- In **shell mode**:
  Pressing ``CTRL-t`` will load the contents of ``_tmp_script.py`` in device buffer and
  execute it. e.g. the file ``_tmp_script.py`` with content:

.. code-block:: python3

    import time
    for i in range(10):
        print(f"hello: {i}")
        time.sleep(0.1)

Pressing ``CTRL-t``

.. code-block:: console

      esp32@sdev:~ $ Running Buffer...
      hello: 0
      hello: 1
      hello: 2
      hello: 3
      hello: 4
      hello: 5
      hello: 6
      hello: 7
      hello: 8
      hello: 9


- In **repl mode**:
  Pressing ``CTRL-e`` will create/open file ``_tmp_script.py`` to be modified
  in ``vim``. After saving and exit, the content will be loaded in device buffer.
  Next, pressing ``CTRL-d`` will execute the buffer or ``CTRL-c`` to cancel.
  e.g.


Pressing ``CTRL-e``, saving and exit, then ``CTRL-d``:

.. code-block:: console

    Temp Buffer loaded do CTRL-D to execute or CTRL-C to cancel
    >>> Running Buffer...
    hello: 0
    hello: 1
    hello: 2
    hello: 3
    hello: 4
    hello: 5
    hello: 6
    hello: 7
    hello: 8
    hello: 9
    >>>


- Using **load** command in **shell mode**: This allows to load and execute local
  scripts in device. This loads a local file content in device buffer and executes it.

.. code-block:: console

  esp32@sdev:~ $ load dummy.py

  This is a dummy file for testing purpose

.. tip:: Device buffer is limited so if the file is too big it may be better to upload the
    file to the device or split the file in smaller ones.

.. note:: This is also avaible in the ``shell-repl`` for WebSocketDevices and BleDevices,
          however latency will be higher due to the nature of wireless connections, e.g
          higher latency of BleDevices if using a bluetooth headset at the same time.

WebSocketDevice
^^^^^^^^^^^^^^^
In `upyutils/network <https://github.com/Carglglz/upydev/tree/master/upyutils/network>`_
there are some modules that may be of help when developing devices that needs to be
connected and mantain a reliable connection.

Using ``wpa_supplicant.py`` module allows to the define a configuration file
``wpa_supplicant.config`` with known AP networks ssid:passwords and its function
e.g.

.. code-block:: json

  {"my_ssid": "my_pass", "my_ssid2": "my_pass2"}


``setup_network()`` will scan and connect to the closest known AP and return ``True`` if
connected.

.. code-block:: python

  import wpa_supplicant

  if wpa_supplicant.setup_network():
    print("Connected")
    # Now for example RTC can be set with ntptime.settime()
  else:
    # Enable device AP instead
    print("Enabling AP")

As a bonus to set mDNS host name of the device, add a file named ``hostname.py`` with
the name e.g. ``NAME = "mydevice"`` and it will be set by ``wpa_supplicant.setup_network()``
too. This allows to use ``mydevice.local`` instead of device IP address.

.. code-block:: console

  $ ping mydevice.local
  PING mydevice.local (192.168.1.53): 56 data bytes
  64 bytes from 192.168.1.53: icmp_seq=0 ttl=255 time=100.093 ms
  64 bytes from 192.168.1.53: icmp_seq=1 ttl=255 time=21.592 ms
  64 bytes from 192.168.1.53: icmp_seq=2 ttl=255 time=239.554 ms
  ^C
  --- mydevice.local ping statistics ---
  3 packets transmitted, 3 packets received, 0.0% packet loss
  round-trip min/avg/max/stddev = 21.592/120.413/239.554/90.135 ms


In case a device needs to be moved (e.g. is powered by battery or to change device location)
A network watchdog can be useful to reset and connect to a new AP or schedule a reconnection
attemp.

Module ``nwatchdog.py`` defines a  Network watchdog class that will init a WatchDog Timer
``WDT`` with a timeout of n+10 and a hardware ``Timer`` that will check every n seconds if WLAN is connected,
and feed the ``WDT`` if True. Therefore if WLAN is for any reason disconnected the
watchdog will not be fed and it will trigger a reset.

e.g. in combination with ``wpa_supplicant.py`` and ``config`` module.

.. code-block:: python

  from wpa_supplicant import setup_network
  from nwatchdog import WatchDog
  from watchdog_config import WATCHDOG
  from log_config import LOG
  import ntptime
  import upylog
  from hostname import NAME

  upylog.basicConfig(level=LOG.level, format='TIME_LVL_MSG')
  log = upylog.getLogger(NAME, log_to_file=True, rotate=5000)

  if setup_network():
    if WATCHDOG.enabled:
        wlan = network.WLAN(network.STA_IF)
        watch_dog = WatchDog(wlan)
        watch_dog.start()
        log.info('Network WatchDog started!')
    # Set time
    try:
        ntptime.settime()
    except Exception as e:
        log.exception(e, "NTP not available")

  else:
    # set AP

Module ``ursyslogger.py`` allows to forward logging messages to a remote host
using `rsyslog <https://github.com/rsyslog/rsyslog>`_ . Configure rsyslog in remote server
to enable remote logging using TCP, see `remote logging with rsyslog <https://www.makeuseof.com/set-up-linux-remote-logging-using-rsyslog/>`_.

Then add ``RsysLogger`` to ``log``.

.. code-block:: python

  ...
  >>> from ursyslogger import RsysLogger
  >>> rsyslog = RsysLogger("server.local", port=514, hostname="mydevice", t_offset="+01:00")
  >>> log.remote_logger = rsyslog
  >>> log.info("Remote hello")
  2022-09-15 10:06:04 [esp32@mydevice] [INFO] Remote hello

Then check in remote server e.g.

.. code-block:: console

  $ tail -F mydevice.local.log
  Sep 15 10:06:04 mydevice.local esp32@mydevice Remote hello


BleDevice
^^^^^^^^^
Once the device is running ``BleREPL`` with ``NUS`` profile (Nordic UART Service), it is possible
to connect and send commands as with other devices. However due to the nature of
Bluetooth Low Energy, the computer needs to scan first and then connect, which
depending on the advertising period of the device, it may take a bit. This is why connecting
to the device using ``shell-repl`` mode is the best way to work. (e.g in case the device cannot
be connected using USB/Serial i.e. no physical access.)
Using ``config`` module it is possible to set different operation modes that will switch
between:

 - Custom ble app/profile (e.g. ``Temeperature Sensor`` Profile)
 - Debug Mode, running ``BleREPL`` with ``NUS`` Profile.
 - Bootloader Mode, running ``DFU`` Profile to do OTA firmware updates.


Set mode config with, (in ``shell-repl``)

.. code-block:: console

    esp32@oble:~ $ config add mode
    esp32@oble:~ $ config mode: app=True blerepl=False dfu=False
    mode -> app=True, blerepl=False, dfu=False


and in ``main.py``:

.. code-block:: python

  from mode_config import MODE

  if MODE.app:
    print('App mode')
    import myapp
    myapp.run()

  elif MODE.blerepl:
    print('Debug mode')
    import ble_uart_repl
    ble_uart_repl.start()

  elif MODE.dfu:
    print('DFU mode')
    from otable import BLE_DFU_TARGET
    ble_dfu = BLE_DFU_TARGET()


.. note:: Note that while running in ``app`` or ``dfu`` mode to switch to another mode, it
  should be done by setting ``mode`` config using ``config`` module and then rebooting the device, using a custom writable characteristic in case of ``app`` mode, and in case of ``dfu`` mode after a timeout with no connections
  or OTA update successfully done (ideally switching to ``debug`` / ``blerepl`` mode to perform tests. After that
  set config to ``app`` mode and reboot)
