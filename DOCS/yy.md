[uPydev Mode/Tools:](#header-n159)  
	[config ](#header-n4)  
	[put ](#header-n6)  
	[get ](#header-n8)  
	[sync ](#header-n168)  
	[cmd ](#header-n173)  
	[wrepl ](#header-n17)  
	[ping ](#header-n182)  
	[run ](#header-n21)  
	[install ](#header-n196)  
	[mpyx ](#header-n28)  
	[timeit ](#header-n204)  
[upy Commands:](#header-n31)  
	[GENERAL](#header-n210)  
		[info ](#header-n34)  
		[id ](#header-n213)  
		[upysh](#header-n217)  
		[reset](#header-n40)  
		[uhelp ](#header-n42)  
		[umodules](#header-n226)  
		[mem\_info ](#header-n46)  
		[filesize ](#header-n48)  
		[filesys\_info ](#header-n50)  
		[netinfo ](#header-n239)  
		[netinfot ](#header-n54)  
		[netscan ](#header-n56)  
		[netstat\_on ](#header-n58)  
		[netstat\_off ](#header-n60)  
		[netstat\_conn ](#header-n62)  
		[netstat ](#header-n256)  
		[ap\_on ](#header-n66)  
		[ap\_off ](#header-n68)  
		[apstat ](#header-n70)  
		[apconfig ](#header-n72)  
		[apscan ](#header-n74)  
		[i2c\_config ](#header-n76)  
		[i2c\_scan ](#header-n78)  
		[spi\_config](#header-n80)  
		[set\_localtime](#header-n277)  
		[set\_ntptime](#header-n84)  
		[get\_datetime](#header-n283)  
	[SD](#header-n87)  
		[sd\_enable](#header-n90)  
		[sd\_init](#header-n92)  
		[sd\_deinit](#header-n94)  
		[sd\_auto ](#header-n96)  
	[INPUT](#header-n295)  
		[ADC](#header-n99)  
			[adc\_config ](#header-n102)  
			[aread ](#header-n104)  
			[ads\_init ](#header-n106)  
			[ads\_read ](#header-n108)  
		[IMU](#header-n115)  
			[imu\_init ](#header-n118)  
			[imuacc ](#header-n120)  
			[imuacc\_sd](#header-n128)  
			[imugy ](#header-n130)  
			[imumag ](#header-n132)  
		[POWER](#header-n134)  
	[OUTPUT](#header-n135)  
		[ DAC](#header-n328)  
			[dac\_confi](#header-n331)  
			[dac\_write](#header-n338)  
			[dac\_sig](#header-n340)  
		[BUZZER:](#header-n345)  
			[buzz\_config](#header-n348)  
			[buzz*set*alarm](#header-n389)  
			[buzz\_interrupt](#header-n352)  
			[buzz\_beep](#header-n354)  
		[DC MOTOR](#header-n356)  
			[dcmotor\_config](#header-n359)  
			[dcmotor\_move](#header-n361)  
			[dcmotor\_stop](#header-n404)  
		[SERVO:](#header-n365)  
			[servo\_config](#header-n368)  
			[servo\_angle](#header-n411)  
			[STEPPER MOTOR:](#header-n415)  
			[stepper\_config](#header-n375)  
			[stepper\_move](#header-n377)

uPydev Mode/Tools: {#header-n159}
==================

config  {#header-n4}
-------

 to save upy device settings (see -p, -t, -g),

so the target and password arguments wont be required any more

put  {#header-n6}
----

to upload a file to upy device (see -f, -s and -rst)

get  {#header-n8}
----

to download a file from upy device (see -f and -s)

sync  {#header-n168}
-----

for a faster transfer of large files (this needs sync\_tool.py in upy
device) (see -f, -s and -lh)

cmd  {#header-n173}
----

to send command to upy device ; (see -c, -r, -rl); example: upydev cmd
-c "led.on()" ; upydev cmd -r "print('Hello uPy')"; upydev cmd -rl
"function*that*print*multiple*lines()";

-   tip: simple commands can be used without quotes; but for commands
    with parenthesis or special characters use quoutes, for example:
    'dummy\_func()' ; use double quotes "" when the command includes a
    string like this example: "uos.listdir('/sd')"

wrepl  {#header-n17}
------

to enter the terminal webrepl; write 'exit' or press CTRL-C to exit
(see: https://github.com/Hermann-SW/webrepl for more information)

ping  {#header-n182}
-----

pings the target to see if it is reachable, CTRL-C to stop \\n

run  {#header-n21}
----

just calls import 'script', where 'script' is indicated by -f option
(script must be in upydevice or in sd card indicated by -s option and
the sd card must be already mounted as 'sd');

Supports CTRL-C to stop the execution and exits nicely.

install  {#header-n196}
--------

install libs to '/lib' path with upip; indicate lib with -f option

mpyx  {#header-n28}
-----

to froze a module/script indicated with -f option, and save some RAM, it
uses mpy-cross tool (see https://gitlab.com/alelec/mpy\_cross)

timeit  {#header-n204}
-------

to measure execution time of a module/script indicated with -f option.
This is an implementation of
https://github.com/peterhinch/micropython-samples/tree/master/timed\_function

upy Commands: {#header-n31}
=============

GENERAL {#header-n210}
-------

### info  {#header-n34}

 for upy device system info

### id  {#header-n213}

for upy device unique id

### upysh {#header-n217}

to enable the upy shell in the upy device (then do 'upydev man' to acces
upysh manual info)

### reset {#header-n40}

to do a soft reset in upy device

### uhelp  {#header-n42}

just calls micropython help

### umodules {#header-n226}

just calls micropython help('modules')

### mem\_info  {#header-n46}

for upy device RAM memory info; call it once to check actual memory,
call it twice and it will free some memory

### filesize  {#header-n48}

 to get the size of file in root dir (default) or sd with '-s sd'
option; if no file name indicated with -f option, prints all files

### filesys\_info  {#header-n50}

to get memory info of the file system, (total capacity, free, used),
(default root dir, -s option to change)

### netinfo  {#header-n239}

for upy device network info if station is enabled and connected to an AP

### netinfot  {#header-n54}

same as netinfo but in table format

### netscan  {#header-n56}

for upy device network scan

### netstat\_on  {#header-n58}

for enable STA

### netstat\_off  {#header-n60}

for disable STA

### netstat\_conn  {#header-n62}

for connect to an AP , must provide essid and password (see -wp)

### netstat  {#header-n256}

STA state ; returns True if enabled, False if disabled

### ap\_on  {#header-n66}

for enable AP

### ap\_off  {#header-n68}

for disable AP

### apstat  {#header-n70}

 AP state ; returns True if enabled, False if disabled

### apconfig  {#header-n72}

AP configuration of essid and password with authmode WPA/WPA2/PSK, (see
-ap), needs first that the AP is enabled (do 'upydev ap\_on')

### apscan  {#header-n74}

scan devices connected to AP; returns number of devices and mac address

### i2c\_config  {#header-n76}

to configurate the i2c pins (see -i2c, defaults are SCL=22, SDA=23)

### i2c\_scan  {#header-n78}

to scan i2c devices (must config i2c pins first)

### spi\_config {#header-n80}

to configurate the spi pins (see -spi, defaults are
SCK=5,MISO=19,MOSI=18,CS=21)

### set\_localtime {#header-n277}

to pass host localtime and set upy device rtc

### set\_ntptime {#header-n84}

to set rtc from server, (see -utc for time zone)

### get\_datetime {#header-n283}

to get date and time (must be set first, see above commands)

SD {#header-n87}
--

### sd\_enable {#header-n90}

to enable/disable the LDO 3.3V regulator that powers the SD module use
-po option to indicate the Pin.

### sd\_init {#header-n92}

to initialize the sd card; (spi must be configurated first) create sd
object and mounts as a filesystem, needs sdcard.py from \[\]

### sd\_deinit {#header-n94}

to unmount sd card

### sd\_auto  {#header-n96}

experimental command, needs a sd module with sd detection pin and the
SD\_AM.py script (see more info in \[\]). Enable an Interrupt with the
sd detection pin, so it mounts the sd when is detected, and unmount the
sd card when is extracted.

INPUT {#header-n295}
-----

### ADC {#header-n99}

^ON BOARD ADCS:

#### adc\_config  {#header-n102}

to config analog pin to read from (see pinout, -po and -att)

#### aread  {#header-n104}

to read from an analog pin previously configurated ^EXTERNAL ADC: (I2C)
ADS1115 \*\*\*

#### ads\_init  {#header-n106}

to initialize and configurate ADS1115 (see -ads)

#### ads\_read  {#header-n108}

to read from an analog pin previously configurated (see -tm option for
stream mode, and -f for logging\*)

for one shot read, logging is also available with -f and -n option (for
tagging)

use '-f now' for automatic 'log*mode*datetime.txt' name.

### IMU {#header-n115}

#### imu\_init  {#header-n118}

initialize IMU, use -imu option to indicate the imu library. (default
option is 'lsm9ds1', see sensor requirements for more info')

#### imuacc  {#header-n120}

one shot read of the IMU lineal accelerometer (g=-9.8m/s^2), (see -tm
option for stream mode, and -f for logging\*)

-   for one shot read, logging is also available with -f and -n option
    (for tagging)

-   use '-f now' for automatic 'log*mode*datetime.txt' name. \*\* stream
    mode and logging are supported in imugy and imumag also

#### imuacc\_sd {#header-n128}

log the imuacc data to the sd (must be mounted) with the file format
'log*mode*datetime.txt' (see -tm option for stream mode)

#### imugy  {#header-n130}

one shot read of the IMU gyroscope (deg/s)

#### imumag  {#header-n132}

one shot read of the IMU magnetometer (gauss)

### POWER {#header-n134}

(INA219)

OUTPUT {#header-n135}
------

###  DAC {#header-n328}

#### dac\_confi {#header-n331}

to config analog pin to write to (use -po option)

#### dac\_write {#header-n338}

to write a value in volts (0-3.3V)

#### dac\_sig {#header-n340}

to write a signal use -sig for different options: ype\] \[Amp\]
\[frequency\] (type: 'sin, sq'; Amp 0-1 V ; fq:0-50 (above that fq loses
quality))

> start : starts signal generation stop : stops signal mod \[Amp\]
> \[frequency\]: modify the signal with the Amp and fq indicated.

### BUZZER: {#header-n345}

#### buzz\_config {#header-n348}

to config PWM pin to drive the buzzer (use -po option)

#### buzz*set*alarm {#header-n389}

to set an alarm at time indicated with option -at, be aware that the rtc
time must be set first with set*localtime or set*ntptime

#### buzz\_interrupt {#header-n352}

to configure an interrupt with pins indicated with -po

#### buzz\_beep {#header-n354}

make the buzzer beep, with options set by -opt, usage: buzz*beep -opt
\[beep*ms\] \[number*of*beeps\] \[time*between*beeps\] \[fq\]

### DC MOTOR {#header-n356}

#### dcmotor\_config {#header-n359}

to config PWM pins to drive a DC motor (use -po option as -po \[DIR1\]
\[DIR2\])

#### dcmotor\_move {#header-n361}

to move the motor to one direction \['R'\] or the opposite \['L'\] use
-to option as -to \['R' or 'L'\] \[VELOCITY\] (60-512)

#### dcmotor\_stop {#header-n404}

to stop the DC motor

### SERVO: {#header-n365}

#### servo\_config {#header-n368}

to configurate the servo pin with -po option

#### servo\_angle {#header-n411}

to move the servo an angle indicated by

#### STEPPER MOTOR: {#header-n415}

#### stepper\_config {#header-n375}

to configurate the servo pin with -po option

#### stepper\_move {#header-n377}

to move the stepper to right or left, at a velocity and a numbers of
steps indicated with -to option: \[R or L\] \[velocity\] \[\# steps\] R:
right, L:left, velocity (1000-20000) (smaller is faster) and steps
(int), where 200 steps means a complete lap

NETWORKING: \* MQTT: - mqtt*config: to set id, broker address, user and
password, use with -client option as "mqtt*config -client \[ID\]
\[BROKER ADDRESS\] \[USER\] \[PASSWORD\]" - mqtt*conn: to start a mqtt
client and connect to broker; use mqtt*config first - mqtt*sub: to
subscribe to a topic, use -to option as "mqtt*sub -to \[TOPIC\]" -
mqtt*pub: to publish to a topic, use -to option as "mqtt*pub -to
\[TOPIC\] \[PAYLOAD\]" or "mqtt*pub -to \[PAYLOAD\]" if already
subscribed to a topic. - mqtt*check: to check for new messages of the
subscribed topics. \* SOCKETS: - socli*init: to initiate a socket client
use with -server option as "socli*init -server \[IP\] \[PORT\] \[BUFFER
LENGTH\]" - socli*conn: to connect the socket client to a server
(inidcated by IP) - socli*send: to send a message to the server, use -n
option to indicate the message - socli*recv: to receive a message from
the server - sosrv*init: to initiate a socket server, use with -server
option as "sosrv*init -server \[PORT\] \[BUFFER LENGTH\]" - sosrv*start:
to start the server, waits for a connection - sosrv*send: to send a
message to the client, use -n option to indicate the message -
sosrv*recv: to receive a message from the client \* UREQUEST: -
rget*json: to make a request to API that returns a JSON response format
(indicate API URL with -f option) - rget*text: to make a request to API
that returns a text response format (indicate API URL with -f option)

Port/board specific commands:

-   battery : if running on battery, gets battery voltage (esp32 huzzah
    feather)

-   pinout : to see the pinout reference/info of a board, indicated by
    -b option, to request a single or a list of pins info use -po option

-   specs : to see the board specs, indicated by -b option

-   pin\_status: to see pin state, to request a specific set use -po
    option \*\*\*

-   ESP32:

    -   touch

    -   hall

    -   deepsleep

    -   temp


