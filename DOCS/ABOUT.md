### ABOUT

#### uPydev

 uPydev is a command line tool for 'wireless MicroPython devices' since it make use of the [WebREPL protocol](https://github.com/micropython/webrepl)  to provide communication with and control of the device. 

(See upydev [gitbook](https://carlosgilglez.gitbook.io/upydev/) for the most up-to-date info)

It is built on top of other tools/scripts which are:

The core is `webrepl_client.py ` : a [Terminal WebREPL protocol](https://github.com/Hermann-SW/webrepl)  by [@Hermann-SW](https://github.com/Hermann-SW)

Other tools are:

* `webrepl_cli.py`  for the file transfer protocol (from the WebREPL repo of micropython) (modified and named `upytool`)
* `esptool.py` to flash the firmware into esp boards
* `mpy-cross`  to compile .py scripts into .mpy files.
* `pydfu.py` to flash firmware to a pyboard (from [MicroPython](https://github.com/micropython/micropython/blob/master/tools/pydfu.py) tools repo)
* `upip_host.py` to install libraries via serial connection (partial port from [upip.py](https://github.com/micropython/micropython/blob/master/tools/upip.py))



### Requirements:

- **WebREPL enabled**
- Python modules (automatically installed using pip):
  - [argcomplete](https://github.com/kislyuk/argcomplete) (for command line autocompletion)
  - [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) (for new WebREPL Terminal implementation)
  - [mpy-cross](https://gitlab.com/alelec/micropython/tree/gitlab_build/mpy-cross)
  - [esptool](https://github.com/espressif/esptool)
  - [python-nmap](http://xael.org/pages/python-nmap-en.html)
  - [netifaces](https://github.com/al45tair/netifaces)
  - [requests](https://requests.kennethreitz.org/en/master/)
  - [cryptography](https://github.com/pyca/cryptography)
  - [websocket-client](https://github.com/websocket-client/websocket-client)
  - [Pygments](https://github.com/pygments/pygments)
  - [pyusb](https://github.com/pyusb/pyusb)
  - [upydevice](https://github.com/Carglglz/upydevice)

### Tested on:

- ### OS:

  - MacOS X (Mojave 10.14.5-6)

  - Raspbian GNU/Linux 10 (Buster) *(through ssh session)*

    For Raspbian `pip install mpy-cross` seems to fail, so to install upydev without mpy-cross do:*

```
$ git clone https://github.com/Carglglz/upydev.git
[...]
$ cd upydev
$ sudo pip3 install . --no-deps -r rpy_rqmnts.txt
```



- #### BOARDS:

  - Esp32 Huzzah feather

  - Esp8266 Huzzah feather

  - Pyboard Lite (SERIAL SHELL-REPL only)

  - Pyboard V1.1 (SERIAL SHELL-REPL only)

    

------

#### Commands Documentation

For an extensive explanation and commands demo see [Documentation](https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md).

#### Addiontal Scripts for some commands:

The commands that need additional scripts in the upy device are under the [uPyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) folder.

For more info see [upyutils_docs](https://github.com/Carglglz/upydev/blob/master/DOCS/upyutils_docs.md).



------

#### USEFUL DEVELOPER TOOLS: (*Under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) folder*)

* [**upylog**](https://github.com/Carglglz/upydev/tree/master/DOCS/upylog.md): MicroPython logging module with time format (predefined) and log to file support.
* [**upynotify**](https://github.com/Carglglz/upydev/tree/master/DOCS/upynotify.md) : module with NOTIFIER class to notify events with beeps and blinks. 