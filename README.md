<img align="right" width="100" height="100" src="uPydevlogo.png">

# uPydev

### Command line tool for wireless Micropython devices

Name, AIM, description, source ideas/code etc...

### Getting Started



#### Requirements:



#### Tested on:



#### Installing using pip:

`$ pip install upydev`

#### Quick Reference:

##### Help:

In cli :

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

##### uPydev Usage:

Usage:

`$ upydev [Mode] [options] or upydev [upy command] [options]`

This means that if the first argument is not a Mode keyword or a
upy command keyword it assumes it is a 'raw' upy command to send to the upy device

Example: Mode

`$ upydev put -f dummy.py`

Example: uPy command

`$ upydev info`

Example: Raw command

`$ upydev "my_func()"`

`$ upydev 2+1`

`$ upydev "import my_lib;foo();my_var=2*3"`

##### uPydev Mode/Tools:

- **config** : to save upy device settings (*see -p, -t, -g)*,
            so the target and password arguments wont be required any more

- **put** : to upload a file to upy device (*see -f, -s and -rst)*

- **get** : to download a file from upy device (*see -f and -s*)

- **sync** : for a faster transfer of large files
    (this needs sync_tool.py in upy device) (*see -f, -s and -lh*)

    *> sync_tool.py is under upyutils directory*

- **cmd** : for debugging purpose, to send command to upy device ; (*see -c, -r, -rl*);

   - Examples:

   `$ upydev cmd -c "led.on()"`

   `$ upydev cmd -r "print('Hello uPy')"`

   ` $ upydev cmd -rl "function_that_print_multiple_lines()"`

   

    * *tip: simple commands can be used without quotes;*
        *but for commands with parenthesis or special characters use quoutes,*
        *for example: 'dummy_func()' ; use double quotes "" when the command*
        *includes a string like this example: "uos.listdir('/sd')"*

- **wrepl** : to enter the terminal webrepl; write *exit* or press *CTRL-C* to exit
        (see: https://github.com/Hermann-SW/webrepl for more information)

- **ping** : pings the target to see if it is reachable, *CTRL-C* to stop

- **run** : just calls import 'script', where 'script' is indicated by -f option
        (script must be in upy device or in sd card indicated by -s option
        and the sd card must be already mounted as 'sd');

    ​	Supports *CTRL-C* to stop the execution and exits nicely.

    
    
- **install** : install libs to '/lib' path with upip; indicate lib with -f option

- **mpyx** : to froze a module/script indicated with -f option, and save some RAM,
         it uses mpy-cross tool (see https://gitlab.com/alelec/mpy_cross)

- **timeit**: to measure execution time of a module/script indicated with -f option.

  This is an adapted version of:
  
   https://github.com/peterhinch/micropython-samples/tree/master/timed_function

##### uPydev Commands:

uPy commands are organized as:

* **General**: These commands should work 'out of the box' in any Micropython running board with WebREPL daemon enabled.

* **SD:** These commands need *sdcard.py* in the upy device, and a sd module/shield at least.

* **INPUT**: These commands need a specific sensor module and the appropriate script in the upydevice (All these scripts are under upyutils directory)

  * ***ADC***: commands that make use of the ADCs from the board, or an external ADC module (ADS1115)
  * ***IMU***: commands that make of the LSM9DS1 module, although other IMU modules could be easily implemented
  * ***Power:*** commands that make use of the INA219 module

  

##### Extensive explanation under:

DOCS

##### Addiontal Scripts for some commands:

Explanation which one and where to find (also source)

uPyutils
