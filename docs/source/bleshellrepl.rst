Bluetooth Low Energy
====================


To configure a ble device see

:ref:`gettingstarted:Create a configuration file`

To access BLE SHELL-REPL

.. code-block:: console

    $ upydev shl # shl works too



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
