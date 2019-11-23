# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] [Unreleased] [Github Repo]
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
