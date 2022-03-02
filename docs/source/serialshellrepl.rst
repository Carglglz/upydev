Serial
========


To use this mode connect the device by USB to the computer and use one of the following commands:

If the device is not previously configured do:

.. code-block:: console

    $ upydev shl -t [serial port] -p [baudrate] (default is 115200)

To configure a serial device see

:ref:`gettingstarted:Create a configuration file`

To access SERIAL SHELL-REPL

.. code-block:: console

    $ upydev shl


To configure a serial device in the global group 'UPY_G' see

:ref:`gettingstarted:Create a GROUP file`


Then the device can be accessed with:

.. code-block:: console

    $ upydev shl -@ foo_device

or

.. code-block:: console

    $ upydev shl@foo_device
    shell-repl @ foo_device
    SerialREPL connected

    MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; ESP32 module with ESP32
    Type "help()" for more information.

    - CTRL-k to see keybindings or -h to see help
    - CTRL-s to toggle shell/repl mode
    - CTRL-x or "exit" to exit
    esp32@foo_device:~ $
