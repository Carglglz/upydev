# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.4] Unreleased [Github Repo]
### Fix
- Fix autocomplete on tab in REPL while `import` or `from X import` in SERIAL REPL
### Added
- Autocomplete `shr@` , `ssl@` and `wssl@` commands with saved devices in UPY_G global group
- `pytest` command in SHELL-REPLS
- `pytest` command mode in CLI.
## [0.3.3] - 2020-06-07
### Fix
- Fix `git status dev` aware of current branch
- Fix `d_sync`, in SHELL-REPLS, support root directory `.` will sync local cwd into device cwd
- Fix `put` for pyboard in SERIAL SHELL-REPL mode
- Fix `fw` for downloading and flashing firmware to pyboard, esp in SERIAL SHELL-REPL mode, now asserts serial port is available after flashing.
- Fix `battery` error if command fails.
## [0.3.2] - 2020-05-27
### Fix
- Fix `set_localtime` for pyboard in SERIAL SHELL-REPL mode
- Fix [issue \#8](https://github.com/Carglglz/upydev/issues/8)
- Fix `d_sync` now supports sync of cwd, use `d_sync` without -dir flag to synchronize current working directory
- Fix error messages in SSLWebREPL
- Fix, now to toggle between shell and REPL modes, there is no need to press ENTER
- Fix, toggle local path in prompt without pressing ENTER
- Fix, `apscan` mode now show MAC address instead of bytes
### Added
- Watch mode with `-wdl` flag for `put -fre` and `d_sync` modes. Uploads only new or modified files
## [0.3.1] - 2020-04-23
### Fix
- Fix for host ip determination
## [0.3.0] - 2020-04-13
### Fix
- Minor fix for host ip determination (while ECDSA key is generated and for SSLWebREPL mode)
## [0.2.9] - 2020-02-24
### Added
- jupyter console integration through jupyter-micropython-upydevice
- 'jupyterc' command in upydev and in SHELLS
### Fix
- autocompletion for zsh
- git integration and 'git init dev' command for SHELLS
- sslgen_key command help
## [0.2.8] - 2020-02-16
### Added
- emacs in nw mode by default
- tig integration for git workflow: [tig](https://jonas.github.io/tig/)
### Fix
- in SERIAL SHELL-REPL 'fw update' command for esp8266
## [0.2.7] - 2020-02-08
### Added
- To be able to use this new commands update the SSL key and cert with 'upydev sslgen_key -tfkey' and do 'upydev update_upyutils'
- 'wss_repl.py' and 'wss_helper.py' to enable WebSecureREPL in the device
- 'wssl' command e.g. 'upydev wssl@esp_room1' or 'upydev wssl@192.168.1.42' for a E2E encryption Terminal (WebSecureREPL + SSL SHELL-REPL)
- 'wss on/off' command in SSL REPL to enable/disable WebSecureREPL
- 'set_wss' upydev command to switch WebREPL to WebSecureREPL and
'set_wss -wss' to switch back to WebREPL
- if WebSecureREPL enabled, upydev 'put' and 'get' commands support WebSecureREPL file transfer using '-wss' option e.g. 'upydev put -f foo.py -wss'
## [0.2.6] 2020-02-02
### Added
- 'bat' command output style configurable and line numbers (inspired by https://github.com/willmcgugan/rich)
- 'batstyle' command to configure 'bat' and 'batl' syntax highlight, 'batstyle -a' list all the themes available (from pygments), default is 'monokai'
- 'upy-config' command for shells, to configure network (connect to a WLAN or set an AP) and configure Interfaces (just I2C by now) through interactive dialogs
### Fix
- cat, bat in SSLWebREPL if last line does not end with new line ('\\n')
- ECDSA key (SECP256R1_SHA256 method to meet IETF recommendations)
- 'git status dev' now tracks all commits (inside or outside the shell)
## [0.2.5] 2020-01-26
### Fix
- put method in SERIAL SHELL for esp32/8266
## [0.2.4] - 2020-01-26
### Added
- 'timeit' command to measure execution time of a script/command (for SSL/SERIAL SHELLS)
- 'i2c' +'config/scan' to configure i2c and scan to find i2c devices (for SSL/SERIAL SHELLS)
- 'git' commands integration + 'git push dev', 'git log dev [-a]', 'git clone_dev' and 'git status dev' to integrate git workflow into a project (for SSL/SERIAL SHELLS) ('git' needs to be available in $PATH)
- 'emacs' to edit a file/script with emacs ('emacs' need to be available in $PATH)
### Fix
- Autocompletion in REPLS improved
- pyboard firmware improved (automatically enables DFU mode, jumper doesn't needed)
- Changed upydev 'sslgen_rsakey' to 'sslgen_key' key now is a ECDSA key (SECP384R1 method)
- Cipher suite is now TLSv1.2 @ ECDHE-ECDSA-AES128-CCM8 - 128 bits which is recommended for constrained devices / IOT (This requires a recent version of python-ssl)
- put method (faster) in SERIAL SHELL
## [0.2.3] - 2020-01-19
### Added
- fw , flash (and fw update which is 'fw get' + 'flash') commands for SERIAL SHELL
- 'du' command for disk usage statistics (unix like) (SSL/SERIAL SHELLS)
- 'd_sync' command to recursively sync directories for (SSL/SERIAL SHELLS)
- 'uping' and 'lping' commands for device and host pings commands (SSL/SERIAL SHELLS)
- wildcard "\*" or [dir] for 'ls' and 'lsl' command e.g. "ls \*.py" or "ls my_dir" (SSL/SERIAL SHELLS)
- install available for pyboard too (experimental) (SERIAL SHELL)
- 'pkg_info' command to see the PGK-INFO file of a module if available (SSL/SERIAL SHELLS)
- 'upipl' to list available packages at pypi.org or micropython.org/pi
e.g. 'upipl' or 'upipl [module]' (SSL/SERIAL SHELLS)
- 'update_upyutils' command for SERIAL SHELL
### Fix
- fw and flash commands of upydev
## [0.2.2] 2020-01-13
### Added
- Autocompletion on REPLS (SSL/SERIAL) for "from foo import X" will show option of what to import/autocomplete on match for frozen modules too.
### Fix
- Autocompletion on REPLS (SSL/SERIAL) for "from foo import X" will show option of what to import/autocomplete on match (bug fix)
## [0.2.1] 2020-01-12
### Added
- Autocompletion on REPLS (SSL/SERIAL) for "from foo import X" will show option of what to import/autocomplete on match
- CTRL-u deprecated (no encryption toggle), CTRL-p now shows RAM STATUS (used/free)
- CTRL-e in SHELLS (SSL/SERIAL) moves cursor to end of the line (if not in edit mode)
- 'batl' command for SHELLS(SSL/SERIAL) to print local file with python syntax highlighting
## [0.2.0] - 2020-01-10
### Added
- serial terminal SHELL-REPL mode (same style as SSLWebREPL) "sh_srepl"
- "shr@[dev]" shorcut to "sh_srepl" mode
- commands view, bat, rcat for SSLWebREPL and Serial SHELL-REPL
### Fix
- ssl_wrepl netscan command for esp8266
- Add help of latest upydev commands
- see -c command help info text wraps at terminal length
## [0.1.9] - 2020-01-07
### Added
- Mode to generate RSA key and self signed certificate ('sslgen_rsakey')
- 'ssl_socket_client_server.py' and 'ssl_repl.py' added to the scripts that are updated with 'update_upyutils' mode
- 'upysh2.py' implements the 'tree' command to print filesystem in a tree view
- SSLWebREPL shell terminal mode (experimental) (see DOCS)
- "ssl@[dev]" shortcut to "ssl_wrepl" mode
- Progress bar length and percentage fix, and estimated time
- put and get commands now works in SSL mode too
## [0.1.8] - 2019-12-29
### Added
- New CryptoWebREPL shell local commands ('lsof', 'l_ifconfig', 'l_ifconfig_t') (last one works only on MacOS, linux pending...). Network utilities
- New CryptoWebREPL shell local command 'docs' to open MicroPython Docs site in browser
- New CryptoWebREPL shell local command 'reload' to delete a module/script from sys.path so it can be imported/run again
### Fix
- Paste mode in unencrypted mode
- Fix -h command error if there is no 'UPY_G.config' global group file
- Installation dependencies
## [0.1.7] - 2019-12-24
### Added
- Mode to generate RSA private key, and send it to the device ('gen_rsakey')
- Mode to refresh the WebREPL password with a random password
 and don't leave explicit trace in tcp Websocket packets.
 (this needs upysecrets.py in the device, more info in DOCS/help) ('rf_wrkey')
 This can be automatically after a wrepl session using '-rkey' option (e.g. upydev wrepl -rkey)
- 'upysecrets.py' added to the scripts that are updated with 'update_upyutils' mode
- 'upysh2.py' implements the 'tree' command to print filesystem in a tree view
- "crypto"-webrepl-shell mode (experimental) (see DOCS)
- New option '-@' to redirect a command to a specific device saved in global
  Group 'UPY_G' (this needs to be created with the 'make_group' command )
  (e.g. "upydev make_group -g -f UPY_G -devs foo_device 192.168.1.42 myfoopass")
  Then commands can be redirected to this device from anywhere using -@ foo_device (e.g. upydev ping -@ foo_device )
### Fix
- Progress bar animation now available in put/get/sync modes and auto-adjust to terminal size
- sync mode improved
## [0.1.6] - 2019-12-08
### Added
- New 'update_upyutils' mode to update the last versions of sync_tool.py,
  upylog.py and upynotify.py (will be uploaded to '/lib' folder)
- New 'debug' mode to execute a local script line by line in the target
  upydevice, use -f option to indicate the file
- improved 'fw' mode options of 'list latest' and 'get latest', now option
  '-n' can be used to filter the results (e.g: -n ota or -n idf4)
### Fix
- BSSID column of netscan command now shows mac address instead of bytes format
- refactor of sync mode (shows transfer progress animation also)
## [0.1.5] - 2019-11-23
### Added
- New mode d_sync to sync recursively a directory (all files and subfolders)
(this needs the new version of *sync_tool.py* from upyutils directory to be
  uploaded to the device)
  * the *-tree* option to get the dir tree view is from:
  "https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python" @abstrus
  * to sync to an sd card, sd must be mounted as 'sd', and then use '-s sd' option
- New modes to execute scripts:
  * sysctl: to execute scripts in the upydevice in non-blocking mode (won't
            follow the output) (use -start and -stop options)
  * log: to execute scripts and log its output; use -dslev and -dflev to
        indicate log level of sys.stdout and log file. To stop use CTRL-C
        Use option -daemon to log in 'daemon-like' mode, the output is logged
        to daemon log file. To follow use -follow option. (detailed explanation
          in docs)

- New mode 'stream_test': (this needs the new version of *sync_tool.py*)
  To test  wireless transmission speed of data through sockets (TCP).
   In the default test the upydevice sends 10 MB of data in chunks of 20 kB,
   then speed is obtained from total time elapsed and amount of data received.
   See docs for more info.


### Fix
- Code refactoring using upydevice
## [0.1.4] - 2019-11-12
### Added
- New 'upyutils' script 'upylog.py' a modification of logging module to be able to log messages or exceptions to file and two formats to choose ([NAME] [LVL]
  MSG) or ([DATETIME] [NAME] [LVL] MSG)
- option to log to file in sd (mounted as 'sd')
- New error.log content test in diagnose mode
- New errlog command mode to see 'error.log' file if any with option to indicate
source sd.
- New 'upyutils' script 'upynotify.py' to make easier physical debugging (led, and buzzer notifications)
### Fix
- Command options -g , -st, -rep, -apmd (do not need any argument, they store true if used)
- Option "-md local" in diagnose option (deprecated) use -apmd instead
## [0.1.3] - 2019-11-02
### Fix
- package requests dependency added
### Added
- KeyboardInterrupt command (kbi) to stop for/while loops
- New mode diagnose
- New -apmd option to set target to 192.168.4.1 (AP default)
## [0.1.2] - 2019-10-14
### Added
- '-dir' option to put/get commands to select in which directory to put file or get a file from
## [0.1.1] - 2019-10-01
### Fix
- Dedent with shift-tab in wrepl (normal mode and paste mode)
### Added
- find command to scan for upy devices in the WLAN
- WIFI UTILS commands
## [0.1.0] - 2019-09-19
### Fix
- toggle wrepl in synchronized mode for ssh session
- Group command mode -devs option fix
### Added
- toggle autosuggest mode (fish shell like)
- mg_group command to manage groups to add or remove devices

## [0.0.9] - 2019-08-22
### Added
- NEW WebREPL Terminal mode (Custom keybindings and autocompletion on tab)

## [0.0.8] - 2019-08-18
### Fix
- Fix long output indentation (with head or cat upysh command for example)
### Added
- Autocompletion groups for -G and -GP options

## [0.0.7] - 2019-08-16
### Fix
- Fix help info file.

## [0.0.6] - 2019-08-16
### Added
- Buzz interrupt reverse operation mode (falling)
- Serial repl using picocom
- Group command parallel mode more reliable
- Sensors i2c pin configuration with -i2c option

## [0.0.5] - 2019-08-12

### Added
- Group command parallel mode
