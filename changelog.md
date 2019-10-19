# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] [Unreleased] [Github Repo]
### Fix
- package requests dependency added
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
