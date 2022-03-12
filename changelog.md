# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] Unreleased Github Repo [develop]
## [0.3.9] - 2022-03-12
## Fix
-  parse additional positional args in cli bug
## [0.3.8] - 2022-03-04
## Added
- added command history file to shell-repls
- added tests and example tests to run with devices
- added shell support for command concatenation (`&&`)
- added shell basic support for pipe device output to a local file (`>, >>, |`)
- `register` command to register a device name or group as a callable shell function
- `ota` command to do OTA Firmware updates (esp32). This needs `ota.py` for network (LAN/WiFi) or `otable.py` for BLE. (`upyutils` directory) and `firmware.bin` file in `build-GENERIC_OTA` or from micropython esp32-ota downloads.
- `ota` with `-sec` option to do OTA over TLS. (This needs `kg ssl` first).
- `rsa sign`, `rsa verify` commands to sign file or verify signatures made with device RSA key
- `kg rsa host`, to generate a host RSA key pair and send public key to device.
- `rsa sign host [FILE]` to sign a file with host RSA key.
- `rsa verify host [FILE]` to verify in the device a file signature made with host RSA key
- `rsa` lib in `upyutils` to support RSA key load, sign, verify, encrypt, decrypt,
generation and export in PEM format
- `kg rsa` added option `-rkey` to remove RSA private key from the host, so in combination with `-tfkey` option, the RSA private key will be stored only in the device.
- `rsa auth` to authenticate a device with a RSA encrypted challenge.
- `shasum.py` lib in `upyutils` to support hash SHA-256 check
- `shasum` and `shasum_c` to compute hash SHA-256 of files and check shasum files.
- `ls` command to improve ls from `upysh`, with multiple dirs and pattern matching
- `cat` command that accepts multiple files and pattern matching
- refactored help
- dropped wlan utils
- dropped prototype commands (this will be a stand alone cli or add-on for upydev)
# Fix
- `mpyx` command with multiple files
- `kg wr` now use RSA public key for password derivation and send encrypted password
that is decrypted and stored in device.
- Load time in MacOS caused by upydevice->BleDevice->bleak->corebluetooth
- Save in ecdsa key/cert directly in `DER`, no need for `openssl` in `PATH`.
- Allow mdns name in ssl certificate.
- Improved file io operations (`put`, `get`, `dsync` ...), more flexibility indicating files / dirs / pattern matching etc. Improved overall performance, specially for WebSocketDevices.
- fix `ping`, `probe` for zerotier devices (this needs updated config, see how-to section in docs.)
- fix `update_upyutils` if dir `lib` does not exists.
- refactored shells-repls, now `shl`, or `rpl` commands only
## [0.3.7] 2021-12-16
## Added
- `rssi` command in shell repls to get RSSI value (Wifi or Ble)
- `make_sgroup` / `mksg` command to create a subgroup of an existing group of devices.
- `set_hostname` command to set hostname of the device for dhcp service (needs *wpa_supplicant.py*)
- `set_localname` command to set localname of the device for ble gap/advertising name (needs *ble_uart_peripheral.py*)
- Now `-@` option accepts multiple devices, names with `*` wildcard or global group `gg` or other group names, e.g. `upydev check -i -@ esp\* dev{1..4} mytestgroup`
will expand to all devices that start with `esp` , `dev1 dev2 dev3 dev4` and devices configured in `mytestgroup`
## Fix
- `firmwaretools.get_fw_versions` update after `micropython.org\all` not working anymore.
- fix device name instead of `None` in `put`, `get`, `fget`, `dsync` in `sslweb_repl` with `-nem` mode enabled.
- fix `fget` disconnection error.

## [0.3.6] 2021-10-24
## Added
- `zerotier` compatibility through raspberry pi bridge (port forwarding + ufw route rules) and `-zt [HOST IP/BRIDGE IP]` option to indicate host zerotier ip and raspberry pi bridge local ip for ssl
shell-repl mode. Also `-zt` option with config command compatibility.
- mDNS `.local`/`dhcp_hostname` compatibility, so device configuration works across networks, e.g, `-t` argument now can accept `-t mydev.local` and resolve to device ip.
- added `-zt [IP]` in `keygen ssl` for zerotier `wss-sslwebrepl` mode
- `wpa_supplicant.py` utility in upyutils
- New buzzer effects in `buzzertools.py`: `error`, `warning_call`, `phone_call`, `door_bell`.
- Added docs for `zerotier` bridge configuration in `HOWTO`
## Fix
- `fget` error on connection, and unintended verbose output on close.
- `check -i`, `info` commands in `-apmd`, if connected to AP of the device.
- fix ssl cert authentication in `wss` mode if using `.local`/`dhcp_hostname` target.

## [0.3.5] 2021-09-09
## Fix
- `set_ntptime` with WebSocket Devices
- blerepl paste command
- paste command in sslweb_repl -nem mode
## Added
- get rssi value in blerepl

## [0.3.4] 2021-08-12
### Fix
- Fix autocomplete on tab in REPL while `import` or `from X import` in SERIAL REPL
- Command names change:
  * `filesize` --> `du`,
  * `filesys_info` --> `df`
  * `fw` --> `fwr`
  * `d_sync` --> `dsync`
  * `sync` --> `fget`

- Catching passwords too short for AP configuration
- Refactor help info organisation for easy reading.
- Refactor device management actions (configuration, groups...)
- Refactor firmware actions, `-i` option to check firmware and platform match. (from firmware file name)
- `tree` command in upysh2.py unix/linux like.
- drop ``mpy-cross`` dependency, better to build from source.
### Added
- Autocomplete `shr@` , `ssl@`, `wssl@` and `ble@` commands with saved devices in UPY_G global group
- `pytest` and `pytest-setup` command in SHELL-REPLS
- `pytest` and `pytest-setup` command mode in CLI.
- commands that start with `%` or not registered in SHELL-REPLS commands are forwarded to local shell (works with alias too)
- Ble SHELL-REPL `ble@[device]`
- `set` command to set current device configuration of a device saved in global group
- `check` command to see device configuration (`-i` to see more info if device available)
- `dm` command to see help about DEVICE MANAGEMENT
- `gc` command to see help about GENERAL COMMANDS
- `wu` command to see help about WLAN UTILS COMMANDS
- `sd` command to see help about SD UTILS COMMANDS
- `pro` command to see help about PROTOTYPE COMMANDS
- `gg` to see global group
- `-gg` flag to set -G flag to global group (`-gg` == `-G UPY_G`)
- `-ggp` flag to set -GP flag to global group (`-ggp` == `-GP UPY_G`)
- `%` before any command e.g. `%config` display help info about that command.
- `probe` command to test if a device/group is reachable
- `scan` command to look for devices (serial [-sr], network [-nt] or ble [-bl])
- `shl` / `shell`, and `rpl` / `repl` commands works with `@` or `-@` and will detect device type, redirecting to the proper SHELL-REPL / REPL type.
- `put`, `get`, `install`, `fget`, `dsync`, file operations now support indicating file/files/cwd/expression as a second argument, e.g, `upydev put this_file.py`, `upydev put demo_*.py`,  `upydev put fileone.py filetwo.py`, `upydev put cwd -dir lib` ...
- Alias and positional args for keygen/firmware/flash actions `upydev kg/keygen rsa/wr/ssl`, `upydev fwr get/list latest`, `upydev flash esp32-idf4-20200122-v1.12-76-gdccace6f3.bin`,`upydev flash pybv11-20200114-v1.12-63-g1c849d63a.dfu` ...
- Alias and positional args for `make_group, mg_group` actions `mkgroup/mkg, mggroup/mgg`, and `see`. e.g `upydev see MY_GROUP`, `upydev mkg MY_GROUP -devs mydevtest 192.168.1.40 mypasswd`, `upydev mgg MY_GROUP -add sdev2 /dev/tty.SLAB_USBtoUART 115200`
- Alias and positional args for SD actions `upydev sd enable/init/deinit/auto`
- upydev pypi version checking on `h`/ `help` command.
- `-gf` flag to indicate a group file operation (files are upload/download to/from a directory with the name of the device in the current working directory). It uses local group configuration file if available (unless -gg flag is indicated), otherwise it falls back to global group configuration
- `-rf` flag for `dsync` mode, to remove files or directories deleted in local dir.
- `-to [devname]` flag now can be used with `-tfkey` to transfer keys by USB/Serial
- `-d ` flag for `dsync` to sync from device to host.
- `backup` command == `dsync . -d` to make a backup of the device filesystem
- `rsync` command == `dsync [DIR] -rf -wdl` to recursively sync (deleting files too)

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
- 'dsync' command to recursively sync directories for (SSL/SERIAL SHELLS)
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
- New 'update_upyutils' mode to update the latest versions of sync_tool.py,
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
