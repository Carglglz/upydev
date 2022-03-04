About
=====

Source code used as a reference

* `webrepl_client.py : Terminal WebREPL protocol <https://github.com/Hermann-SW/webrepl>`_
* `webrepl_cli.py  : File transfer protocol <https://github.com/micropython/webrepl>`_
* `pyboard.py  <https://github.com/micropython/micropython/blob/master/tools/pyboard.py>`_

Other tools are:

* `pydfu.py: to flash firmware to a pyboard <https://github.com/micropython/micropython/blob/master/tools/pydfu.py>`_
* `upip_host.py: to install libraries via serial connection <https://github.com/micropython/micropython/blob/master/tools/upip.py>`_


Requirements (modules)
----------------------
  - `argcomplete <https://github.com/kislyuk/argcomplete>`_
  - `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_
  - `esptool <https://github.com/espressif/esptool>`_
  - `python-nmap <http://xael.org/pages/python-nmap-en.html>`_
  - `netifaces <https://github.com/al45tair/netifaces>`_
  - `requests <https://requests.kennethreitz.org/en/master/>`_
  - `cryptography <https://github.com/pyca/cryptography>`_
  - `websocket-client <https://github.com/websocket-client/websocket-client>`_
  - `Pygments <https://github.com/pygments/pygments>`_
  - `pyusb <https://github.com/pyusb/pyusb>`_
  - `braceexpand <https://github.com/trendels/braceexpand>`_
  - `upydevice <https://github.com/Carglglz/upydevice>`_

Tested on
---------

- OS:

  - MacOS X (Mojave 10.14.5-6, Big Sur 11.6.1)
  - Raspbian GNU/Linux 10 (Buster)
  - Ubuntu 20.04.2 LTS (GNU/Linux 5.8.0-55-generic x86_64)



BOARDS
------

  - Esp32 (Huzzah feather, Geekcreit)

  - Esp8266 Huzzah feather

  - Pyboard Lite v1.0

  - Pyboard v1.1



DEVELOPER TOOLS
----------------
*Under* `Upyutils <https://github.com/Carglglz/upydev/tree/master/upyutils>`_
*folder*

:ref:`upylog:Upylog`
MicroPython logging module with time format (predefined) and log to file support.

:ref:`upynotify:Upynotify`
MicroPython module with NOTIFYER class to notify events with beeps (needs buzzer) and blinks.
