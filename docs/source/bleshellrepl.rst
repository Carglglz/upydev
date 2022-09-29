Bluetooth Low Energy
====================

This is still experimental and for esp32 requires ``ble_advertising.py``, ``ble_uart_peripheral.py``, ``ble_uart_repl.py`` to be uploaded
to the device. These scripts can be found in `upyutils <https://github.com/Carglglz/upydev/tree/master/upyutils>`_ directory and they come from `micropython examples <https://github.com/micropython/micropython/tree/master/examples/bluetooth>`_.
Finally to enable it add the following to ``main.py``:

.. code-block:: python

  import ble_uart_repl
  ble_uart_repl.start()

To configure a ble device see

:ref:`gettingstarted:Create a configuration file`

To access BLE SHELL-REPL

.. code-block:: console

    $ upydev shl



To configure a ble device in the global group 'UPY_G' see

:ref:`gettingstarted:Create a GROUP file`


Then the device can be accessed with:

.. code-block:: console

    $ upydev shl -@ ble_device

or

.. code-block:: console

    $ upydev shl@ble_device
    shell-repl @ ble_device
    BleREPL connected

    MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; ESP32 module with ESP32
    Type "help()" for more information.

    - CTRL-k to see keybindings or -h to see help
    - CTRL-s to toggle shell/repl mode
    - CTRL-x or "exit" to exit
    esp32@ble_device:~ $


By default advertising and GAP name is set using device platform and unique id.
e.g. advertising name ``esp32-74`` and GAP name ``ESP32@7c9ebd3d9df4``
To set a custom name use ``set localname [NAME]`` in upydev or shell-repl as

.. code-block:: console

  esp32@ble_device:~ $ set localname bledev

  # Now reset the device, then check localname with $ upydev -i -@ ble_device
  # or connect to shell-repl mode and use command info e.g.

  esp32@ble_device:~ $ info
  BleDevice @ 00FEFE2D-5983-4D6C-9679-01F732CBA9D9, Type: esp32 , Class: BleDevice
  Firmware: MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; 4MB/OTA BLE module with ESP32
  (MAC: ec:94:cb:54:8e:14, Local Name: bledev, RSSI: -76 dBm)


See :ref:`BleDevice development setup <examples:BleDevice>`
