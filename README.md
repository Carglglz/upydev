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

[mpy-cross](https://gitlab.com/alelec/micropython/tree/gitlab_build/mpy-cross)

[esptool](https://github.com/espressif/esptool)

#### Tested on:

MacOS X (Mojave 10.14.5)

Raspbian GNU/Linux 9 (stretch) *(through ssh session)*

*For Raspbian `pip install mpy-cross` seems to fail, so to install upydev without mpy-cross do:*

```
$ git clone https://github.com/Carglglz/upydev.git
[...]
$ cd upydev
$ sudo pip3 install . -r rpy_rqmnts.txt
```

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

  `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g t`

  example:

  `$ upydev config -t 192.168.1.58 -p mypass -g t`

 *upydev will use local working directory configuration unless it does not find any or manually indicated with -g option.*

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

- **put** : to upload a file to upy device (*see -f, -s and -rst)*

- **get** : to download a file from upy device (*see -f and -s*)

- **sync** : for a faster transfer of large files
    (this needs sync_tool.py in upy device) (*see -f, -s and -lh*)

    *> sync_tool.py is under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) directory*

- **cmd** : for debugging purpose, to send command to upy device ; (*see -c, -r, -rl*);

   - Examples:

   `$ upydev cmd -c "led.on()"`

   `$ upydev cmd -r "print('Hello uPy')"`

   ` $ upydev cmd -rl "function_that_print_multiple_lines()"`
   
   *  *tip: simple commands can be used without quotes;*
     *but for commands with parenthesis or special characters use quoutes,*
     *for example: 'dummy_func()' ; use double quotes "" when the command*
     *includes a string like this example: "uos.listdir('/sd')"*

- **wrepl** : to enter the terminal webrepl; write *exit* or press *CTRL-C* to exit
        (see [Terminal WebREPL protocol](https://github.com/Hermann-SW/webrepl) for more information)

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
      - to list do: "upydev fw -md list -b [BOARD]" board should be 'esp32' or 'esp8266' (web scraping from [micropython downloads page](https://www.micropython.org/downloads) )
      - to get do: "upydev fw -md get [firmware file]" (uses curl)
      -  to see available serial ports do: "upydev fw -md list serial_ports"
  
* **flash**: to flash a firmware file to the upydevice, a serial port must be indicated
              to flash do: "upydev flash -port [serial port] -f [firmware file]"
          
* **see**:  to get specific command help info indicated with -c option

* **make_group:** to make a group of boards to send commands to. Use -f for the name of the group 

     ​	and -devs option to indicate a name, ip and the password of each board.

**GROUP COMMAND MODE (-G option)**: 

To send a command to multiple devices in a group (made with make_group command) use -G option

 Usage: `upydev [command] -G [GROUP NAME]`

To target specific devices within a group add -devs option as `-devs [DEV_1 NAME] [DEV_2 NAME]`

------

#### uPydev Commands:

uPy commands are organized in:

* **General**: These commands should work 'out of the box' in any Micropython running board with WebREPL daemon enabled.

* **SD:** These commands need *sdcard.py* in the upy device, and a sd module/shield at least.

* **INPUT**: These commands need a specific sensor module and the appropriate script in the upydevice (All these scripts are under [upyutils](https://github.com/Carglglz/upydev/tree/master/upyutils) directory)
    * ***ADC***: commands that make use of the ADCs from the board, or an external ADC module (ADS1115) (for external module needs 'ads1115.py' and 'init_ADS.py')
    * ***IMU***: commands that make use of the LSM9DS1 module, although other IMU modules could be easily implemented (needs 'lsm9ds1.py' and 'init_MY_IMU.py')
    * ***WEATHER***: commands that make use of the BME280 module, although other weather sensor modules could be easily implemented (needs 'bme280.py' and 'init_BME280.py')
    * ***POWER:*** commands that make use of the INA219 module.

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

