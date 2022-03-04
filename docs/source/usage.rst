
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
			e.g. ``$ upydev info``, ``$ upydev mem``, ``$ upydev df``

	3) "Raw" or unregistered commands:
			Commands that are not registered in upydev are sent directly to the device as in a REPL.
			e.g. ``$ upydev "led.on()"``, ``$ upydev "print('Hello')"``, ``$ upydev "import mylib; mylib.dothis()"``


Mode/Tools
-----------

	> :ref:`modetools:HELP`
			To see help on any mode, tool or command.

			ACTIONS: ``help``, ``h``, ``dm``, ``fio``, ``fw``, ``kg``, ``rp``, ``sh``, ``db``, ``gp``, ``gc``.

	> :ref:`modetools:Device Management`
			To manage configuration of a device/group of devices.

			ACTIONS : ``config``, ``check``, ``set``, ``register``, ``lsdevs``, ``mkg``, ``mgg``, ``mksg``, ``see``, ``gg``

	> :ref:`modetools:File IO operations`
			To upload/download files to/from a device.

			ACTIONS: ``put``, ``get``, ``dsync``, ``install``, ``update_upyutils``

	> :ref:`modetools:Firmware`
			To list, get or flash the firmware of a device.

			ACTIONS: ``fwr``, ``flash``, ``ota``, ``mpyx``

	> :ref:`modetools:Keygen`
			To generate SSL key-certs and random WebREPL passwords.

			ACTIONS: ``kg rsa``, ``kg wr``, ``kg ssl``, ``rsa sign``, ``rsa verify``, ``rsa auth``


	> :ref:`modetools:REPL`
			To enter the REPL.

			ACTIONS: ``repl``, ``rpl``

	> :ref:`modetools:SHELL-REPL`:
			To enter shell-repl.

			ACTIONS: ``shell``, ``shl``,  ``shl-config``, ``set_wss``, ``jupyterc``

	> :ref:`modetools:Debugging`
			To debug device connection, run scripts or run interactive test with pytest.

			ACTIONS: ``ping``, ``probe``, ``scan``, ``run``, ``timeit``, ``stream_test``, ``sysctl``, ``log``, ``pytest setup``, ``pytest``

	> :ref:`Group Command Mode <modetools:Group Mode>`
			To operate with a group of devices.

			OPTIONS: ``-G``, ``-GP``


upy Commands
------------
	> :ref:`upycmd:General Commands`

		A set of commands to control or configure the device.
