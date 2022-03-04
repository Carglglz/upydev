

<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Carglglz/upydev/master/uPydevlogo.png">

# uPydev

[![PyPI version](https://badge.fury.io/py/upydev.svg)](https://badge.fury.io/py/upydev)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

### Command line tool for MicroPython devices

**uPydev** is an acronym of '**MicroPy**thon **dev**ice', and it is intended to be a command line tool to make easier the development, prototyping and testing process of devices based on boards running MicroPython. It is intended to be cross-platform and
connection agnostic (Serial, WiFi and Bluetooth Low Energy).

### Features:

* Tools to allow configuration, management, communication and control of MicroPython devices.
* Command line Autocompletion
* File IO operations (upload, download one or multiple files, recursively sync directories...)
* SHELL-REPL modes: Serial, WiFi (SSL/WebREPL), BLE
* OTA\* Firmware updates WiFi (TCP/SSL), BLE  (\* esp32 only)
* Custom commands for debugging, testing and prototyping.
* Group mode to operate with multiple devices
------

### [Docs](https://upydev.readthedocs.io/en/latest/)

### Getting Started


#### Installing :

`$ pip install upydev` or ``$ pip install --upgrade upydev`` to update to the latest version available

#### Create a configuration file:

upydev will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory:

  ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE]``, where ``ADDRESS`` must be a valid **IP** , **SERIAL ADDRESS**

  > ``-p`` is set to 115200 by default, so it is not necessary unless using a different baudrate

  , or **MAC ADDRESS/ UUID**

  > It will depend on OS system (e.g. Linux uses MAC format 'XX:XX:XX:XX:XX:XX', and macOS uses UUID format 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')

    e.g.

  ```bash
  # WiFi
  $ upydev config -t 192.168.1.40 -p mypass

  # SERIAL
  $ upydev config -t /dev/tty.usbmodem387E386731342

  # BLE
  $ upydev config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9
  ```


  Default device name is ``upydevice``, to set a custom name use ``-@`` flag as

```bash
 $ upydev config -t 192.168.1.40 -p mypass -@ mycustomdevice
```


  To check configuration ``upydev`` or ``upydev check``

```bash
$ upydev
Device: mycustomdevice
Address: 192.168.1.40, Device Type: WebSocketDevice
```

  Or to get more information if the device is online

```bash
$ upydev -i
Device: mycustomdevice
WebSocketDevice @ ws://192.168.1.40:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.13-221-gc8b055717 on 2020-12-05; ESP32 module with ESP32
(MAC: 80:7d:3a:80:9b:30, RSSI: -48 dBm)
```

- To save configuration globally use ``-g`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -g``

  e.g.

```bash
$ upydev config -t 192.168.1.40 -p mypass -g
```

- To save configuration in a global group use ``-gg`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -gg -@ mydevice``

  e.g.

```bash
$ upydev config -t 192.168.1.40 -p mypass -gg -@ mydevice
```

- [Optional]
Finally use `register` command to
define a function in ``~/.bashrc`` or ``~/.profile``

```bash
$ upydev register -@ mydevice
````

```bash
function mydevice() { upydev "$@" -@ mydevice; }
function _argcomp_upydev() { _python_argcomplete upydev; }
complete -o bashdefault -o default -o nospace -F _argcomp_upydev mydevice
```

Now ``mydevice`` will accept any args and pass them to upydev, as well as
autocompletion of args, e.g.

```bash
$ mydevice
Device: mydevice
Address: 192.168.1.40, Device Type: WebSocketDevice
```
Or if the device is connected.

```bash
$ mydevice -i
Device: mydevice
WebSocketDevice @ ws://192.168.1.40:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.17-290-g802ef271b-dirty on 2022-01-04; ESP32 module with ESP32
(MAC: 80:7d:3a:80:9b:30, RSSI: -48 dBm)
```

Once the device is configured see next section or read  [Usage documentation](https://upydev.readthedocs.io/en/latest/usage.html) to check which modes and tools are available.

Or if you are working with more than one device continue with this [section](https://upydev.readthedocs.io/en/latest/gettingstarted.html#create-a-group-file) to create a group configuration.

------

#### uPydev Usage:

*Requirement* : **Needs REPL to be accessible** (see [Getting Started](https://upydev.readthedocs.io/en/latest/gettingstarted.html))

Usage:

`$ upydev [Mode] [options] or upydev [upy command] [options]`

This means that if the first argument is not a Mode keyword or a
upy command keyword it assumes it is a 'raw' upy command to send to the upy device

##### Help: `$ upydev h`, `$ upydev help`, `$ upydev -h` or `$ upydev %[command]`

Example: Mode

`$ upydev put dummy.py`, `$ upydev get dummpy.py`

Example: uPy command

`$ upydev info`

Example: Raw commands

`$ upydev "my_func()"`

`$ upydev 2+1`

`$ upydev "import my_lib;foo();my_var=2*3"`


To see documentation check [Upydev readthedocs](https://upydev.readthedocs.io/en/latest/)
