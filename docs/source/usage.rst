
Usage
======

usage: ``$ upydev ACTION [options]``

Upydev can handle three types of directives:

	1) An ACTION from Mode / Tools:
			Utilities to manage/control a device.
			e.g. ``$ upydev config -t /dev/tty.usbmodem387E386731342 -@ pyblite``,
			``$ upydev check``, ``$ upydev put my_script.py``


	2) A predefined MicroPython command:
			This always requires a connected device and it translates into MicroPython code snippets.
			e.g. ``$ upydev info``, ``$ upydev meminfo``, ``$ upydev df``

	3) "Raw" or unregistered commands:
			Commands that are not registered in upydev are sent directly to the device as in a REPL.
			e.g. ``$ upydev "led.on()"``, ``$ upydev "print('Hello')"``, ``$ upydev "import mylib; mylib.dothis()"``


Mode/Tools
-----------

	> :ref:`modetools:HELP`
			To see help on any mode, tool or command.

			ACTIONS: ``help``, ``h``, ``dm``, ``fio``, ``fw``, ``kg``, ``rp``, ``sh``, ``db``, ``gp``, ``gc``, ``wu``, ``sd``, ``pro``.

	> :ref:`modetools:Device Management`
			To manage configuration of a device/group of devices.

			ACTIONS : ``config``, ``check``, ``set``, ``register``, ``make_group``, ``mg_group``, ``make_sgroup``, ``see``, ``gg``

	> :ref:`modetools:File IO operations`
			To upload/download files to/from a device.

			ACTIONS: ``put``, ``get``, ``fget``, ``dsync``, ``rsync``, ``backup``, ``install``, ``update_upyutils``

	> :ref:`modetools:Firmware`
			To list, get or flash the firmware of a device.

			ACTIONS: ``fwr``, ``flash``, ``ota``, ``mpyx``

	> :ref:`modetools:Keygen`
			To generate SSL key-certs and random WebREPL passwords.

			ACTIONS: ``gen_rsakey``, ``rsa_sign``, ``rsa_verify``, ``rf_wrkey``, ``sslgen_key``


	> :ref:`modetools:REPL`
			To enter the REPL.

			ACTIONS: ``repl``, ``rpl``, ``wrepl``, ``wssrepl``, ``srepl``

	> :ref:`modetools:SHELL-REPL`:
			To enter shell-repl modes.

			ACTIONS: ``shell``, ``shl``, ``ssl_wrepl``, ``ssl``, ``sh_srepl``, ``shr``, ``wssl``, ``set_wss``, ``ble``, ``jupyterc``

	> :ref:`modetools:Debugging`
			To debug device connection, run scripts or run interactive test with pytest.

			ACTIONS: ``ping``, ``probe``, ``scan``, ``run``, ``timeit``, ``diagnose``, ``errlog``, ``stream_test``, ``sysctl``, ``log``, ``debug``, ``pytest-setup``, ``pytest``

	> :ref:`Group Command Mode <modetools:Group Mode>`
			To operate with a group of devices.

			OPTIONS: ``-G``, ``-GP``


upy Commands
------------
	> :ref:`upycmd:General Commands`

		A set of commands to control or configure the device.

	> :ref:`upycmd:WiFi Utils`

		To set or manage WiFi configuration or connection mode.

	> :ref:`upycmd:SD`

		A set of commands to mount/unmount a SD card.

	> :ref:`upycmd:Prototype`

		A set of commands to test/prototype sensors, actuators, networking...
