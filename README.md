<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Carglglz/upydev/master/uPydevlogo.png">

# uPydev

[![PyPI version](https://badge.fury.io/py/upydev.svg)](https://badge.fury.io/py/upydev)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

### Command line tool for MicroPython devices

**uPydev** is an acronym of '**MicroPy**thon **dev**ice', and it is intended to be a command line tool to make easier the development, prototyping and testing process of devices based on boards running MicroPython. It is intended to be cross-platform and
connection agnostic (Serial, WiFi and Bluetooth Low Energy).

### Features:

* Tools to allow configuration, management, communication and control of MicroPython devices
* Command line Autocompletion
* File IO operations (upload, download one or multiple files, recursively sync directories...)
* SHELL-REPL modes: Serial, WiFi (SSL/WebREPL), BLE
* OTA\* Firmware updates WiFi (TCP/SSL), BLE  (\* esp32 only)
* Custom commands for debugging, testing and prototyping
* Custom tasks yaml files that can be played like ansible
* Run tests in device with pytest and parametric tests or benchmarks using yaml files
* Group mode to operate with multiple devices

------

### [Docs](https://upydev.readthedocs.io/en/latest/)

### Getting Started

#### Installing :

`$ pip install upydev` or ``$ pip install --upgrade upydev`` to update to the latest version available

#### Create a configuration file:

upydev will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory:

  ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE]``, where ``[DEVICE ADDRESS]`` must be a valid :

  * **IP/HOSTNAME**

  * **SERIAL ADDRESS**

  * **MAC ADDRESS/ UUID**

  > Hostname must be set in device, e.g. in esp32 default is ``esp32.local``
  >
  > ``-p`` is set to 115200 by default, so it is not necessary unless using a different baudrate

  > MAC address format will depend on OS system (e.g. Linux uses MAC format 'XX:XX:XX:XX:XX:XX', and macOS uses UUID format 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')

    e.g.

  ```bash
  # WiFi
  $ upydev config -t 192.168.1.53 -p mypass

  # SERIAL
  $ upydev config -t /dev/tty.usbmodem387E386731342

  # BLE
  $ upydev config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9
  ```

  Default device name is ``upydevice``, to set a custom name use ``-@`` flag as

```bash
 $ upydev config -t 192.168.1.53 -p mypass -@ mycustomdevice
```

  To check configuration ``upydev`` or ``upydev check``

```bash
$ upydev
Device: mycustomdevice
Address: 192.168.1.53, Device Type: WebSocketDevice
```

  Or to get more information if the device is online

```bash
$ upydev -i
Device: mycustomdevice
WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, RSSI: -45 dBm)
```

- To save configuration globally use ``-g`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -g``

  e.g.

```bash
$ upydev config -t 192.168.1.53 -p mypass -g
```

- To save configuration in a global group use ``-gg`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -gg -@ mydevice``

  e.g.

```bash
$ upydev config -t 192.168.1.53 -p mypass -gg -@ mydevice
```

- [Optional]
  Use `register` command to
  define a function in ``~/.bashrc`` or ``~/.profile``

```bash
$ upydev register -@ mydevice
```

Reload `~/.bashrc` or `~/.profile`,  e.g. (`$ source ~/.profile`)

Now ``mydevice`` will accept any args and pass them to upydev, as well as
autocompletion of args, e.g.

```bash
$ mydevice
Device: mydevice
Address: 192.168.1.53, Device Type: WebSocketDevice
```

Or if the device is connected.

```bash
$ mydevice -i
Device: mydevice
WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, RSSI: -45 dBm)
```

To see registered devices do:

```bash
$ upydev lsdevs
Device: mydevice
Address: 192.168.1.53, Device Type: WebSocketDevice
```

Which adds the `lsdevs`  command to `~.profile`  too. So after reloading  again:

```bash
$ lsdevs
Device: mydevice
Address: 192.168.1.53, Device Type: WebSocketDevice
```

Finally to enter device shell-repl mode do:

```bash
$ upydev shl@mydevice
shell-repl @ mydevice
WebREPL connected
WARNING: ENCRYPTION DISABLED IN THIS MODE

MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
Type "help()" for more information.

- CTRL-k to see keybindings or -h to see help
- CTRL-s to toggle shell/repl mode
- CTRL-x or "exit" to exit
esp32@mydevice:~ $
```

or if the device is registered:

```bash
$ mydevice shl
shell-repl @ mydevice
WebSecREPL with TLSv1.2 connected
TLSv1.2 @ ECDHE-ECDSA-AES128-CCM8 - 128 bits Encryption

MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
Type "help()" for more information.

- CTRL-k to see keybindings or -h to see help
- CTRL-s to toggle shell/repl mode
- CTRL-x or "exit" to exit
esp32@mydevice:~ $
```

> *To enable WebSocket over TLS or wss check [WebSocket (ws) / WebSocket Secure (wss) TLS ](https://upydev.readthedocs.io/en/latest/sslwebshellrepl.html)*

Once the device is configured see next section or read  [Usage documentation](https://upydev.readthedocs.io/en/latest/usage.html) to check which modes and tools are available.

Or if you are working with more than one device continue with this [section](https://upydev.readthedocs.io/en/latest/gettingstarted.html#create-a-group-file) to create a group configuration.

------

#### uPydev Usage:

*Requirement* : **Needs REPL to be accessible** (see [Getting Started](https://upydev.readthedocs.io/en/latest/gettingstarted.html))

Usage:

`$ upydev [Mode] [options] or upydev [upy command] [options]`

This means that if the first argument is not a Mode keyword or a
upy command keyword it assumes it is a 'raw' upy command to send to the upy device

##### Help: `$ upydev h`, `$ upydev help`, `$ upydev -h` or `$ upydev [command] -h`

Example: Mode

`$ upydev put dummy.py`, `$ upydev get dummy.py`

Example: uPy command

`$ upydev info`

Example: Raw commands

`$ upydev "my_func()"`

`$ upydev 2+1`

`$ upydev "import my_lib;foo();my_var=2*3"`

To see documentation check [Upydev readthedocs](https://upydev.readthedocs.io/en/latest/)
