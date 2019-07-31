<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [uPydev Mode/Tools:](#upydev-modetools)
	- [config](#config)
	- [put](#put)
	- [get](#get)
	- [sync](#sync)
	- [cmd](#cmd)
	- [wrepl](#wrepl)
	- [ping](#ping)
	- [run](#run)
	- [install](#install)
	- [mpyx](#mpyx)
	- [timeit](#timeit)
- [upy Commands:](#upy-commands)
	- [GENERAL](#general)
		- [info](#info)
		- [id](#id)
		- [upysh](#upysh)
		- [reset](#reset)
		- [uhelp](#uhelp)
		- [umodules](#umodules)
		- [mem_info](#meminfo)
		- [filesize](#filesize)
		- [filesys_info](#filesysinfo)
		- [netinfo](#netinfo)
		- [netinfot](#netinfot)
		- [netscan](#netscan)
		- [netstat_on](#netstaton)
		- [netstat_off](#netstatoff)
		- [netstat_conn](#netstatconn)
		- [netstat](#netstat)
		- [ap_on](#apon)
		- [ap_off](#apoff)
		- [apstat](#apstat)
		- [apconfig](#apconfig)
		- [apscan](#apscan)
		- [i2c_config](#i2cconfig)
		- [i2c_scan](#i2cscan)
		- [spi_config](#spiconfig)
		- [set_localtime](#setlocaltime)
		- [set_ntptime](#setntptime)
		- [get_datetime](#getdatetime)
	- [SD](#sd)
		- [sd_enable](#sdenable)
		- [sd_init](#sdinit)
		- [sd_deinit](#sddeinit)
		- [sd_auto](#sdauto)
	- [INPUT](#input)
		- [ADC](#adc)
			- [adc_config](#adcconfig)
			- [aread](#aread)
			- [ads_init](#adsinit)
			- [ads_read](#adsread)
		- [IMU](#imu)
			- [imu_init](#imuinit)
			- [imuacc](#imuacc)
			- [imuacc_sd](#imuaccsd)
			- [imugy](#imugy)
			- [imumag](#imumag)
		- [POWER](#power)
	- [OUTPUT](#output)
		- [DAC](#dac)
			- [dac_config](#dacconfig)
			- [dac_write](#dacwrite)
			- [dac_sig](#dacsig)
		- [BUZZER:](#buzzer)
			- [buzz_config](#buzzconfig)
			- [buzz_set_alarm](#buzzsetalarm)
			- [buzz_interrupt](#buzzinterrupt)
			- [buzz_beep](#buzzbeep)
		- [DC MOTOR](#dc-motor)
			- [dcmotor_config](#dcmotorconfig)
			- [dcmotor_move](#dcmotormove)
			- [dcmotor_stop](#dcmotorstop)
		- [SERVO:](#servo)
			- [servo_config](#servoconfig)
			- [servo_angle](#servoangle)
		- [STEPPER MOTOR:](#stepper-motor)
			- [stepper_config](#stepperconfig)
			- [stepper_move](#steppermove)
	- [NETWORKING:](#networking)
		- [MQTT:](#mqtt)
			- [mqtt_config](#mqttconfig)
			- [mqtt_conn](#mqttconn)
			- [mqtt_sub](#mqttsub)
			- [mqtt_pub](#mqttpub)
			- [mqtt_check](#mqttcheck)
		- [SOCKETS:](#sockets)
			- [socli_init](#socliinit)
			- [socli_conn](#socliconn)
			- [socli_send](#soclisend)
			- [socli_recv](#soclirecv)
			- [sosrv_init](#sosrvinit)
			- [sosrv_start](#sosrvstart)
			- [sosrv_send](#sosrvsend)
			- [sosrv_recv](#sosrvrecv)
		- [UREQUEST:](#urequest)
			- [rget_json](#rgetjson)
			- [rget_text](#rgettext)
	- [Port/board specific commands:](#portboard-specific-commands)
		- [battery](#battery)
		- [pinout](#pinout)
		- [specs](#specs)
			- [pin_status](#pinstatus)
		- [ESP32:](#esp32)
			- [touch](#touch)
			- [hall](#hall)
			- [deepsleep](#deepsleep)
			- [temp](#temp)

<!-- /TOC -->

# uPydev Mode/Tools:

## config

 to save upy device settings (see -p, -t, -g), (saves a config file 'upydev_.config')

so the target and password arguments wont be required any more

- To save configuration in working directory:

  `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD]`

  example:

  ```
  $ upydev config -t 192.168.1.58 -p mypass
  upy device settings saved in working directory!
  ```

- To save configuration globally use -g option:

  `$ upydev config -t [UPYDEVICE IP] -p [PASSWORD] -g t`

  example:

  ```
  $ upydev config -t 192.168.1.58 -p mypass -g t
  upy device settings saved globally!
  ```

  

 *upydev will use local working directory configuration unless it does not find any or manually indicated with -g option.*

## put

to upload a file to upy device (see -f, -s and -rst)

Usage: `$ upydev put -f [filename] [options]` 

Examples:

```
$ upydev put -f dummy_script.py
Uploading file dummy_script.py...
op:put, host:192.168.1.53, port:8266, passwd:*******.
dummy_script.py -> /dummy_script.py
Remote WebREPL version: (1, 11, 0)
Sent 44 of 44 bytes
File Uploaded!
Rebooting upy device...
Done!
```

*By default upydev sends a reset command after uploading a new file, to disable reset use -rst f*

*Default target directory in upy device is root directory which is in flash memmory, to change target directory to an sd use -s sd (so that means that the sd must be already mounted as 'sd'* 

Disabling reset:

```
$ upydev put -f dummy_script.py -rst f
Uploading file dummy_script.py...
op:put, host:192.168.1.53, port:8266, passwd:*******.
dummy_script.py -> /dummy_script.py
Remote WebREPL version: (1, 11, 0)
Sent 44 of 44 bytes
File Uploaded!
```

Uploading to sd:

```
$ upydev put -f dummy_script.py -rst f -s sd
Uploading file dummy_script.py...
op:put, host:192.168.1.53, port:8266, passwd:*******.
dummy_script.py -> /sd/dummy_script.py
Remote WebREPL version: (1, 11, 0)
Sent 44 of 44 bytes
File Uploaded!
```



## get

to download a file from upy device (see -f and -s)

Usage: `$ upydev get -f [filename] [options]` 

Examples:

```
$ upydev get -f dummy_script.py
Looking for file in upy device root dir
Getting file dummy_script.py...
op:get, host:192.168.1.53, port:8266, passwd:*******.
dummy_script.py -> ./dummy_script.py
Remote WebREPL version: (1, 11, 0)
Received 44 bytes
```

*Default target directory in upy device is root directory which is in flash memmory, to change target directory to an sd use -s sd (so that means that the sd must be already mounted as 'sd'* 

To get a file from sd:

```
$ upydev get -f dummy_script.py -s sd
Looking in SD memory...
Getting file dummy_script.py...
op:get, host:192.168.1.53, port:8266, passwd:*******.
/sd/dummy_script.py -> ./dummy_script.py
Remote WebREPL version: (1, 11, 0)
Received 44 bytes
```



## sync

*get operation use webrepl_cli.py and when it comes to 'large' files (+100 KB) is quite slow*

*this mode was created to get log files from sd*

for a faster transfer of large files
(this needs sync_tool.py in upy device) (see -f, -s and -lh)

```
$ upydev sync -f logACC_26_6_2019_0_18_42.txt -s sd
Looking in SD memory...
Getting file logACC_26_6_2019_0_18_42.txt...
logACC_26_6_2019_0_18_42.txt             Size:   490.3 KB
Server listening...
Connection received...
Syncing file logACC_26_6_2019_0_18_42.txt from upy device
Saving logACC_26_6_2019_0_18_42.txt file
Done in 5.55 seconds
```

*it creates a server and a client and transfer the file using a tcp socket*

*the server is the computer and the client the upy device*

*if not using MacOS use -lh to indicate the local ip*

*Linux automatic local ip detection is still on the way...*

## cmd

for debugging purpose, to send command to upy device ; (*see -c, -r, -rl*);

- Examples:

This send the command and returns without response

`$ upydev cmd -c "led.on()"` 

This sends a command a waits for a response (single line)

```
$ upydev cmd -r "print('Hello uPy')"
Hello uPy
```

This sends a command a waits for a response (multiple lines)


```
$ upydev cmd -rl "import dummy_script"
Hello there!
Hello there!
Hello there!
Hello there!
Hello there!
```



- *tip: simple commands can be used without quotes;*
  *but for commands with parenthesis or special characters use quoutes,*
  *for example: 'dummy_func()' ; use double quotes "" when the command*
  *includes a string like this example: "uos.listdir('/sd')"*

## wrepl

to enter the terminal webrepl; write 'exit' or press CTRL-C to exit
(see: [Terminal WebREPL](https://github.com/Hermann-SW/webrepl) for more information)

```
$ upydev wrepl
Password:
WebREPL connected
>>>
>>>
MicroPython v1.11-37-g62f004ba4 on 2019-06-09; ESP32 module with ESP32
Type "help()" for more information.
>>> print('Hello')
Hello
>>> led.on()
>>> led.off()
>>> ^C### closed ###
```



## ping

pings the target to see if it is reachable, CTRL-C to stop \n

```
$ upydev ping
PING 192.168.1.53 (192.168.1.53): 56 data bytes
64 bytes from 192.168.1.53: icmp_seq=0 ttl=255 time=26.424 ms
64 bytes from 192.168.1.53: icmp_seq=1 ttl=255 time=49.121 ms
64 bytes from 192.168.1.53: icmp_seq=2 ttl=255 time=72.531 ms
64 bytes from 192.168.1.53: icmp_seq=3 ttl=255 time=93.594 ms
64 bytes from 192.168.1.53: icmp_seq=4 ttl=255 time=115.345 ms
64 bytes from 192.168.1.53: icmp_seq=5 ttl=255 time=33.658 ms
64 bytes from 192.168.1.53: icmp_seq=6 ttl=255 time=55.945 ms
64 bytes from 192.168.1.53: icmp_seq=7 ttl=255 time=179.598 ms
^C
--- 192.168.1.53 ping statistics ---
8 packets transmitted, 8 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 26.424/78.277/179.598/47.350 ms
```



## run

just calls import 'script', where 'script' is indicated by -f option
(script must be in upydevice or in sd card indicated by -s option
and the sd card must be already mounted as 'sd');

Supports CTRL-C to stop the execution and exits nicely.

Example: (dummy script with ZeroDivisionError to show traceback output.)

```
$ upydev run -f udummy.py
Running udummy.py...
hello dummy!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "udummy.py", line 16, in <module>
ZeroDivisionError: divide by zero

Done!
```

Infinite loop dummy script to show CTRL-C stop.

```
$ upydev run -f dummy_inf_loop.py
Running dummy_inf_loop.py...
hello dummy!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
^C...closing...
### closed ###
Done!
```



## install

install libs to '/lib' path with upip; indicate lib with -f option

```
$ upydev install -f logging
Looking for logging lib...
Installing to: /lib/
Warning: micropython.org SSL certificate is not validated
Installing logging 0.3 from https://micropython.org/pi/logging/logging-0.3.tar.gz

Library logging installed!
```



## mpyx

to froze a module/script indicated with -f option, and save some RAM,
it uses mpy-cross tool (see [mpy-cross](https://gitlab.com/alelec/mpy_cross) )

```
$ upydev mpyx -f dummy_script.py
$ ls
dummy_script.mpy		dummy_script.py			logACC_26_6_2019_0_18_42.txt	upydev_.config
```

## timeit

to measure execution time of a module/script indicated with -f option.
This is an implementation of [timed_function](https://github.com/peterhinch/micropython-samples/tree/master/timed_function)

```
$ upydev timeit -f dummy_time.py
Running dummy_time.py...
hello dummy!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
bye bye!
Script dummy_time Time = 165.696ms

Done!
```



## fw

to list or get available firmware versions, (webscraping from [micropython downloads page](https://www.micropython.org/downloads) ) use -md option to indicate operation:

 to list do: "upydev fw -md list -b [BOARD]" board should be 'esp32' or 'esp8266'

```
$ upydev fw -md list -b esp32
Firmware versions found for esp32:
esp32-20190731-v1.11-183-ga8e3201b3.bin
esp32-20190529-v1.11.bin
esp32-20190125-v1.10.bin
esp32-20180511-v1.9.4.bin
esp32--bluetooth.bin
esp32spiram-20190731-v1.11-183-ga8e3201b3.bin
esp32spiram-20190529-v1.11.bin
esp32spiram-20190125-v1.10.bin
```

 to get do: "upydev fw -md get [firmware file]"

```
upydev fw -md get esp32-20190731-v1.11-183-ga8e3201b3.bin
Downloading esp32-20190731-v1.11-183-ga8e3201b3.bin ...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 1149k  100 1149k    0     0  1375k      0 --:--:-- --:--:-- --:--:-- 1376k

Done!
```

to see available serial ports do: "upydev fw -md list serial_ports"

```
$ upydev fw -md list serial_ports
Available Serial ports are:
/dev/tty.SOC
/dev/tty.MALS
/dev/tty.Bluetooth-Incoming-Port
/dev/tty.VHP-TW20BK-SerialPort
```

## flash

to flash a firmware file to the upydevice, a serial port must be indicated 

to flash do: "upydev flash -port [serial port] -f [firmware file]"

```
$ upydev flash -port /dev/tty.SLAB_USBtoUART -f esp32-20190731-v1.11-183-ga8e3201b3.bin
Flashing firmware esp32-20190731-v1.11-183-ga8e3201b3.bin ...
esptool.py v2.6
Serial port /dev/tty.SLAB_USBtoUART
Connecting........_
Chip is ESP32D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, Coding Scheme None
MAC: 30:ae:a4:1e:73:f8
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Auto-detected Flash size: 4MB
Compressed 1177312 bytes to 735861...
Wrote 1177312 bytes (735861 compressed) at 0x00001000 in 64.9 seconds (effective 145.2 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...

Done!
```



## see

to get specific command help info indicated with -c option.

```
$ upydev see -c get
 to download a file from upy device (see -f and -s)
$ upydev see -c config
 to save upy device settings (see -p, -t, -g), so the target and password arguments wont be required any more
```



# upy Commands:

## GENERAL

### info

 for upy device system info

### id

for upy device unique id

### upysh

to enable the upy shell in the upy device (then do 'upydev man' to
acces upysh manual info)

### reset

to do a soft reset in upy device

### uhelp

just calls micropython help

### umodules

just calls micropython help('modules')

### mem_info

for upy device RAM memory info; call it once to check actual memory,
call it twice and it will free some memory

### filesize

 to get the size of file in root dir (default) or sd with '-s sd' option;
if no file name indicated with -f option, prints all files

### filesys_info

to get memory info of the file system, (total capacity, free, used),
(default root dir, -s option to change)

### netinfo

for upy device network info if station is enabled and connected to an AP

### netinfot

same as netinfo but in table format

### netscan

for upy device network scan

### netstat_on

for enable STA

### netstat_off

for disable STA

### netstat_conn

for connect to an AP , must provide essid and password (see -wp)

### netstat

STA state ; returns True if enabled, False if disabled

### ap_on

for enable AP

### ap_off

for disable AP

### apstat

 AP state ; returns True if enabled, False if disabled

### apconfig

AP configuration of essid and password with authmode WPA/WPA2/PSK,
(see -ap), needs first that the AP is enabled (do 'upydev ap_on')

### apscan

scan devices connected to AP; returns number of devices and mac address

### i2c_config

to configurate the i2c pins (see -i2c, defaults are SCL=22, SDA=23)

### i2c_scan

to scan i2c devices (must config i2c pins first)

### spi_config

to configurate the spi pins (see -spi, defaults are SCK=5,MISO=19,MOSI=18,CS=21)

### set_localtime

to pass host localtime and set upy device rtc

### set_ntptime

to set rtc from server, (see -utc for time zone)

### get_datetime

to get date and time (must be set first, see above commands)

## SD

### sd_enable

to enable/disable the LDO 3.3V regulator that powers the SD module
use -po option to indicate the Pin.

### sd_init

to initialize the sd card; (spi must be configurated first)
create sd object and mounts as a filesystem, needs sdcard.py from []

### sd_deinit

to unmount sd card

### sd_auto

experimental command, needs a sd module with sd detection pin
and the SD_AM.py script (see more info in []). Enable an Interrupt
with the sd detection pin, so it mounts the sd when is detected,
and unmount the sd card when is extracted.

## INPUT

### ADC

^ON BOARD ADCS:

#### adc_config  

to config analog pin to read from (see pinout, -po and -att)

#### aread  

to read from an analog pin previously configurated
^EXTERNAL ADC: (I2C) ADS1115 ***

#### ads_init

to initialize and configurate ADS1115 (see -ads)

#### ads_read

to read from an analog pin previously configurated
(see -tm option for stream mode, and -f for logging*)

for one shot read, logging is also available with -f and
-n option (for tagging)

use '-f now' for automatic 'log_mode_datetime.txt' name.

### IMU

#### imu_init

initialize IMU, use -imu option to indicate the imu library.
(default option is 'lsm9ds1', see sensor requirements for more info')

#### imuacc  

one shot read of the IMU lineal accelerometer (g=-9.8m/s^2),
(see -tm option for stream mode, and -f for logging*)

* for one shot read, logging is also available with -f and
    -n option (for tagging)
* use '-f now' for automatic 'log_mode_datetime.txt' name.
** stream mode and logging are supported in imugy and imumag also
#### imuacc_sd

log the imuacc data to the sd (must be mounted)
with the file format 'log_mode_datetime.txt'
(see -tm option for stream mode)

#### imugy  

one shot read of the IMU gyroscope (deg/s)

#### imumag

one shot read of the IMU magnetometer (gauss)

### POWER

(INA219)

## OUTPUT

###     DAC

#### dac_config

to config analog pin to write to (use -po option)

#### dac_write

to write a value in volts (0-3.3V)

#### dac_sig

to write a signal use -sig for different options:
ype] [Amp] [frequency]
(type: 'sin, sq'; Amp 0-1 V ; fq:0-50 (above that fq loses quality))

> start : starts signal generation
> stop : stops signal
> mod [Amp] [frequency]: modify the signal with the Amp and fq indicated.

### BUZZER:

#### buzz_config

to config PWM pin to drive the buzzer (use -po option)

#### buzz_set_alarm

to set an alarm at time indicated with option -at, be
    aware that the rtc time must be set first with set_localtime
    or set_ntptime

#### buzz_interrupt

to configure an interrupt with pins indicated with -po

#### buzz_beep

make the buzzer beep, with options set by -opt,
    usage: buzz_beep -opt [beep_ms] [number_of_beeps] [time_between_beeps] [fq]

### DC MOTOR

#### dcmotor_config

to config PWM pins to drive a DC motor (use -po option as -po [DIR1] [DIR2])

#### dcmotor_move

to move the motor to one direction ['R'] or the opposite ['L']
    use -to option as -to ['R' or 'L'] [VELOCITY] (60-512)

#### dcmotor_stop

to stop the DC motor

### SERVO:

#### servo_config

to configurate the servo pin with -po option

#### servo_angle

to move the servo an angle indicated by

### STEPPER MOTOR:

#### stepper_config

to configurate the servo pin with -po option

#### stepper_move

to move the stepper to right or left, at a velocity and
    a numbers of steps indicated with -to option: [R or L] [velocity] [# steps]
    R: right, L:left, velocity (1000-20000) (smaller is faster) and steps (int), where 200 steps means a complete lap

## NETWORKING:

### MQTT:

#### mqtt_config

to set id, broker address, user and password, use with -client option
    as "mqtt_config -client [ID] [BROKER ADDRESS] [USER] [PASSWORD]"

#### mqtt_conn

to start a mqtt client and connect to broker; use mqtt_config first

#### mqtt_sub

to subscribe to a topic, use -to option as "mqtt_sub -to [TOPIC]"

#### mqtt_pub

to publish to a topic, use -to option as "mqtt_pub -to [TOPIC] [PAYLOAD]" or
    "mqtt_pub -to [PAYLOAD]" if already subscribed to a topic.

#### mqtt_check

to check for new messages of the subscribed topics.

### SOCKETS:

#### socli_init

to initiate a socket client use with -server option as
    "socli_init -server [IP] [PORT] [BUFFER LENGTH]"

#### socli_conn

to connect the socket client to a server (inidcated by IP)

#### socli_send

to send a message to the server, use -n option to indicate
    the message

#### socli_recv

to receive a message from the server

#### sosrv_init

to initiate a socket server, use with -server option as
    "sosrv_init -server [PORT] [BUFFER LENGTH]"

#### sosrv_start

to start the server, waits for a connection

#### sosrv_send

to send a message to the client, use -n option to indicate
    the message

#### sosrv_recv

to receive a message from the client

### UREQUEST:

#### rget_json

to make a request to API that returns a JSON response format
    (indicate API URL with -f option)

#### rget_text

to make a request to API that returns a text response format
    (indicate API URL with -f option)

## Port/board specific commands:

### battery

if running on battery, gets battery voltage (esp32 huzzah feather)

### pinout

to see the pinout reference/info of a board, indicated by -b option,
to request a single or a list of pins info use -po option

### specs

to see the board specs, indicated by -b option

#### pin_status

to see pin state, to request a specific set use -po option ***

### ESP32:

#### touch

#### hall

#### deepsleep

#### temp
