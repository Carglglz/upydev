
Getting started
================

If using a device with no MicroPython preinstalled (esp8266, esp32) first
follow MicroPython getting started from official docs_ to see how to install it for the
first time.

.. _docs: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

After that the device should be up and running for the next step.

Requirement
-----------
**Needs REPL to be accessible**:
    > Wireless Devices:
        * *WiFi*: Needs **WebREPL** enabled in the device
          see `WebREPL: a prompt over-wifi <http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi>`_
          and `WebREPL: web-browser interactive prompt <http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt>`_

        * *Bluetooth Low Energy*: Needs **BleREPL** enabled in the device. [#]_

    > Serial Devices:
        * *USB*: Connected through USB **data** cable.


.. [#] This is still experimental and for esp32 requires ``ble_advertising.py``, ``ble_uart_peripheral.py``, ``ble_uart_repl.py`` to be uploaded
       to the device. These scripts can be found in `upyutils <https://github.com/Carglglz/upydev/tree/master/upyutils>`_ directory and they come from `micropython examples <https://github.com/micropython/micropython/tree/master/examples/bluetooth>`_.
       Finally to enable it add the following to ``main.py``:

       .. code-block:: console

          import ble_uart_repl
          ble_uart_repl.start()

Create a configuration file
---------------------------

  Save the address and password/baudrate of a connected device so this won't be required
  for future interaction.

.. note::

    *If device address is unknown use* ``$ upydev scan [OPTION]`` *where* ``OPTION`` *can be* ``-sr``
    *for* **SERIAL**, ``-nt`` *for* **WiFi** *or* ``-bl`` *for* **Bluetooth Low Energy**.

  e.g.

    .. code-block:: console

      $ upydev scan -sr
      Serial Scan:
      SerialDevice/s found: 2
      ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
      ┃                  PORT                   ┃               DESCRIPTION                ┃          MANUFACTURER          ┃
      ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
      ┃     /dev/cu.usbmodem387E386731342       ┃   Pyboard Virtual Comm Port in FS Mode   ┃          MicroPython           ┃
      ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
      ┃         /dev/cu.SLAB_USBtoUART          ┃  CP2104 USB to UART Bridge Controller    ┃          Silicon Labs          ┃
      ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛



Upydev will use local working directory configuration unless it does not find any or manually indicated with ``-g`` option which is the global configuration flag.

- To save configuration in working directory:

``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE]``, where ``ADDRESS`` must be a valid **IP** [#]_ , **SERIAL ADDRESS** [#]_, or **MAC ADDRESS/ UUID** [#]_

  e.g.

  .. code-block:: console

    # WiFi
    $ upydev config -t 192.168.1.40 -p mypass

    # SERIAL
    $ upydev config -t /dev/tty.usbmodem387E386731342

    # BLE
    $ upydev config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9


.. [#] IP can be a valid dhcp_hostname e.g. `esp_dev.local`
.. [#] ``-p`` is set to 115200 by default, so it is not necessary unless using a different baudrate
.. [#] It will depend on OS system (e.g. Linux uses MAC format 'XX:XX:XX:XX:XX:XX', and macOS uses UUID format 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')


Default device name is ``upydevice``, to set a custom name use ``-@`` flag as

  .. code-block:: console

    $ upydev config -t 192.168.1.40 -p mypass -@ mycustomdevice


To check configuration ``upydev`` or ``upydev check``

  .. code-block:: console

    $ upydev
    Device: mycustomdevice
    Address: 192.168.1.40, Device Type: WebSocketDevice

Or to get more information if the device is online

  .. code-block:: console

    $ upydev -i
    Device: mycustomdevice
    WebSocketDevice @ ws://192.168.1.40:8266, Type: esp32, Class: WebSocketDevice
    Firmware: MicroPython v1.13-221-gc8b055717 on 2020-12-05; ESP32 module with ESP32
    (MAC: 80:7d:3a:80:9b:30, RSSI: -48 dBm)


- To save configuration globally use ``-g`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -g``

  e.g.

  .. code-block:: console

    $ upydev config -t 192.168.1.40 -p mypass -g


- To save configuration in a global group use ``-gg`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -gg -@ mydevice``

  e.g.

  .. code-block:: console

    $ upydev config -t 192.168.1.40 -p mypass -gg -@ mydevice



- [Optional]

Finally use `register` command to register a device as a shell function.
This defines the function in ``~/.bashrc`` or ``~/.profile``


  .. code-block:: console

    $ upydev register -@ mydevice


  .. code-block:: console

    function mydevice() { upydev "$@" -@ mydevice; }
    function _argcomp_upydev() { _python_argcomplete upydev; }
    complete -o bashdefault -o default -o nospace -F _argcomp_upydev mydevice

  .. code-block:: console

    $ source ~/.profile

  Now ``mydevice`` will accept any args and pass them to upydev, as well as
  autocompletion of args, e.g.

  .. code-block:: console

    $ mydevice
    Device: mydevice
    Address: 192.168.1.40, Device Type: WebSocketDevice

Or if the device is connected.

  .. code-block:: console

    $ mydevice -i
    Device: mydevice
    WebSocketDevice @ ws://192.168.1.40:8266, Type: esp32, Class: WebSocketDevice
    Firmware: MicroPython v1.17-290-g802ef271b-dirty on 2022-01-04; ESP32 module with ESP32
    (MAC: 80:7d:3a:80:9b:30, RSSI: -48 dBm)



Once the device is configured see :doc:`usage` documentation to check which modes and tools are available.

Or if you are working with more than one device continue with the following section to create a group configuration.



Create a GROUP file
-------------------

Make a global group of uPy devices named "UPY_G" to enable redirection to a specific device
so next time any command can be redirected to any device within the group

Use ``mkg`` as ``$ upydev mkg UPY_G -g -devs [NAME] [ADDRESS] [PASSWORD/BAUDRATE/DUMMY] [NAME2]...`` [#]_

to create and add more than one device at once.
e.g.

  .. code-block:: console

    $ upydev mkg UPY_G -g -devs esp_room1 192.168.1.42 mypass esp_room2 192.168.1.54 mypass2


.. [#] Every device must have a name, address and password/baudrate/dummy data (in case of ble) so the args can be parsed properly.

or use ``config`` and ``-gg`` flag as mentioned above to add one device at a time.


.. code-block:: console

  $ upydev config -t 192.168.1.42 -p mypass -gg -@ esp_room1
  WebSocketDevice esp_room1 settings saved in global group!

  $ upydev config -t 192.168.1.54 -p mypass -gg -@ esp_room2
  WebSocketDevice esp_room2 settings saved in global group!

To see the devices saved in this global group, use ``gg``.

  .. code-block:: console

      $ upydev gg
      GROUP NAME: UPY_G
      # DEVICES: 2
      ┣━ esp_room1    -> WebSocketDevice @ 192.168.1.42
      ┗━ esp_room2    -> WebSocketDevice @ 192.168.1.54


Now any command can be redirected to one of these devices with the ``-@`` [#]_ option :

  .. code-block:: console

    $ upydev info -@ esp_room1
    WebSocketDevice @ ws://192.168.1.42:8266, Type: esp32, Class: WebSocketDevice
    Firmware: MicroPython v1.12-63-g1c849d63a on 2020-01-14; ESP32 module with ESP32
    (MAC: 80:7d:3a:80:9b:30, RSSI: -51 dBm)

.. [#] Option ``-@`` has autocompletion on tab so hit tab and see what devices are available

.. note::

  To add or remove devices from this group use ``mgg``, and ``-gg`` flag which is the same
  as ``-G UPY_G``.

  - Add ``$ upydev mgg -gg -add [NAME] [PASSWORD] [PASSWORD/BAUDRATE/DUMMY] [NAME2]...``
  - Remove ``$ upydev mgg -gg -rm [NAME] [NAME2]...``


- [Optional]

Finally use `register` command to register a group as a shell function.
This defines the function in ``~/.bashrc`` or ``~/.profile``

.. code-block:: console

  $ upydev register devsg -@ pybV1.1 espdev oble

.. code-block:: console

  #UPYDEV GROUP devsg
  function devsg() { upydev "$@" -@ pybV1.1 espdev oble; }
  function _argcomp_upydev() { _python_argcomplete upydev; }
  complete -o bashdefault -o default -o nospace -F _argcomp_upydev devsg

.. code-block:: console

  $ source ~/.profile

Now ``devsg`` will accept any args and pass them to upydev, as well as
autocompletion of args, e.g.

.. code-block:: console

  $ devsg
  Device: pybV1.1
  Address: /dev/tty.usbmodem3370377430372, Device Type: SerialDevice

  Device: espdev
  Address: espdev.local, Device Type: WebSocketDevice

  Device: oble
  Address: 00FEFE2D-5983-4D6C-9679-01F732CBA9D9, Device Type: BleDevice

.. code-block:: console

  $ devsg -i
  Device: pybV1.1
  SerialDevice @ /dev/tty.usbmodem3370377430372, Type: pyboard, Class: SerialDevice
  Firmware: MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; PYBv1.1 with STM32F405RG
  Pyboard Virtual Comm Port in FS Mode, Manufacturer: MicroPython
  (MAC: 3c:00:3d:00:02:47:37:30:38:37:33:33)

  Device: espdev
  WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
  Firmware: MicroPython v1.18-42-g30b6ce86b-dirty on 2022-01-27; ESP32 module with ESP32
  (MAC: 30:ae:a4:23:35:64, Host Name: espdev, RSSI: -55 dBm)

  Device: oble
  BleDevice @ 00FEFE2D-5983-4D6C-9679-01F732CBA9D9, Type: esp32 , Class: BleDevice
  Firmware: MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; 4MB/OTA BLE module with ESP32
  (MAC: ec:94:cb:54:8e:14, Local Name: oble, RSSI: -50 dBm)
