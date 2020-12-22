
Getting started
================

Requirement
-----------
**Needs REPL to be accesible.**:
    > Wireless Devices:
        * *WiFi*: Needs **WebREPL** enabled in the device
          see `WebREPL: a prompt over-wifi <http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi>`_
          and `WebREPL: web-browser interactive prompt <http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt>`_

        * *Bluetooth Low Energy*: Needs **BleREPL** enabled in the device
          see http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt

    > Serial Devices:
        * *USB*: Connected through USB **data** cable.


Create a configuration file
---------------------------

upydev will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory: ``$ upydev config -t [UPYDEVICE IP] -p [PASSWORD]``

  e.g.

  .. code-block:: console

    $ upydev config -t 192.168.1.58 -p mypass

- To save configuration globally use -g flag: ``$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g``

  e.g.

  .. code-block:: console

    $ upydev config -t 192.168.1.58 -p mypass -g
