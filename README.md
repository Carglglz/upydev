

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

### [Docs](https://upydev.readthedocs.io/en/latest/)

### Getting Started

<<<<<<< HEAD
* [WebREPL: a prompt over-wifi](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi)
* [WebREPL: web-browser interactive prompt](http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt)
=======
>>>>>>> develop

#### Installing :

`$ pip install upydev` or ``$ pip install --upgrade upydev`` to update to the latest version available

#### Create a configuration file:

upydev will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

<<<<<<< HEAD
- To save configuration in working directory: `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD]`

  e.g:

  `$ upydev config -t 192.168.1.58 -p mypass`

* To save configuration globally use -g flag: `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g`

  e.g.

  `$ upydev config -t 192.168.1.58 -p mypass -g `

------

#### uPydev Usage:

Usage:

`$ upydev [Mode] [options] or upydev [upy command] [options]`

This means that if the first argument is not a Mode keyword or a
upy command keyword it assumes it is a 'raw' upy command to send to the upy device

##### Help: `$ upydev -h`

Example: Mode

`$ upydev put -f dummy.py`

Example: uPy command

`$ upydev info`

Example: Raw commands

`$ upydev "my_func()"`

`$ upydev 2+1`

`$ upydev "import my_lib;foo();my_var=2*3"`

------

#### uPydev Mode/Tools:

- **`upydev config`**: save upy device settings (*see `-p`, `-t`, `-g`)*, so the target and password arguments wont be required any more

- **`upydev put`** : to upload a file to upy device (*see `-f`, `-s` , `-dir`, `-rst`; for multiple files see `-fre` option and  use `-wdl` to put only new or modified files.)*

- **`upydev get`** : to download a file from upy device (*see `-f` , `-dir`, `-s`; for multiple files see `-fre` option*)

- **`upydev sync`** : for a faster transfer of large files (this needs [sync_tool.py](https://github.com/Carglglz/upydev/tree/master/upyutils) in upy device) (*see `-f`, `-s` and `-lh`; for multiple files see `-fre` option*)

- **`upydev d_sync`**: to recursively sync a folder in upydevice filesystem use `-dir` to indicate the folder (must be in cwd), use `-tree` to see dir structure, or `-s sd` to sync to an Sd card mounted as 'sd'. Use `-wdl` to sync only new or modified files.

- **`upydev cmd`** : for debugging purpose, to send command to upy device ; (*see -c, -r, -rl*);

   - Examples:

   `$ upydev cmd -c "led.on()"`

   `$ upydev cmd -r "print('Hello uPy')"`

   ` $ upydev cmd -rl "function_that_print_multiple_lines()"`

   *  *tip: simple commands can be used without quotes;*
     *but for commands with parenthesis or special characters use quotes,*
     *for example: 'dummy_func()' ; use double quotes "" when the command*
     *includes a string like this example: "uos.listdir('/sd')"*

- **`upydev wrepl`** : to enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
    To see more keybinding info do CTRL-k
 (Added custom keybindings and autocompletion on tab to the previous work
     see: [Terminal WebREPL](https://github.com/Hermann-SW/webrepl) for the original work)

- **`upydev wssrepl`** : to enter the terminal WebSecureREPL; CTRL-x to exit, CTRL-d to do soft reset To see more keybindings info do CTRL-k. REPL over WebSecureSockets (This needs use of `sslgen_key -tfkey`, `update_upyutils` and enable WebSecureREPL in the device `import wss_repl;wss_repl.start(ssl=True)`)

- **`upydev srepl`** : to enter the terminal serial repl using picocom, indicate port by `-port` option (to exit do CTRL-a, CTRL-x) (see: [Picocom](https://github.com/npat-efault/picocom) for more information)

- **`upydev ping`** : pings the target to see if it is reachable, CTRL-C to stop

- **`upydev run`** : just calls import 'script', where 'script' is indicated by `-f` option (script must be in upy device or in sd card indicated by `-s` option and the sd card must be already mounted as 'sd');

     Supports *CTRL-C* to stop the execution and exit nicely.
=======
- To save configuration in working directory:

  ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE]``, where ``ADDRESS`` must be a valid **IP** , **SERIAL ADDRESS**
>>>>>>> develop

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

<<<<<<< HEAD
* **`upydev flash`**: to flash a firmware file to the upydevice, a serial port must be indicated to flash do: `upydev flash -port [serial port] -f [firmware file]` (*just for esp8266 and esp32*)

* **`upydev see`**: to get specific command help info indicated with `-c` option
=======
>>>>>>> develop

  Default device name is ``upydevice``, to set a custom name use ``-@`` flag as

```bash
 $ upydev config -t 192.168.1.40 -p mypass -@ mycustomdevice
```


  To check configuration

```bash
$ upydev check
Device: mycustomdevice
Address: 192.168.1.40, Device Type: WebSocketDevice
```

  Or to get more information if the device is online

```bash
$ upydev check -i
Device: mycustomdevice
WebSocketDevice @ ws://192.168.1.40:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.13-221-gc8b055717 on 2020-12-05; ESP32 module with ESP32
(MAC: 80:7d:3a:80:9b:30, RSSI: -48 dBm)
```

- To save configuration globally use ``-g`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -g``

<<<<<<< HEAD
* **`upydev debug`**: to execute a local script line by line in the target upydevice, use `-f` option to indicate the file. To enter next line press ENTER, to finish PRESS C then ENTER. To break a while loop do CTRL-C.

* **`upydev gen_rsakey`** To generate RSA-2048 bit key that will be shared with the device (it is unique for each device) use -tfkey to send this key to the device (use only if connected directly to the AP of the device or a "secure" wifi e.g. local/home). If not connected to a "secure" wifi upload the key (it is stored in upydev._*path*_) by USB/Serial connection.

* **`upydev rf_wrkey`** To "refresh" the WebREPL password with a new random password derivated from the RSA key previously generated. A token then is sent to the device to generate the same password from the RSA key previously uploaded. This won't leave any clues in the TCP Websocekts packages of the current WebREPL password. (Only the token will be visible; check this using wireshark) (This needs upysecrets.py)

* **`upydev crypto_wrepl`**:To enter the terminal CryptoWebREPL a E2EE wrepl/shell terminal; CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default) To see more keybindings info do CTRL-k. By default resets after exit, use `-rkey` option to refresh the WebREPL password with a new random password, after exit. This passowrd will be stored in the working directory or in global directory with `-g` option. (This mode needs upysecrets.py)

* **`upydev upy`** to access crypto_wrepl in a 'ssh' style command to be used like e.g.: `upydev upy@192.168.1.42` or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. `upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass`) The device can be accessed as `upydev upy@foo_device` or redirect any command as e.g. `upydev ping -@foo_device`

* **`upydev sslgen_key`** (This needs openssl available in `$PATH`)

     To generate ECDSA key and a self-signed certificate to enable SSL sockets This needs a passphrase, that will be required every time the key is loaded. Use `-tfkey` to upload this key to the device (use only if connected directly to the AP of the device or a "secure" wifi e.g. local/home). If not connected to a "secure" wifi upload the key (it is stored in upydev._*path*_) by USB/Serial connection.

- **`upydev ssl_wrepl`**: To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal (SSL sockets); CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default) To see more keybindings info do CTRL-k. By default resets after exit. (This mode needs *ssl_repl.py)* use `-rkey` option to refresh the WebREPL password with a new random password, after exit. This passowrd will be stored in the working directory or in global directory with `-g` option. (This mode needs *ssl_repl.py, upysecrets.py* for `-rfkey`) *(Use `-nem` option to use without encryption (for esp8266))

- **`upydev ssl`**: to access ssl_wrepl in a 'ssh' style command to be used like e.g.: `upydev ssl@192.168.1.42` or if a device is stored in a global group called "*UPY_G*" (this needs to be created first doing e.g. `$ upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass`) The device can be accessed as `$ upydev ssl@foo_device` or redirect any command as e.g. `$ upydev ping -@foo_device`

- **`upydev sh_srepl`**: To enter the serial terminal SHELL-REPL; CTRL-x to exit, To see more keybindings info do CTRL-k. By default resets after exit. To configure a serial device use `-b` for baudrate and `-t` for serial port To access without previous configuration: `sh_srepl -t [serial port] -b [baudrate]` (default baudrate is 115200) To access with previous configuration:

   - `sh_srepl` (if device configured in current working directory)
   - `sh_srepl -@ foo_device` (if foo_device is configured in global group 'UPY_G')

- **`upydev shr`**: to access the serial terminal SHELL-REPL in a 'ssh' style command to be used like e.g.: `upydev shr@/dev/tty.usbmodem3370377430372` or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. `upydev make_group -g -f UPY_G -devs foo_device 115200 /dev/tty.usbmodem3370377430372`) The device can be accessed as `upydev shr@foo_device`

- **`upydev wssl`**: to access ssl_wrepl if WebSecureREPL is enabled in a 'ssh' style command to be used like e.g.: `upydev wssl@192.168.1.42` or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. `upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass`) then the device can be accessed as `upydev wssl@foo_device`.

- **`upydev set_wss`**: To toggle between WebSecureREPL and WebREPL, to enable WebSecureREPL do 'set_wss', to disable 'set_wss -wss'

- **`upydev jupyterc`**: to run MicroPython upydevice kernel for jupyter console, CTRL-D to exit, %lsmagic to see magic commands and how to connect to a device either WebREPL (%websocketconnect) or Serial connection (%serialconnect).

   Hit tab to autcomplete magic commands, and MicroPython/Python code. (This needs jupyter and MicroPython upydevice kernel to be installed)
- **`upydev make_group`**: to make a group of boards to send commands to. Use -f for the name of the group

  and -devs option to indicate a name, ip and the password of each board. (To store the group settings globally use `-g` option)

- **`upydev mg_group`**: to manage a group of boards to send commands to. Use `-G` for the name of the group and `-add` option to add devices (indicate a name, ip and the password of each board) or `-rm` to remove devices (indicated by name). More info at [GitBook Wiki](https://carlosgilglez.gitbook.io/upydev/#upydev-mode-tools).

------

**GROUP COMMAND MODE (-G option)**:

To send a command to multiple devices in a group (made with make_group command) use -G option

 Usage: `upydev [command] -G [GROUP NAME]`

To target specific devices within a group add -devs option as `-devs [DEV_1 NAME] [DEV_2 NAME]`

*upydev will use local working directory configuration unless it does not find any or manually indicated with -g option*

**GROUP COMMAND PARALLEL MODE (-GP option)**:

To send a command **at the same time** to multiple devices in a group (made with make_group command) use -GP option.

***Be aware that not all the commands are suitable for parallel execution (wrepl for example)*

 Usage: `upydev [command] -GP [GROUP NAME]`

To target specific devices within a group add -devs option as `-devs [DEV_1 NAME] [DEV_2 NAME]`

*upydev will use local working directory configuration unless it does not find any or manually indicated with -g option*

------
=======
  e.g.
>>>>>>> develop

```bash
$ upydev config -t 192.168.1.40 -p mypass -g
```

- To save configuration in a global group use ``-gg`` flag: ``$ upydev config -t [DEVICE ADDRESS] -p [PASSWORD/BAUDRATE] -gg -@ mydevice``

  e.g.

```bash
$ upydev config -t 192.168.1.40 -p mypass -gg -@ mydevice
```


Once the device is configured see next section or read  [Usage documentation](https://upydev.readthedocs.io/en/latest/usage.html) to check which modes and tools are available.

Or if you are working with more than one device continue with this [section](https://upydev.readthedocs.io/en/latest/gettingstarted.html#create-a-group-file) to create a group configuration.

------

<<<<<<< HEAD
### DEBUG

#### RECOMMENDATION:

  >Since upydev is based in a wireless protocol connection, in order to succeed sending upydev commands make sure that there is a reliable connection between the host and the device and that the wifi signal strength (rssi) in the device is above -80  (below -80 performance could be inconsistent)

  **A 'Reliable' connection** **means that there is no packet loss**  (use ping or  `upydev ping` command to check)

  See [Received signal strength indication](https://en.wikipedia.org/wiki/Received_signal_strength_indication) and
  [Mobile Signal Strength Recommendations](https://wiki.teltonika.lt/view/Mobile_Signal_Strength_Recommendations).

#### TRACKING PACKETS:

To see if "command packets" are sent and received or lost use [Wireshark](https://www.wireshark.org) and filter the ip of the device.

#### SEE WHAT'S GOING ON UNDER THE HOOD:
=======
#### uPydev Usage:

*Requirement* : **Needs REPL to be accessible** (see [Getting Started](https://upydev.readthedocs.io/en/latest/gettingstarted.html))
>>>>>>> develop

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
