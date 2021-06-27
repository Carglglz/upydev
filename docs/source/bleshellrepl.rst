BLE
====================

A Terminal SHELL-REPL over Bluetooth Low Energy


To configure a ble device see

:ref:`gettingstarted:Create a configuration file`

To access BLE SHELL-REPL

.. code-block:: console

    $ upydev ble # shl works too


To configure a ble device in the global group 'UPY_G' see

:ref:`gettingstarted:Create a GROUP file`


Then the device can be accessed with:

.. code-block:: console

    $ upydev ble -@ ble_device # shl works too

or

.. code-block:: console

    $ upydev shl@ble_device

Example: For a *esp32* saved as ``bledev``

.. code-block:: console

    $ upydev shl@bledev
    BLE SHELL-REPL @ bledev
    BLE SHELL-REPL connected

    MicroPython v1.16 on 2021-06-24; ESP32 module with ESP32
    Type "help()" for more information.

    Use CTRL-x to exit, Use CTRL-s to toggle shell/repl mode
    Use CTRL-k to see more info
    esp32@bledev:~ $ df
    Filesystem      Size        Used       Avail        Use%     Mounted on
    Flash          2.0 MB      1.6 MB     400.0 KB    80.2 %     /
    esp32@bledev:~ $ meminfo
    Memory          Size        Used       Avail        Use%
    RAM          108.562 KB  93.516 KB   15.047 KB    86.1 %
    esp32@bledev:~ $ tree test_sync_dir
    test_sync_dir
    ├── ATEXTFILE.txt
    ├── THETESTCODE.py
    ├── ble_test_file.txt
    ├── dummy_time.py
    ├── logACC_6_7_2019_0_28_43.txt
    ├── my_other_dir_sync
    │   └── another_file.txt
    ├── new_tree_test_dir
    │   ├── example_code.py
    │   ├── foo_file.txt
    │   ├── sub_foo_test_dir
    │   │   ├── file_code.py
    │   │   └── foo2.txt
    │   ├── w_name_dir
    │   │   └── dummy_file.txt
    │   └── zfile.py
    └── test_subdir_sync
          ├── SUBTEXT.txt
          └── sub_sub_dir_test_sync
              ├── level_2_subtext.txt
              ├── level_3_subtext.txt
              └── ultimate_file.py

    6 directories, 16 files
    esp32@bledev:~ $



BLE : SHELL-REPL
--------------------

The BLE SHELL-REPL allows to toggle between SHELL and REPL mode (Use *CTRL-s* to do this)

The REPL mode has two limitations:

- It is not listening actively for output (This means that if a timer/hardware interrupt callback print something it will not appear in the repl). To active listening for this kind of output do *CTRL-g*, to stop actively listening do *CTRL-c*

- To define a function/class or make a loop use the paste mode. (CTRL-E)


.. note::

    To see keybindings / shell commands info do **CTRL-k**: This will print the following info

.. code-block:: console

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
    - CRTL-s  : toggle shell mode to navigate filesystem (see shell commands)
    - CTRL-k : prints the custom keybindings (this list) (+ shell commands if in shell mode)

    Autocompletion commands:

    - tab to autocomplete device file / dirs names / raw micropython (repl commands)
    - shift-tab to autocomplete shell commands
    - shift-right to autocomplete local file / dirs names
    - shift-left  to toggle local path in prompt

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
      - ls  : list device files in colored format (same as pressing tab on empty line)(allows "\*" wildcard or directories)
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
      - apconfig: to see access POINT (AP) interface configuration (IP, SUBNET, GATEAWAY, DNS)
      - apconfig_t: to see access POINT (AP) interface configuration in table format
            (SSID, BSSID, CHANNEL, AUTH, IP, SUBNET, GATEAWAY, DNS)
      - install: to install a library into the device with upip.
      - touch  : to create a new file (e.g. touch test.txt)
      - edit   : to edit a file (e.g. edit my_script.py)
      - get    : to get a file from the device (also allows "\*" wildcard, 'cwd' or multiple files)
      - put    : to upload a file to the device (also allows "\*" wildcard, 'cwd' or multiple files)
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
