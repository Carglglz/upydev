
Usage
======

usage: ``$ upydev ACTION [options]``

Upydev can handle three types of directives:

	1) An ACTION from Mode / Tools:
			Utilities to manage/control that not always require a connected device.
			e.g. ``$ upydev config -t /dev/tty.usbmodem387E386731342 -@ pyblite``,
			``$ upydev check``, ``$ upydev put my_script.py``


	2) A predefined MicroPython command:
			This always require a connected device and it traduces into MicroPython code snippets.
			e.g. ``$ upydev info``, ``$ upydev meminfo``, ``$ upydev df``

	3) "Raw" or unregistered commands:
			Commands that are not registered in upydev are sent directly to the device as in a REPL.
			e.g. ``$ upydev "led.on()"``, ``$ upydev "print('Hello')"``, ``$ upydev "import mylib; mylib.dothis()"``


Mode/Tools
-----------
	> DEVICE MANAGEMENT: '$ upydev dm' to see help on device management.
	    ACTIONS : config, check, set, make_group, mg_group, see, gg

	> FILEIO: '$ upydev fio' to see help on file input/ouput operations.
	    ACTIONS: put, get, sync, d_sync, install, update_upyutils

	> FIRMWARE: '$ upydev fw' to see help on firmware operations.
	    ACTIONS: fwr, flash, mpyx

	> KEYGEN: '$ upydev kg' to see help on keygen operations.
	    ACTIONS: gen_rsakey, rf_wrkey, sslgen_key

	> REPLS: '$ upydev rp' to see help on repls modes.
	    ACTIONS: repl, rpl, wrepl, wssrepl, srepl

	> SHELL-REPLS: '$ upydev sh' to see help on shell-repls modes.
	    ACTIONS: shell, shl, ssl_wrepl, ssl, sh_srepl, shr, wssl, set_wss, ble, jupyterc

	> DEBUGGING: '$ upydev db' to see help on debugging operations.
	    ACTIONS: ping, probe, scan, run, timeit, diagnose, errlog, stream_test,
	             sysctl, log, debug, pytest

	> GROUP COMMAND MODE: '$ upydev gp' to see help on group mode options.
	    OPTIONS: -G, -GP

	> HELP: '$ upydev h' or '$ upydev help' to see help (without optional args)
	        '$ upydev -h' or '$ upydev --help' to see full help info.

	        - To see help about a any ACTION/COMMAND
	          put % before that ACTION/COMMAND as : $ upydev %ACTION

	    ACTIONS: help, h, dm, fio, fw, kg, rp, sh, db, gp, gc, wu, sd, pro.

upy Commands
------------
	> GENERAL: do '$ upydev gc' to see General commmands help.

	> WIFI UTILS: do '$ upydev wu' to see Wifi utils commands help.

	> SD: do '$ upydev sd' to see SD utils commands help.

	> PROTOTYPE: do '$ upydev pro' to see Prototype utils commands help.
