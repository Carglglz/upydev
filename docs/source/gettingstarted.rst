
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

``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE]``, where ``ADDRESS`` must be a valid **IP** , **SERIAL ADDRESS** [#]_, or **MAC ADDRESS/ UUID** [#]_

  e.g.

  .. code-block:: console

    # WiFi
    $ upydev config -t 192.168.1.40 -p mypass

    # SERIAL
    $ upydev config -t /dev/tty.usbmodem387E386731342

    # BLE
    $ upydev config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9


.. [#] ``-p`` is set to 115200 by default, so it is not necessary unless using a different baudrate
.. [#] It will depend on OS system (e.g. Linux uses MAC format 'XX:XX:XX:XX:XX:XX', and macOS uses UUID format 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')


Default device name is ``upydevice``, to set a custom name use ``-@`` flag as

  .. code-block:: console

    $ upydev config -t 192.168.1.40 -p mypass -@ mycustomdevice


To check configuration

  .. code-block:: console

    $ upydev check
    Device: mycustomdevice
    Address: 192.168.1.40, Device Type: WebSocketDevice

Or to get more information if the device is online

  .. code-block:: console

    $ upydev check -i
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



Once the device is configured see :doc:`usage` documentation to check which modes and tools are available.

Or if you are working with more than one device continue with the following section to create a group configuration.



Create a GROUP file
-------------------

Make a global group of uPy devices named "UPY_G" to enable redirection to a specific device
so next time any command can be redirected to any device within the group

Use ``make_group`` or ``mkg`` as ``$ upydev mkg -g -f UPY_G -devs [NAME] [ADDRESS] [PASSWORD/BAUDRATE/DUMMY] [NAME2]...`` [#]_

to create and add more than one device at once.
e.g.

  .. code-block:: console

    $ upydev make_group -g -f UPY_G -devs esp_room1 192.168.1.42 mypass esp_room2 192.168.1.54 mypass2


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

  To add or remove devices from this group use ``mg_group`` or ``mgg``, and ``-gg`` flag which is the same
  as ``-G UPY_G``.

  - Add ``$ upydev mgg -gg -add [NAME] [PASSWORD] [PASSWORD/BAUDRATE/DUMMY] [NAME2]...``
  - Remove ``$ upydev mgg -gg -rm [NAME] [NAME2]...``
