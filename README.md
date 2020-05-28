

<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Carglglz/upydev/master/uPydevlogo.png">

# uPydev

[![PyPI version](https://badge.fury.io/py/upydev.svg)](https://badge.fury.io/py/upydev)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

### Command line tool for wireless MicroPython devices

**uPydev** is an acronym of '**MicroPy**thon **dev**ice', and it is intended to be a command line tool to make easier the development, prototyping and testing process of devices based on boards running MicroPython.

⚠️ ***Keep in mind that this project is in ALPHA state, sometimes, some commands may not work/return anything*** ⚠️

### Features:

* Command line wireless communication/control of MicroPython devices.
* Terminal WebREPL and WebSecureREPL protocol
* Custom commands to automate communication/control
* Command line autocompletion
* [SSLWebREPL](https://github.com/Carglglz/upydev/blob/master/DOCS/SSLWebREPL_docs.md) (a Terminal SHELL/REPL over SSL)
* [SERIAL SHELL-REPL](https://github.com/Carglglz/upydev/blob/master/DOCS/SERIAL_SHELL_REPL_docs.md) (a Terminal SHELL/REPL over USB)

#### See what is [NEW](https://github.com/Carglglz/upydev/blob/master/DOCS/WHATSNEW.md)

ℹ️ For Bluetooth Low Energy devices check [uPyble](https://github.com/Carglglz/upyble)

------

### Getting Started

First be sure that the **WebREPL daemon is enabled** and running see:

* [WebREPL: a prompt over-wifi](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi) 
* [WebREPL: web-browser interactive prompt](http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt)

#### Installing :

`$ pip install upydev` or ``$ pip install --upgrade upydev`` to update to the last version available

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

- **`upydev install`** : install libs to '/lib' path with upip; indicate lib with -f option

- **`upydev mpyx`** : to froze a module/script indicated with -f option, and save some RAM,
         it uses mpy-cross tool (see [mpy-cross](https://gitlab.com/alelec/micropython/tree/gitlab_build/mpy-cross) for more information)

- **`upydev timeit`** : to measure execution time of a module/script indicated with -f option.

  source: [timed_function](https://github.com/peterhinch/micropython-samples/tree/master/timed_function)


* **`upydev fw`**: to list or get available firmware versions, use `-md` option to indicate operation:

  - to list do: `upydev fw -md list -b [BOARD]` , board could be 'esp32', 'esp8266' or 'PYBD' for example (web scraping from [micropython downloads page](https://www.micropython.org/download/all) ) (use `list latest -b [BOARD]` to see the latest available firmware) *results can be filtered further with `-n` option, e.g. `-n idf3`
  - to get do: `upydev fw -md get [firmware file]` or `upydev fw -md get latest -b [BOARD]` to get the latest available firmware. (this uses curl) *results can be filtered further with `-n` option, e.g. `-n idf3`
  - to see available serial ports do: `upydev fw -md list serial_ports`

* **`upydev flash`**: to flash a firmware file to the upydevice, a serial port must be indicated to flash do: `upydev flash -port [serial port] -f [firmware file]` (*just for esp8266 and esp32*)
  
* **`upydev see`**: to get specific command help info indicated with `-c` option

* **`upydev find`**: to get a list of possible upy devices. Scans the local network to find devices with port 8266 (WebREPL) open. Use `-n` option to perform n scans (A single scan may not find all the devices)

* **`upydev diagnose`** to make a diagnostic test of the device (sends useful commands to get device state info)

*  **`upydev errlog`**: if `error.log` is present in the upydevice, this shows the content (`cat('error.log')`).

     If `error.log` in sd use `-s sd` (This command needs `upysh` installed, do `upydev install -f upysh`)

* **`upydev stream_test`**: to test download speed (from device to host). Default test is 10 MB of random bytes are sent in chunks of 20 kB and received in chunks of 32 kB. To change test parameters use `-chunk_tx` , `-chunk_rx`, and `-total_size`.

* **`upydev sysctl`** to start/stop a script without following the output. To follow initiate wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl) TO START: use `-start[SCRIPT_NAME]`, TO STOP: use `-stop [SCRIPT_NAME]`

* **`upydev log`** to log the output of a upydevice script, indicate script with `-f` option, and the `sys.stdout` log level and file log level with `-dslev` and `-dflev` (defaults are debug for sys.stdout and error for file). To log in background use `-daemon` option, then the log will be redirected to a file with level `-dslev`. To stop the 'daemon' log mode use `-stopd` and indicate script with `-f` option. 'Normal' file log and 'Daemon' file log are under .upydev_logs folder in `$HOME` directory, named after the name of the script. To follow an on going 'daemon' mode log, use `-follow` option and indicate the script with `-f` option.

* **`upydev update_upyutils`**: to update the latest versions of *sync_tool.py, upylog.py, upynotify.py, upysh2.py, upysecrets.py, ssl_repl.py, uping.py, time_it.py, wss_repl.py and wss_helper.py* (these are uploaded to the '/lib' folder of the upydevice)

* **`upydev debug`**: to execute a local script line by line in the target upydevice, use `-f` option to indicate the file. To enter next line press ENTER, to finish PRESS C then ENTER. To break a while loop do CTRL-C.

* **`upydev gen_rsakey`** To generate RSA-2048 bit key that will be shared with the device (it is unique for each device) use -tfkey to send this key to the device (use only if connected directly to the AP of the device or a "secure" wifi e.g. local/home). If not connected to a "secure" wifi upload the key (it is stored in upydev._*path*_) by USB/Serial connection.

* **`upydev rf_wrkey`** To "refresh" the WebREPL password with a new random password derivated from the RSA key previously generated. A token then is sent to the device to generate the same password from the RSA key previously uploaded. This won't leave any clues in the TCP Websocekts packages of the current WebREPL password. (Only the token will be visible; check this using wireshark) (This needs upysecrets.py)

* **`upydev crypto_wrepl`**:To enter the terminal CryptoWebREPL a E2EE wrepl/shell terminal; CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default) To see more keybindings info do CTRL-k. By default resets after exit, use `-rkey` option to refresh the WebREPL password with a new random password, after exit. This passowrd will be stored in the working directory or in global directory with `-g` option. (This mode needs upysecrets.py)

* **`upydev upy`** to acces crypto_wrepl in a 'ssh' style command to be used like e.g.: `upydev upy@192.168.1.42` or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. `upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass`) The device can be accesed as `upydev upy@foo_device` or redirect any command as e.g. `upydev ping -@foo_device`

* **`upydev sslgen_key`** (This needs openssl available in `$PATH`)

     To generate ECDSA key and a self-signed certificate to enable SSL sockets This needs a passphrase, that will be required every time the key is loaded. Use `-tfkey` to upload this key to the device (use only if connected directly to the AP of the device or a "secure" wifi e.g. local/home). If not connected to a "secure" wifi upload the key (it is stored in upydev._*path*_) by USB/Serial connection.

- **`upydev ssl_wrepl`**: To enter the terminal SSLWebREPL a E2EE wrepl/shell terminal (SSL sockets); CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default) To see more keybindings info do CTRL-k. By default resets after exit. (This mode needs *ssl_repl.py)* use `-rkey` option to refresh the WebREPL password with a new random password, after exit. This passowrd will be stored in the working directory or in global directory with `-g` option. (This mode needs *ssl_repl.py, upysecrets.py* for `-rfkey`) *(Use `-nem` option to use without encryption (for esp8266))
  
- **`upydev ssl`**: to acces ssl_wrepl in a 'ssh' style command to be used like e.g.: `upydev ssl@192.168.1.42` or if a device is stored in a global group called "*UPY_G*" (this needs to be created first doing e.g. `$ upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass`) The device can be accesed as `$ upydev ssl@foo_device` or redirect any command as e.g. `$ upydev ping -@foo_device`
  
- **`upydev sh_srepl`**: To enter the serial terminal SHELL-REPL; CTRL-x to exit, To see more keybindings info do CTRL-k. By default resets after exit. To configure a serial device use `-t` for baudrate and `-p` for serial port To acces without previous configuration: `sh_srepl -port [serial port] -b [baudrate]` (default baudrate is 115200) To acces with previous configuration:

   - `sh_srepl` (if device configured in current working directory)
   - `sh_srepl -@ foo_device` (if foo_device is configured in global group 'UPY_G')

- **`upydev shr`**: to acces the serial terminal SHELL-REPL in a 'ssh' style command to be used like e.g.: `upydev shr@/dev/tty.usbmodem3370377430372` or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. `upydev make_group -g -f UPY_G -devs foo_device 115200 /dev/tty.usbmodem3370377430372`) The device can be accesed as `upydev shr@foo_device`
  
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

#### uPydev Commands:

uPy commands are organized in:

* **General**: These commands should work 'out of the box' in any MicroPython running board with WebREPL daemon enabled.
* **Wifi utils** : This commands make easier to save/load wifi configuration (STA and AP ) and connect to an access point or enable its own (needs wifiutils.py in upydevice, see [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) directory)
* **SD:** These commands need *sdcard.py* in the upy device, and a sd module/shield at least.
* **INPUT**: These commands need a specific sensor module and the appropriate script in the upydevice (All these scripts are under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) directory)
    * ***ADC***: commands that make use of the ADCs from the board, or an external ADC module (ADS1115) (for external module needs 'ads1115.py' and 'init_ADS.py')
    * ***IMU***: commands that make use of the LSM9DS1 module, although other IMU modules could be easily implemented (needs 'lsm9ds1.py' and 'init_MY_IMU.py')
    * ***WEATHER***: commands that make use of the BME280 module, although other weather sensor modules could be easily implemented (needs 'bme280.py' and 'init_BME280.py')
    * ***POWER:*** commands that make use of the INA219 module.(needs 'ina219.py' and 'init_INA219.py')
* **OUTPUT:** These commands use the DAC or PWM of the board, some needs an actuator module (buzzer or motor driver and a motor) at least and the appropriate script in the upydevice.

  * ***DAC:*** to generate an analog signal (dc value, sine wave or square wave at the momment) (needs 'dac_signal_gen.py')
  * ***BUZZER***: to drive a buzzer with PWM (needs 'buzzertools.py')
  * ***DC MOTOR***: to control a DC motor (needs a motor driver and the appropriate script) (needs 'dcmotor.py')
  * ***SERVO:*** to drive a servo motor (needs 'servo.py')
  * ***STEPPER MOTOR***: to drive stepper motor (needs a motor driver and 'stepper.py')
* **NETWORKING:**
    * ***MQTT:*** commands to connect to a broker, subscribe to topic, publish and receive messages (needs 'mqtt_client.py')
    * ***SOCKETS:*** commands to start client/server socket and send/receive messages (needs 'socket_client_server.py')
    * ***UREQUEST:*** commands to make http requests, and get json or text output
* **PORT/BOARD SPECIFIC COMMANDS**:

    * battery : if running on battery, gets battery voltage (esp32 huzzah feather)
    * pinout : to see the pinout reference/info of a board, indicated by -b option,
             to request a single or a list of pins info use -po option (currently just esp32 huzzah feather)
    * specs : to see the board specs, indicated by -b option (currently just esp32 huzzah feather)
    * pin_status: to see pin state, to request a specific set use -po option



------

### DEBUG

#### RECOMMENDATION:

  >Since upydev is based in a wireless protocol connection, in order to succeed sending upydev commands make sure that there is a reliable connection between the host and the device and that the wifi signal strength (rssi) in the device is above -80  (below -80 performance could be inconsistent)

  **A 'Reliable' connection** **means that there is no packet loss**  (use ping or  `upydev ping` command to check)

  See [Received signal strength indication](https://en.wikipedia.org/wiki/Received_signal_strength_indication) and 
  [Mobile Signal Strength Recommendations](https://wiki.teltonika.lt/view/Mobile_Signal_Strength_Recommendations).

#### TRACKING PACKETS:

To see if "command packets" are sent and received or lost use [Wireshark](https://www.wireshark.org) and filter the ip of the device.

#### SEE WHAT'S GOING ON UNDER THE HOOD: 

_ℹ️ Host and the device must be connected._

  In a terminal window open a 'serial repl' with `upydev srepl --port [USBPORT]` command

  In another window use upydev normally. Now in the terminal window with the serial repl you can see which commands are sent.



------

### HOW TO

- #### [ATOM / VISUAL STUDIO CODE INTEGRATION](https://github.com/Carglglz/upydev/blob/master/DOCS/HOWTO.md)

- #### [GLOBAL GROUP CONFIGURATION](https://github.com/Carglglz/upydev/blob/master/DOCS/HOWTO.md)



____

### ABOUT

To see more information about upydev toolbox sources, requirements, tested devices, etc see [ABOUT](https://github.com/Carglglz/upydev/blob/master/DOCS/ABOUT.md) doc.