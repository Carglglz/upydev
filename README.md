

<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Carglglz/upydev/master/uPydevlogo.png">

# uPydev

[![PyPI version](https://badge.fury.io/py/upydev.svg)](https://badge.fury.io/py/upydev)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

### Command line tool for wireless MicroPython devices

**uPydev** is an acronym of '**MicroPy**thon **dev**ice', and it is intended to be a command line tool to make easier the development, prototyping and testing process of devices based on boards running MicroPython. It is intended to be cross-platform and
connection agnostic (Serial, WiFi and Bluetooth Low Energy).

⚠️ ***Keep in mind that this project is in ALPHA state, sometimes, some commands may not work/return anything*** ⚠️

### Features:

* Tools to allow configuration, management, communication and control of MicroPython devices.
* Command line Autocompletion
* File IO operations (upload, download one or multiple files, recursively sync directories...)
* SHELL-REPL modes: Serial, WiFi (SSL/WebREPL), BLE
* Custom commands for debugging, testing and prototyping.
* Group mode to operate with multiple devices
------

### Getting Started


#### Installing :

`$ pip install upydev` or ``$ pip install --upgrade upydev`` to update to the latest version available

#### Create a configuration file:

upydev will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory: `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD]`

  e.g:

  `$ upydev config -t 192.168.1.58 -p mypass`

* To save configuration globally use -g flag: `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g`

  e.g.

  `$ upydev config -t 192.168.1.58 -p mypass -g `

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


Too see documentation check [Upydev readthedocs](https://upydev.readthedocs.io/en/latest/)
