

<img align="right" width="100" height="100" src="uPydevlogo.png">



# uPydev

### Command line tool for wireless Micropython devices

**uPydev** is an acronym of '**Micropy**thon **dev**ice', and it is intended to be a command line tool to make easier the development, prototyping and testing process of devices based on boards running Micropython.

 It is a command line tool for 'wireless Micropython devices' since it make use of the [WebREPL protocol](https://github.com/micropython/webrepl)  to provide communication with and control of the device.

*uPydev is built on top of other tools/scripts which are:

The core is 'webrepl_client.py ' : a [Terminal WebREPL protocol](https://github.com/Hermann-SW/webrepl) as seen in this [WebREPL pull request](https://github.com/micropython/webrepl/pull/37) by [@Hermann-SW](https://github.com/Hermann-SW)

Other tools are:

'webrepl_cli.py'  for the file transfer protocol (from the WebREPL repo of micropython) (modified and named 'upytool')

'esptool.py' to flash the firmware into esp boards

'mpy-cross'  to compile .py scripts into .mpy files.

***Keep in mind that this project is in ALPHA state, sometimes, some commands may not work/return anything***

### Features:

* Command line wireless communication/control of micropython devices.
* Terminal WebREPL protocol
* Custom commands to automate communication/control
* Command line autocompletion

### Getting Started

First be sure that the WebREPL daemon is enabled and running see [webrepl-a-prompt-over-wifi](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi) and

[webrepl-web-browser-interactive-prompt](http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt)

#### Requirements:

WebREPL enabled

Python modules (automatically installed using pip):

[argcomplete](https://github.com/kislyuk/argcomplete) (for command line autocompletion)

[prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) (for new WebREPL Terminal implementation)

[mpy-cross](https://gitlab.com/alelec/micropython/tree/gitlab_build/mpy-cross)

[esptool](https://github.com/espressif/esptool)

[python-nmap](http://xael.org/pages/python-nmap-en.html)

[netifaces](https://github.com/al45tair/netifaces)

[requests](https://requests.kennethreitz.org/en/master/)

[cryptography]()

[upydevice](https://github.com/Carglglz/upydevice)

#### Tested on:

MacOS X (Mojave 10.14.5-6)

Raspbian GNU/Linux 9 (stretch) *(through ssh session)*

*For Raspbian `pip install mpy-cross` seems to fail, so to install upydev without mpy-cross do:*

```
$ git clone https://github.com/Carglglz/upydev.git
[...]
$ cd upydev
$ sudo pip3 install . --no-deps -r rpy_rqmnts.txt
```

Then to install upydevice see instructions in [upydevice repo](https://github.com/Carglglz/upydevice)

upy Boards:

Esp32 Huzzah feather

Esp8266 Huzzah feather

#### Installing using pip:

`$ pip install upydev`

#### Quick Reference:

##### Help:

In CLI do :

`$ upydev -h`

##### Configurate uPy Device:

1st step: Configurate upy device target and password:

- To save configuration in working directory:

  `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD]`

  example:

  `$ upydev config -t 192.168.1.58 -p mypass`

* To save configuration globally use -g option:

  `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g `

  example:

  `$ upydev config -t 192.168.1.58 -p mypass -g `

 *upydev will use local working directory configuration unless it does not find any or manually indicated with -g option.*

**Make a global group of uPy devices named "UPY_G" to enable redirection to a specific device:**  ** (**New in version 0.1.7**)

Make a global group named "UPY_G" of devices, so next time any command can be redirected to any device within the group:

Example:

`$ upydev make_group -g -f UPY_G -devs esp_room1 192.168.1.42 mypass esp_room2 192.168.1.54 mypass2`

To see the devices saved in this global group do:

```
$ upydev see -G UPY_G -g
GROUP NAME: UPY_G
# DEVICES: 2
DEVICE NAME: esp_room1, IP: 192.168.1.42
DEVICE NAME: esp_room2, IP: 192.168.1.54
```

*To add or remove devices from this group use "mg_group" command (see uPydev Mode/Tools)*

Now any command can be redirected to one of these devices with the "-@" option:

```
$ upydev info -@ esp_room1
SYSTEM NAME: esp32
NODE NAME: esp32
RELEASE: 1.12.0
VERSION: v1.12 on 2019-12-20
MACHINE: ESP32 module with ESP32
```

*Option "-@" has autocompletion on tab so hit tab and see what devices are available*

***New in version 0.1.7: Mode 'crypto_wrepl', a repl/shell with encryption mode** (*experimental)

The idea behind this mode is to try to mimic a SSH protocol. (But right now although encryption works this doesn't mean it is secure. )

(This mode needs upysh in the device, so if it is not already installed or it's not included in the frozen modules do: `$ upydev install -f upysh`)

How to use it:

* TLDR: To test the functionality of this mode **without encryption** do:

  `$ upydev crypto_wrepl -nem`

* With **Encryption mode**: This needs some configuration before (which is basically generate an RSA private key and pass it to the device). Follow [this instructions](https://github.com/Carglglz/upydev/blob/master/DOCS/crypto_wrepl_docs.md) to do this.

  After the configuration is done, to use this mode do:

  `$ upydev crypto_wrepl` 

  Or if there is already a global "UPY_G" named group, any device can be accessed with this mode using:

  e.g.:

  `$ upydev upy@esp_room1`  or `$ upydev upy@192.168.1.42` 

  ![](https://raw.githubusercontent.com/Carglglz/upydev/master/DOCS/CryptoWebREPL_demo.gif)

------

#### uPydev Usage:

Usage:

`$ upydev [Mode] [options] or upydev [upy command] [options]`

This means that if the first argument is not a Mode keyword or a
upy command keyword it assumes it is a 'raw' upy command to send to the upy device

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

- **config** : to save upy device settings (*see -p, -t, -g)*,
            so the target and password arguments wont be required any more

- **put** : to upload a file to upy device (*see -f, -s , -dir, -rst; for multiple files see -fre option)*

- **get** : to download a file from upy device (*see -f , -dir, -s; for multiple files see -fre option*)

- **sync** : for a faster transfer of large files
    (this needs sync_tool.py in upy device) (*see -f, -s and -lh*; for multiple files see -fre option)

    *> sync_tool.py is under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) directory*

- **d_sync**: to recursively sync a folder in upydevice filesystem use -dir  to indicate the folder (must be in cwd), use '-tree' to see dir structure, or '-s sd' to sync to an Sd card mounted as 'sd'

- **cmd** : for debugging purpose, to send command to upy device ; (*see -c, -r, -rl*);

   - Examples:

   `$ upydev cmd -c "led.on()"`

   `$ upydev cmd -r "print('Hello uPy')"`

   ` $ upydev cmd -rl "function_that_print_multiple_lines()"`
   
   *  *tip: simple commands can be used without quotes;*
     *but for commands with parenthesis or special characters use quotes,*
     *for example: 'dummy_func()' ; use double quotes "" when the command*
     *includes a string like this example: "uos.listdir('/sd')"*

- **wrepl** :to enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
    To see more keybinding info do CTRL-k
 (Added custom keybindings and autocompletion on tab to the previous work
     see: [Terminal WebREPL](https://github.com/Hermann-SW/webrepl) for the original work)
    
- **srepl** : to enter the terminal serial repl using picocom, indicate port by -port option
            (to exit do CTRL-a, CTRL-x) (see: [Picocom](https://github.com/npat-efault/picocom) for more information)

- **ping** : pings the target to see if it is reachable, *CTRL-C* to stop

- **run** : just calls import 'script', where 'script' is indicated by -f option
        (script must be in upy device or in sd card indicated by -s option
        and the sd card must be already mounted as 'sd');

    ​	Supports *CTRL-C* to stop the execution and exit nicely.

- **install** : install libs to '/lib' path with upip; indicate lib with -f option

- **mpyx** : to froze a module/script indicated with -f option, and save some RAM,
         it uses mpy-cross tool (see [mpy-cross](https://gitlab.com/alelec/micropython/tree/gitlab_build/mpy-cross) for more information)

- **timeit**: to measure execution time of a module/script indicated with -f option.

  This is an adapted version of [timed_function](https://github.com/peterhinch/micropython-samples/tree/master/timed_function)


* **fw**: to list or get available firmware versions, use -md option to indicate operation:
  
  - to list do: "upydev fw -md list -b [BOARD]" , board could be 'esp32', 'esp8266' or 'PYBD' for example (web scraping from [micropython downloads page](https://www.micropython.org/downloads) ) (use 'list latest -b [BOARD]' to see the latest available firmware)  *results can be filtered further with '-n' option, e.g. '-n idf3'
  - to get do: "upydev fw -md get [firmware file]" or 'upydev fw -md get latest -b [BOARD]' to get the latest available firmware. (this uses curl) *results can be filtered further with '-n' option, e.g. '-n idf3'
  - to see available serial ports do: "upydev fw -md list serial_ports"
  
* **flash**: to flash a firmware file to the upydevice, a serial port must be indicated
              to flash do: "upydev flash -port [serial port] -f [firmware file]" (*just for esp8266 and esp32)
          
* **see**:  to get specific command help info indicated with -c option

* **find**: to get a list of possible upy devices. Scans the local network to find devices with port 8266     (WebREPL) open. Use -n option to perform n scans (A single scan may not find all the devices)

* **diagnose:** to make a diagnostic test of the device (sends useful commands to get device state info)

*  **errlog**: if 'error.log' is present in the upydevice, this shows the content (cat('error.log')).

     If 'error.log' in sd use -s sd (This command needs upysh installed, do `upydev install -f upysh`)

* **stream_test**: to test download speed (from device to host). Default test is 10 MB of random bytes are sent in chunks of 20 kB and received in chunks of 32 kB. To change test parameters use -chunk_tx , chunk_rx, and -total_size.

* **sysctl:** to start/stop a script without following the output. To follow initiate wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl) TO START: use -start [SCRIPT_NAME], TO STOP: use -stop [SCRIPT_NAME]

* **log:** to log the output of a upydevice script, indicate script with -f option, and the sys.stdout log level and file log level with -dslev and -dflev (defaults are debug for sys.stdout and error for file). To log in background use -daemon option, then the log will be redirected to a file with level -dslev. To stop the 'daemon' log mode use -stopd and indicate script with -f option. 'Normal' file log and 'Daemon' file log are under .upydev_logs folder in $HOME directory, named after the name of the script. To follow an on going 'daemon' mode log, use -follow option and indicate the script with -f option.

* **update_upyutils**: to update the last versions of sync_tool.py, upylog.py and upynotify.py (these are uploaded to the '/lib' folder of the upydevice)

* **debug**: to execute a local script line by line in the target upydevice, use -f option to indicate the file. To enter next line press ENTER, to finish PRESS C then ENTER. To break a while loop do CTRL+C.

* **gen_rsakey:** To generate RSA-2048 bit key that will be shared with the device (it is unique for each device) use -tfkey to send this key to the device (use only if connected directly to the AP of the device or a "secure" wifi e.g. local/home). If not connected to a "secure" wifi upload the key (it is stored in upydev.\__path__) by USB/Serial connection.

* **rf_wrkey:** To "refresh" the WebREPL password with a new random password derivated from the RSA key previously generated. A token then is sent to the device to generate the same password from the RSA key previously uploaded. This won't leave any clues in the TCP Websocekts packages of the current WebREPL password. (Only the token will be visible; check this using wireshark)  (This needs upysecrets.py)

* **crypto_wrepl**:To enter the terminal CryptoWebREPL a E2EE wrepl/shell terminal; CTRL-x to exit, CTRL-u to toggle encryption mode (enabled by default) To see more keybindings info do CTRL-k. By default resets after exit, use -rkey option to refresh the WebREPL password with a new random password, after exit. This passowrd will be stored in the working directory or in global directory with -g option. (This mode needs upysecrets.py)

* **upy:** to acces crypto_wrepl in a 'ssh' style command to be used like e.g.: "upydev upy@192.168.1.42" or if a device is stored in a global group called "UPY_G" (this needs to be created first doing e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass") The device can be accesed as "upydev upy@foo_device" or redirect any command as e.g. "upydev ping -@foo_device"

* **make_group**: to make a group of boards to send commands to. Use -f for the name of the group 

     and -devs option to indicate a name, ip and the password of each board. (To store the group settings globally use -g option)
     
* **mg_group**: to manage a group of boards to send commands to. Use -G for the name of the group and -add option to add devices (indicate a name, ip and the password of each board) or -rm to remove devices (indicated by name)

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

* **General**: These commands should work 'out of the box' in any Micropython running board with WebREPL daemon enabled.
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

#### Extensive explanation:

For an extensive explanation and commands demo see [Documentation](https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md).

#### Addiontal Scripts for some commands:

The commands that need additional scripts in the upy device are under the [uPyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) folder.

For more info see [upyutils_docs](https://github.com/Carglglz/upydev/blob/master/DOCS/upyutils_docs.md).

------

#### USEFUL DEVELOPER TOOLS: (*Under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) folder*)

* [**upylog**](https://github.com/Carglglz/upydev/tree/master/DOCS/upylog.md): MicroPython logging module with time format (predefined) and log to file support.
* [**upynotify**](https://github.com/Carglglz/upydev/tree/master/DOCS/upynotify.md) : module with NOTIFIER class to notify events with beeps and blinks. 

------

### HOW TO:

- #### **ATOM/VSC INTEGRATION** (PLATFORMIO TERMINAL) 

  - ##### ATOM:

    To do this go to `Atom Settings --> Packages -->` Then search for `platformio-ide-terminal` and click on `Settings`. Here go to `Custom Texts` section: (There are up to 8 "custom texts" or commands that can be customised) These custom text will be pasted an executed in the Terminal when called. And this can be done with keybindings or key-shortcuts. For example:

    - **To automate upload the current file:**

      In `Custom text 1`  write:  `upydev put -f $F` 

    - **To automate run the current file:**

      In `Custom text 2`  write:  `upydev run -f $F` 

    - **To automate open the wrepl:**

      In `Custom text 3`  write:  `upydev wrepl`

    - **To automate diagnose:**

      In `Custom text 4`  write:  `upydev diagnose` 

      

    Now configure the Keybindings, to do this go to `Settings --> Keybindings --> your keymap file` 

    Then in `keymap.cson` add: (This is an example, the key combination can be changed)

    ```
    'atom-workspace atom-text-editor:not([mini])':
      'ctrl-shift-d': 'platformio-ide-terminal:insert-custom-text-4'
      'ctrl-cmd-u': 'platformio-ide-terminal:insert-custom-text-1'
      'ctrl-cmd-x': 'platformio-ide-terminal:insert-custom-text-2'
      'ctrl-cmd-w': 'platformio-ide-terminal:insert-custom-text-3'
    ```

     Save the file and now when pressing these key combinations should paste the command and run it in the Terminal.

  - ##### VSC:

    Using tasks and adding the shortcut in keybinds.json file for example:

    Task:

    ```json
    "version": "2.0.0",
        "tasks": [
            {
                "label": "upydev_upload",
                "type": "shell",
                "command": "upydev",
                "args": ["put", "-f", "${file}"],
                "options": {
                    "cwd": "${workspaceFolder}"
                },
                "presentation": {
                    "echo": true,
                    "reveal": "always",
                    "focus": true,
                    "panel": "shared",
                    "showReuseMessage": true,
                    "clear": false
                },
                "problemMatcher": []
            }, ]
    ```

    Keybinding.json

    ```json
    {
            "key": "ctrl+cmd+u",
            "command": "workbench.action.tasks.runTask",
            "args": "upydev_upload"
        }
    ```

    

- #### DEBUG :

  ##### *RECOMMENDATION:

  **Since upydev is based in a wireless protocol connection, in order to succes sending upydev commands make sure that there is a reliable connection* between the host and the device** **and that the wifi signal strength (rssi) in the device is above -80 ** *(below -80 performance could be inconsistent*)

  **A 'Reliable' connection** **means that there is no packet loss**  (use ping or  `upydev ping` command to check)

  See https://en.wikipedia.org/wiki/Received_signal_strength_indication and

  https://wiki.teltonika.lt/view/Mobile_Signal_Strength_Recommendations.

  ##### *TRACKING PACKETS:

  **To see if "command packets" are sent and received or lost use [wireshark](https://www.wireshark.org) and filter the ip of the device** 

  ##### * SEE WHAT'S GOING ON UNDER THE HOOD: 

  ##### *(THIS NEEDS THAT THE HOST AND THE DEVICE TO BE CONNECTED BY USB)

  In a terminal window open a 'serial repl' with `upydev srepl --port /dev/tty.[USBPORT]` command

  In another window use upydev normally. Now in the terminal window with the serial repl you can see which commands are sent.