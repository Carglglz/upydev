# SERIAL SHELL-REPL

To use this mode connect the device by USB to the computer and use one of the following commands:

If the device is not previously configured do:

`$ upydev sh_srepl -port [serial port] -b [baudrate]` (-b default is 115200)

To configurate a serial device use in current working directory:

`$ upydev config -t [baudrate] -p [serial port]` 

Then 

`$ upydev sh_srepl` to access the device

To configurate a serial device in the global group 'UPY_G':

If the group does not exists already:

`$ upydev make_group -g -f UPY_G -devs foo_device [baudrate] [serial port]`

e.g `$ upydev make_group -g -f UPY_G -devs foo_device 115200 /dev/tty.usbmodem3370377430372`

If there is already a global 'UPY_G' group:

`$ upydev mg_group -G UPY_G -add foo_device 115200 /dev/tty.usbmodem3370377430372`

Then the device can be accessed with:

`$ upydev sh_srepl -@ foo_device`

or

`$ upydev shr@foo_device`

Example: For a pyboard1.1 saved as *pybV1.1*

```bash
$ upydev shr@pybV1.1
SERIAL SHELL-REPL connected

MicroPython v1.12-87-g96716b46e on 2020-01-26; PYBv1.1 with STM32F405RG
Type "help()" for more information.

Use CTRL-x to exit, Use CTRL-s,ENTER to toggle shell/repl mode
Use CTRL-k to see more info
pyboard@pybV1.1:~ $ whoami
DEVICE: pybV1.1, SERIAL PORT: /dev/tty.usbmodem3370377430372 , BAUDRATE: 9600,  ID: 3c003d000247373038373333
SYSTEM NAME: pyboard
NODE NAME: pyboard
RELEASE: 1.12.0
VERSION: v1.12-87-g96716b46e on 2020-01-26
MACHINE: PYBv1.1 with STM32F405RG
pyboard@pybV1.1:~ $ tree
  DIR_TEST <dir>
        └────  example_code.py
  README.txt
  boot.py
  lib <dir>
        ├────  ffilib.py
        ├────  pystone_lowmem.py
        ├────  sqlite3.py
        ├────  time_it.py
        ├────  uasyncio <dir>
        │    ├────  __init__.py
        │    └────  core.py
        ├────  uping.py
        ├────  upylog.py
        ├────  upynotify.py
        ├────  upysh.py
        └────  upysh2.py
  lsm9ds1.py
  main.py
  main_test.py
  new_dir <dir>
        └────  udummy.py
  pybcdc.inf
  servo_serial.py
  test_code.py
  test_file.txt
  udummy.py
4 directories, 23 files
pyboard@pybV1.1:~ $ df
Filesystem      Size        Used       Avail        Use%     Mounted on
Flash         95.0 KB     86.0 KB      9.0 KB     90.5 %     /
pyboard@pybV1.1:~ $ meminfo
Memmory         Size        Used       Avail        Use%
RAM          100.938 KB  10.828 KB   90.109 KB    10.7 %
pyboard@pybV1.1:~ $
```



### SERIAL : shell/repl

The SERIAL SHELL-REPL allows to toggle between shell and repl modes (Use 'CTRL-s' and then press 'ENTER' to do this)

The repl mode has two limitations:

- It is not listening actively for output (This means that if a timer/hardware interrupt callback print something it will not appear in the repl). To active listening for this kind of output do CTRL-g, to stop actively listening do CTRL-c

- To define a function/class or make a loop use the paste mode. (CTRL-E)

  *However the original Serial REPL can be accesed from shell with 'srepl' command* (This needs Picocom)

  e.g.

  ```
  pyboard@pybV1.1:~ $ srepl
  <-- Device pyboard MicroPython -->
  Use CTRL-a,CTRL-x to exit
  picocom v3.1
  
  port is        : /dev/tty.usbmodem3370377430372
  flowcontrol    : none
  baudrate is    : 115200
  parity is      : none
  databits are   : 8
  stopbits are   : 1
  escape is      : C-a
  local echo is  : no
  noinit is      : no
  noreset is     : no
  hangup is      : no
  nolock is      : no
  send_cmd is    : sz -vv
  receive_cmd is : rz -vv -E
  imap is        :
  omap is        :
  emap is        : crcrlf,delbs,
  logfile is     : none
  initstring     : none
  exit_after is  : not set
  exit is        : no
  
  Type [C-a] [C-h] to see available commands
  Terminal ready
  
  >>>
  ```

  

**To see keybindings / shell commands info do 'CTRL-k': This will print**:

Custom keybindings:

- CTRL-x : to exit SHELL-REPL Terminal
- CTRL-p : toggle RAM status right aligned message (USED/FREE)
- CTRL-e : paste mode in repl,(in shell mode set cursor position at the end)/ (edit mode after 'edit' shell command)
- CTRL-d : ends paste mode in repl, (ends edit mode after 'edit' shell command)
          (or soft-reset in repl, CTRL-C to start repl again)
- CTRL-c : KeyboardInterrupt, in normal mode, cancel in paste or edit mode
- CTRL-b : prints MicroPython version and sys platform
- CTRL-r : to flush line buffer
- CTRL-o : to list files in cwd (sz shorcut command)
- CTRL-n : shows mem_info()
- CTRL-y : gc.collect() shortcut command
- CTRL-space : repeats last command
- CTRL-t : runs test_code.py if present
- CTRL-w : flush test_code from sys modules, so it can be run again
- CTRL-a : set cursor position at the beggining
- CTRL-f : toggle autosuggest mode (Fish shell like)(use right arrow to complete)
- CTRL-g : To active listen for device output (Timer or hardware interrupts), CTRL-c to break
- CRTL-s , ENTER : toggle shell mode to navigate filesystem (see shell commands)
- CTRL-k : prints the custom keybindings (this list) (+ shell commands if in shell mode)

Autocompletion commands:

- tab to autocomplete device file / dirs names / raw micropython (repl commands)
- shift-tab to autocomplete shell commands
- shift-right to autocomplete local file / dirs names
- shift-left,ENTER to toggle local path in prompt

Device shell commands:

* upysh commands:
  - sz   : list files and size in bytes
  - head : print the head of a file
  - cat  : prints the content of a file
  - mkdir: make directory
  - cd   : change directory (cd .. to go back one level)
  - pwd  : print working directory
  - rm   : to remove a file
  - rmdir: to remove a directory

* custom shell commands:
  - ls  : list device files in colored format (same as pressing tab on empty line)(allows "*" wildcard or directories)
  - tree : to print a tree version of filesystem (to see also hidden files/dirs use 'tree -a')
  - run  : to run a 'script.py'
  - df   : to see filesystem flash usage (and SD if already mounted)
  - du   : display disk usage statistics (usage: "du", "du [dir or file]" + '-d' deep level option)
  - meminfo: to see RAM info
  - dump_mem: to do a memory dump
  - whoami : to see user, system and machine info
  - datetime: to see device datetime (if not set, will display uptime)
  - set_localtime : to set the device datetime from the local machine time
  - ifconfig: to see STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
  - ifconfig_t: to see STATION interface configuration in table format
        (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
  - netscan: to scan WLANs available, (ESSID, MAC ADDRESS, CHANNEL, RSSI, AUTH MODE, HIDDEN)
  - uping : to make the device send ICMP ECHO_REQUEST packets to network hosts (do 'uping host' to ping local machine)
  - apconfig: to see ACCESS POINT (AP) interface configuration (IP, SUBNET, GATEAWAY, DNS)
  - apconfig_t: to see ACCESS POINT (AP) interface configuration in table format
        (SSID, BSSID, CHANNEL, AUTH, IP, SUBNET, GATEAWAY, DNS)
  - install: to install a library into the device with upip.
  - touch  : to create a new file (e.g. touch test.txt)
  - edit   : to edit a file (e.g. edit my_script.py)
  - get    : to get a file from the device (also allows "*" wildcard, 'cwd' or multiple files)
  - put    : to upload a file to the device (also allows "*" wildcard, 'cwd' or multiple files)
  - sync   : to get file (faster) from the device (use with > 10 KB files) (no encrypted mode only)
  - d_sync: to recursively sync a local directory with the device filesystem
  - srepl  : to enter the Serial Terminal (This needs Picocom)
  - reload : to delete a module from sys.path so it can be imported again.
  - flush_soc: to flush serial in case of wrong output
  - view   : to preview '.pbm' binary image files (image need to be centered and rows = columns) 
  - bat    : prints the content of a '.py' file with Python syntax hightlighting (named after https://github.com/sharkdp/bat)
  - rcat   : prints the raw content of a file (encryption mode only)
  - timeit : to measure execution time of a script/command
  - i2c    : config/scan (config must be used first, i2c config -scl [SCL] -sda [SDA]
  - upy-config: interactive dialog to configure Network (connect to a WLAN or set an AP) or Interafaces (I2C)
  - jupyterc: to run MicroPython upydevice kernel for jupyter console
  - exit   : to exit SSLWebREPL Terminal (in encrypted mode soft-reset by default)
        to exit without reset do 'exit -nr'
        to exit and do hard reset 'exit -hr'
* Local shell commands:
  - pwdl   : to see local path
  - cdl    : to change local directory
  - lsl    : to list local directory
  - catl   : to print the contents of a local file
  - batl   : prints the content of a local '.py' file with Python syntax hightlighting
  - l_micropython: if "micropython" local machine version available in $PATH, runs it.
  - python : switch to local python3 repl
  - vim    : to edit a local file with vim  (e.g. vim script.py)
  - emacs  : to edit a local file with emacs (e.g. emacs script.py)
  - l_ifconfig: to see local machine STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
  - l_ifconfig_t: to see local machine STATION interface configuration in table format
        (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
  - docs : to open MicroPython docs site in the default web browser, if a second term
        is passed e.g. 'docs machine' it will open the docs site and search for 'machine'
  - get_rawbuff: to get the raw output of a command (for debugging purpose)
  - fw   : + list/get/update/latest firmware e.g (fw list latest, fw get latest) (use option -n [expresion to match])
        e.g. (fw get latest -n spiram, or fw get esp32-idf3-20200114-v1.12-63-g1c849d63a.bin, or fw update -n pybv11)
  - flash : to flash a firmware file, e.g 'flash esp32-idf3-20200114-v1.12-63-g1c849d63a.bin'
  - ldu  : display local path disk usage statistics (usage: "du", "du [dir or file]" + '-d' deep level option)
  - upipl : (usage 'upipl' or 'upipl [module]' display available micropython packages that can be installed with install command
  - pkg_info: to see the PGK-INFO file of a module if available at pypi.org or micropython.org/pi
  - lping : to make local machine send ICMP ECHO_REQUEST packets to network hosts (do 'lping dev' to ping the device)
  - update_upyutils: to install 'upydev update_upyutils' scripts in the device
  - git : to call git commands and integrate the git workflow into a project (needs 'git' available in $PATH)
    - Use 'git init dev' to initiate device repo
    - Use 'git push dev' after a 'git commit ..' or 'git pull' to push the changes to the device.
    - Use 'git log dev' to see the latest commit pushed to the device ('git log dev -a' to see all commits)
    - Use 'git log host' to see the latest commit in the local repo
    - Use 'git status dev' to see if the local repo is ahead of the device repo and track these changes
    - Use 'git clone_dev' to clone the local repo into the device
    - Use 'git repo' to open the remote repo in the web browser if remote repo exists
    - Any other git command will be echoed directly to git
  - tig: to use the 'Text mode interface for git' tool. Must be available in $PATH

Some examples of these commands:

```bash
pyboard@pybV1.1:~ $ df
Filesystem      Size        Used       Avail        Use%     Mounted on
Flash         95.0 KB     86.0 KB      9.0 KB     90.5 %     /
pyboard@pybV1.1:~ $ cd lib
pyboard@pybV1.1:~/flash/lib$ ls
ffilib.py                   pystone_lowmem.py           sqlite3.py                  time_it.py                  uasyncio                    uping.py
upylog.py                   upynotify.py                upysh.py                    upysh2.py
pyboard@pybV1.1:~/flash/lib$ meminfo
Memmory         Size        Used       Avail        Use%
RAM          100.938 KB   7.922 KB   93.016 KB     7.8 %
pyboard@pybV1.1:~/flash/lib$ cd ..
pyboard@pybV1.1:~/flash$ du lib
1.5 KB    ./lib/upysh.py
4.8 KB    ./lib/upysh2.py
7.7 KB    ./lib/pystone_lowmem.py
4.0 KB    ./lib/sqlite3.py
523 by    ./lib/time_it.py
17.5 KB   ./lib/uasyncio <dir>
8.1 KB    ./lib/uping.py
1006 by   ./lib/ffilib.py
4.9 KB    ./lib/upylog.py
2.7 KB    ./lib/upynotify.py
pyboard@pybV1.1:~/flash$ run udummy.py
hello dummy!
bye bye! hello again
This line is edited
This line is edited via serial
Another edited line
bye bye! hello again
This line is edited
This line is edited via serial
Another edited line
bye bye! hello again
This line is edited
This line is edited via serial
Another edited line
bye bye! hello again
This line is edited
This line is edited via serial
^CTraceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "udummy.py", line 13, in <module>
KeyboardInterrupt:
>>>
>>>
pyboard@pybV1.1:~/flash$ reload udummy.py
pyboard@pybV1.1:~/flash$ exit
Rebooting device...
Done!
logout
Connection to /dev/tty.usbmodem3370377430372 closed.
```

