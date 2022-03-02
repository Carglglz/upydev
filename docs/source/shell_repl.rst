shell-repl
------------------------

The shell-repl Mode allows to toggle between SHELL and REPL modes (Use *CTRL-s* to do this)

The REPL mode has two limitations:

- It is not listening actively for output (This means that if a timer/hardware interrupt callback print something it will not appear in the repl).

- To define a function/class or make a loop use the paste mode. (*CTRL-E*)

  *However the original WebREPL Terminal can be accessed from shell with* ``repl`` *command*

  e.g.

.. code-block:: console

    esp32@esp_room1:~ $ repl
    <-- Device esp_room1 MicroPython -->
    Use CTRL-x to exit, Use CTRL-k to see custom wrepl Keybdings
    Password:
    WebREPL connected
    >>>
    MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
    Type "help()" for more information.
    >>>
    >>>

.. note::
    To see help use ``-h``

.. code-block:: console

  esp32@esp_room1:~ $ -h
  usage: command [options]

  This means that if the first argument [command] is not a registered
  command it is redirected to the underlying system shell. To redirect a command
  to the system shell use %command

  Shell for MicroPython devices

  Do CTRL-k to see keybindings info
  [command] -h to see further help of any command

  optional arguments:
  -h, --help            show this help message and exit
  -v                    show program's version number and exit

  commands:
  ** use enable_sh to upload required files for filesystem cmds

  {ls,head,cat,mkdir,touch,cd,pwd,rm,rmdir,du,tree,df,mem,exit,vim,run,reload,info,id,uhelp,modules,uping,rssi,net,ifconfig,ap,i2c,set,datetime,shasum,upip,timeit,update_upyutils,lcd,lsl,lpwd,ldu,docs,mdocs,ctime,enable_sh,diff,config,sd,repl,getcert,jupyterc,pytest,put,get,dsync,debugws,fw,mpyx,ota,upy-config,install}
  ls                  list files or directories
  head                display first lines of a file
  cat                 concatenate and print files
  mkdir               make directories
  touch               create a new file
  cd                  change current working directory
  pwd                 print current working directory
  rm                  remove file or pattern of files
  rmdir               remove directories or pattern of directories
  du                  display disk usage statistics
  tree                list contents of directories in a tree-like format
  df                  display free disk space
  mem                 show ram usage info
  exit                exit upydev shell
  vim                 use vim to edit files
  run                 run device's scripts
  reload              reload device's scripts
  info                prints device's info
  id                  prints device's unique id
  uhelp               prints device's help info
  modules             prints device's frozen modules
  uping               device send ICMP ECHO_REQUEST packets to network hosts
  rssi                prints device's RSSI (WiFi or BLE)
  net                 manage network station interface (STA._IF)
  ifconfig            prints network interface configuration (STA._IF)
  ap                  manage network acces point interface (AP._IF)
  i2c                 manage I2C interface
  set                 set device's configuration {rtc, hostname, localname}
  datetime            prints device's RTC time
  shasum              shasum SHA-256 tool
  upip                install or manage MicroPython libs
  timeit              measure execution time of a script/function
  update_upyutils     update upyutils scripts
  lcd                 change local current working directory
  lsl                 list local files or directories
  lpwd                print local current working directory
  ldu                 display local disk usage statistics
  docs                see upydev docs at https://upydev.readthedocs.io/en/latest/
  mdocs               see MicroPython docs at docs.micropython.org
  ctime               measure execution time of a shell command
  enable_sh           upload required files so shell is fully operational
  diff                use git diff between device's [~file/s] and local file/s
  config              set or check config (from *_config.py files*)#
  sd                  commands to manage an sd
  repl                enter WebREPL
  getcert             get device's certificate if available
  jupyterc            enter jupyter console with upydevice kernel
  pytest              run tests on device with pytest (use pytest setup first)
  put                 upload files to device
  get                 download files from device
  dsync               recursively sync a folder from/to device's filesystem
  debugws             toggle debug mode for websocket debugging
  fw                  list or get available firmware from micropython.org
  mpyx                freeze .py files using mpy-cross. (must be available in $PATH)
  ota                 to flash a firmware file using OTA system
  upy-config          enter upy-config dialog
  install             install libraries or modules with upip to ./lib


.. note::
    To see keybindings info do **CTRL-k**: This will print the following info

.. code-block:: console

  * Autocompletion keybindings:
   - tab to autocomplete device file / dirs names / raw micropython (repl commands)
   - shift-tab to autocomplete shell commands
   - shift-right to autocomplete local file / dirs names
   - shift-left to toggle local path in prompt
  * CTRL - keybindings:
  - CTRL-x : to exit shell/repl
  - CTRL-p : toggle RAM STATUS right aligned message (USED/FREE)
  - CTRL-e : paste vim mode in repl
  - CTRL-d : ends vim paste mode in repl and execute buffer
  - CTRL-c : KeyboardInterrupt, in normal mode, cancel in paste mode
  - CTRL-b : prints MicroPython version and sys platform
  - CTRL-r : to flush line buffer
  - CTRL-n : shows mem_info()
  - CTRL-y : gc.collect() shortcut command
  - CTRL-space : repeats last command
  - CTRL-o, Enter : to enter upy-config dialog
  - CTRL-t : runs temp buffer ('_tmp_script.py' in cwd)
  - CTRL-w : prints device info
  - CTRL-a : set cursor position at the beggining
  - CTRL-j : set cursor position at the end of line
  - CTRL-f : toggle autosuggest mode (Fish shell like)(use right arrow to complete)
  - CRTL-s : toggle shell mode to navigate filesystem (see shell commands)
  - CTRL-k : prints the custom keybindings (this list)

Some examples of these commands:

.. code-block:: console

    esp32@esp_room1:~ $ df
    Filesystem      Size        Used       Avail        Use%     Mounted on
    Flash          2.0 MB     636.0 KB     1.4 MB     31.4 %     /
    esp32@esp_room1:~ $ cd lib
    esp32@esp_room1:~/lib$ ls
    client.py                   logging.py
    protocol.py                 ssl_repl.py
    sync_tool.py                upylog.py
    upynotify.py                upysecrets.py
    upysh2.py
    esp32@esp_room1:~/lib$ mem
    Memory         Size        Used       Avail        Use%
    RAM          116.188 KB  17.984 KB   98.203 KB    15.5 %
    esp32@esp_room1:~/lib$ cd
    esp32@esp_room1:~ $ cd test_sync_dir
    esp32@esp_room1:~/test_sync_dir$ tree
    .
    ├── dirA
    │   ├── dirB
    │   │   └── file3.py
    │   └── file2.py
    ├── THETESTCODE.py
    ├── file1b.py
    └── othe_dir

    3 directories, 4 files

    esp32@esp_room1:~/test_sync_dir$ cat THETESTCODE.py
    # This is a MicroPython script
    # define a function in edit mode now
    def my_test_func():
        print('This is a function defined in edit mode with tab indentation')
    for i in range(10):
        my_test_func()
    for i in range(5):
        print('test finish')
    esp32@esp_room1:~/test_sync_dir$ run THETESTCODE.py
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    This is a function defined in edit mode with tab indentation
    test finish
    test finish
    test finish
    test finish
    test finish
    esp32@esp_room1:~/test_sync_dir$ exit -r
    Rebooting device...
    Done!
    logout
    Connection to esp_room1 closed.
