HOWTO
=====

DEBUG
-----

SERIAL DEVICES
^^^^^^^^^^^^^^
While working with new serial devices be aware of:

  * Use a USB data cable, otherwise the device will be powered on but won't be accessible.

  * If using a device with no native USB support (e.g. esp32, esp8266) most likely it will have a
    CP210x USB to UART Bridge Virtual COM Port (VCP) chip (or something similar), so the up to date drivers will be needed.
    (e.g. `Silicon labs VCP Drivers <https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers>`_) [#]_

  * If using Linux, it may be necessary to add user to dialout group to allow access to the USB device. [#]_


  .. code-block:: console

      $ sudo usermod -a -G dialout $USER


  .. [#] This may require reset the computer so the drivers can be loaded properly.

  .. [#] See `How do I allow a non-default user to use serial device ttyUSB0? <https://askubuntu.com/questions/112568/how-do-i-allow-a-non-default-user-to-use-serial-device-ttyusb0>`_

------


WEBSOCKET DEVICES (WIFI)
^^^^^^^^^^^^^^^^^^^^^^^^

  While working with devices connected over WiFi, in order to succeed sending upydev commands make sure that there is a reliable connection between the host and the device and that the wifi signal strength (rssi) in the device is above -80  (below -80 performance could be inconsistent)

  **A 'Reliable' connection** **means that there is no packet loss**  (use ping or  `upydev ping` command to check)

  See  `Received signal strength indication <https://en.wikipedia.org/wiki/Received_signal_strength_indication>`_
  and `Mobile Signal Strength Recommendations <https://wiki.teltonika.lt/view/Mobile_Signal_Strength_Recommendations>`_

  **TRACKING PACKETS**


  To see if "command packets" are sent and received or lost use `Wireshark <https://www.wireshark.org>`_ and filter the ip of the device.

  **SEE WHAT'S GOING ON UNDER THE HOOD**:

  *ℹ️ Host and the device must be connected.*

    In a terminal window open a 'serial repl' with `upydev srepl --port [USBPORT]` command

    In another window use upydev normally. Now in the terminal window with the serial repl you can see which commands are sent.


  **Working with dchp_hostname instead of IP**

  To do this activate station interface and set ``dhcp_hostname`` before connecting to the WLAN, e.g. in MicroPython REPL/script

  .. code-block:: console

    >>> import network
    >>> wlan = network.WLAN(network.STA_IF)
    >>> wlan.active(True)
    >>> wlan.config(dhcp_hostname='esp_dev')

  After connecting, the device should be reachable as ``esp_dev.local``, do ``$ ping esp_dev.local``,  ``avahi-resolve --name esp_dev.local``
  or ``$ sudo resolvectl query esp_dev.local`` to check that it is working as expected.

  .. code-block:: console

      $ ping esp_dev.local
      PING esp_dev.local (192.168.1.73): 56 data bytes
      64 bytes from 192.168.1.73: icmp_seq=0 ttl=255 time=2.403 ms
      64 bytes from 192.168.1.73: icmp_seq=1 ttl=255 time=219.618 ms
      64 bytes from 192.168.1.73: icmp_seq=2 ttl=255 time=239.348 ms
      ^C
      --- esp_dev.local ping statistics ---
      3 packets transmitted, 3 packets received, 0.0% packet loss
      round-trip min/avg/max/stddev = 2.403/153.790/239.348/107.349 ms

      $ avahi-resolve --name esp_dev.local

      esp_dev.local	192.168.1.73

      $ sudo resolvectl query esp_dev.local

      esp_dev.local: 192.168.1.73                     -- link: enp5s0


  Now is possible to use this ``dhcp_hostname`` for ``-t`` argument while configuring a device e.g.

  .. code-block:: console


      $ upydev config -t esp_dev.local -p mypass -@ esp_dev -gg
      WebSocketDevice esp_dev settings saved in global group!

      $ upydev check -@ esp_dev
      Device: esp_dev
      Address: esp_dev.local, Device Type: WebSocketDevice

      $ upydev check -@ esp_dev -i
      Device: esp_dev
      WebSocketDevice @ ws://192.168.1.73:8266, Type: esp32, Class: WebSocketDevice
      Firmware: MicroPython v1.12-63-g1c849d63a on 2020-01-14; ESP32 module with ESP32
      (MAC: 30:ae:a4:1e:73:f8, RSSI: -38 dBm)

      $ upydev ping -@ esp_dev
      PING esp_dev.local (192.168.1.73): 56 data bytes
      64 bytes from 192.168.1.73: icmp_seq=0 ttl=255 time=56.655 ms
      64 bytes from 192.168.1.73: icmp_seq=1 ttl=255 time=75.751 ms
      ^C
      --- esp_dev.local ping statistics ---
      2 packets transmitted, 2 packets received, 0.0% packet loss
      round-trip min/avg/max/stddev = 56.655/66.203/75.751/9.548 ms

.. note::

  Be aware some systems default ``ping`` use ``ipv6`` first, and fallback to ``ipv4`` while
  resolving mDNS names, which may cause some delay. Use  ``ping -4`` instead which will use
  ``ipv4`` directly and resolve the name faster.

------

BLUETOOTH LOW ENERGY DEVICES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See `Bleak Troubleshooting <https://bleak.readthedocs.io/en/latest/troubleshooting.html#capture-bluetooth-traffic>`_

------


WEBSOCKET DEVICES (WIFI) THROUGH ZEROTIER GLOBAL AREA NETWORK
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See `ZeroTier Global Area Network <https://www.zerotier.com>`_

Although there is no library to directly connect a microcontroller to a zerotier network, a raspberry pi can be used as a bridge to make it possible.
So install zerotier in your computer and in the raspberry pi.

Setup a zerotier network, add both your computer and the raspberry pi. (`guide <https://breadnet.co.uk/zerotier-cloud-managment/?pk_campaign=reddit&pk_kwd=zerotier_cloud>`_)
Now add the rules for port fordwarding e.g. for WebREPL port (*8266*) in the raspberry pi and device with IP *192.168.1.46*

First enable port forwarding by editing ``/etc/sysctl.conf`` and uncomment

.. code-block:: console

    net.ipv4.ip_forward=1

And reload

.. code-block:: console

    $ sudo sysctl -p
    net.ipv4.ip_forward = 1

Then set the rules with ``iptables``

.. code-block:: console

    $ sudo iptables -t nat -A PREROUTING -p tcp --dport 8266 -j DNAT --to-destination 192.168.1.46:8266
    $ sudo iptables -t nat -A POSTROUTING -j MASQUERADE

And if using a firewall e.g. `ufw`

.. code-block:: console

    $ sudo ufw allow 8266
    $ sudo ufw route allow in on ztrta7qtbo out on wlan0 to 192.168.1.46 port 8266 from any
    $ sudo ufw reload

Where *ztrta7qtbo* is the zerotier interface (check this and its IP with *ifconfig*)
Now connecting to the raspberry pi zerotier IP and port *8266* should redirect the traffic to the microcontroller port *8266* (WebREPL), e.g.

.. code-block:: console

    $ upydev config -t 142.64.115.62 -p mypass -gg -@ zerotdevice

Where *142.64.115.62* is the IP of the raspberry pi zerotier interface.

To configure shell-repl with WebSecureREPL through zerotier network do the same as above but with port 8833.

To enable ota firmware updates (e.g your computer has a zerotier IP *142.64.115.75*)

.. code-block:: console

    $ sudo iptables -t nat -A PREROUTING -p tcp --dport 8014 -j DNAT --to-destination 142.64.115.75:8014
    $ sudo iptables -t nat -A POSTROUTING -j MASQUERADE

And if using a firewall e.g. `ufw`

.. code-block:: console

    $ sudo ufw allow 8014
    $ sudo ufw route allow in on wlan0 out on ztrta7qtbo to 142.64.115.75 port 8014 from any
    $ sudo ufw reload

.. note::

  If ``$ sudo zerotier-cli info`` shows this error:
  *Error connecting to the ZeroTier service:*

  *Please check that the service is running and that TCP port 9993 can be contacted via 127.0.0.1.*

  Add this rule ``$ sudo iptables -t nat -I POSTROUTING -o lo -j ACCEPT``

Now shell-repl mode is available using ``-zt`` option: e.g.


.. code-block:: console

    $ upydev shl@zerotdevice -zt 142.64.115.75/192.168.1.79

Where *192.168.1.79* is the IP of the raspberry pi in the local area network.

Or configure a device with the ``-zt`` option so it is not required anymore, e.g.

.. code-block:: console

    $ upydev config -t 142.64.115.62 -p mypass -gg -@ zerowpy -zt 142.64.115.75/192.168.1.79
    WebSocketDevice zerotdevice settings saved in global group!
    WebSocketDevice zerotdevice settings saved in ZeroTier group!

Now to access the shell-repl mode through zerotier network:

.. code-block:: console

    $ upydev shl@zerotdevice


.. note::

  To allow ``ping`` and ``probe`` work correctly instead of pinging the raspberry pi,
  add the ssh alias of the raspberry pi and the local ip or mDNS name of the device to ``-zt`` option as ``:[ALIAS]/[DEVICE_IP]`` e.g. :

    .. code-block:: console

      $ upydev config -t 142.64.115.62 -p mypass -gg -@ zerowpy -zt 142.64.115.75/192.168.1.79:rpi/192.168.1.46
      # OR
      upydev config -t 142.64.115.62 -p mypass -gg -@ zerowpy -zt 142.64.115.75/192.168.1.79:rpi/weatpy.local

  This expects the raspberry pi to be accesible through ``ssh [ALIAS]``, and the keys added to the ``ssh-agent``.
  See `ssh add keys <https://www.ssh.com/academy/ssh/add>`_ and `ssh alias <https://ostechnix.com/how-to-create-ssh-alias-in-linux/>`_

  Now ``ping`` and ``probe`` should actually reach the device through raspbery pi ping, e.g.:

  .. code-block:: console

      $ upydev ping -@ zerowpy


TESTING DEVICES WITH PYTEST
---------------------------

`upydevice <https://github.com/Carglglz/upydevice/tree/master>`_ device classes allow to test MicroPython code in devices interactively with pytest, e.g. button press, screen swipes, sensor calibration, actuators, servo/stepper/dc motors , etc.
Under `tests <https://github.com/Carglglz/upydev/tree/develop/tests>`_ directory there are example tests to run with devices.
e.g.

.. code-block:: console

    $ upydev pytest test_esp_serial.py -@ sdev
    Running pytest with Device: sdev
    ============================================================= test session starts =============================================================
    platform darwin -- Python 3.7.9, pytest-6.1.0, py-1.9.0, pluggy-0.13.1
    rootdir: /Users/carlosgilgonzalez/Desktop/MICROPYTHON/TOOLS/upydevice/test, configfile: pytest.ini
    collected 7 items

    test_esp_serial.py::test_devname PASSED
    test_esp_serial.py::test_platform
    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:14 [pytest] [ESP32] : Running SerialDevice test...
    22:34:14 [pytest] [ESP32] : DEV PLATFORM: esp32
    SerialDevice @ /dev/tty.SLAB_USBtoUART, Type: esp32, Class: SerialDevice
    Firmware: MicroPython v1.16 on 2021-06-24; ESP32 module with ESP32
    CP2104 USB to UART Bridge Controller, Manufacturer: Silicon Labs
    (MAC: 30:ae:a4:23:35:64)
    22:34:14 [pytest] [ESP32] : DEV PLATFORM TEST: [✔]
    Test Result: PASSED
    test_esp_serial.py::test_blink_led LED: ON
    LED: OFF
    LED: ON
    LED: OFF

    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:17 [pytest] [ESP32] : BLINK LED TEST: [✔]
    Test Result: PASSED
    test_esp_serial.py::test_run_script
    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:17 [pytest] [ESP32] : RUN SCRIPT TEST: test_code.py
    2000-01-01 00:53:30 [log_test] [INFO] Test message2: 100(foobar)
    2000-01-01 00:53:30 [log_test] [WARN] Test message3: %d(%s)
    2000-01-01 00:53:30 [log_test] [ERROR] Test message4
    2000-01-01 00:53:30 [log_test] [CRIT] Test message5
    2000-01-01 00:53:30 [None] [INFO] Test message6
    2000-01-01 00:53:30 [log_test] [ERROR] Exception Ocurred
    Traceback (most recent call last):
    File "test_code.py", line 14, in <module>
    ZeroDivisionError: divide by zero
    2000-01-01 00:53:30 [errorlog_test] [ERROR] Exception Ocurred
    Traceback (most recent call last):
    File "test_code.py", line 20, in <module>
    ZeroDivisionError: divide by zero
    22:34:18 [pytest] [ESP32] : RUN SCRIPT TEST: [✔]
    Test Result: PASSED
    test_esp_serial.py::test_raise_device_exception
    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:18 [pytest] [ESP32] : DEVICE EXCEPTION TEST: b = 1/0
    [DeviceError]:
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    ZeroDivisionError: divide by zero

    22:34:18 [pytest] [ESP32] : DEVICE EXCEPTION TEST: [✔]
    Test Result: PASSED
    test_esp_serial.py::test_reset
    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:18 [pytest] [ESP32] : DEVICE RESET TEST
    Rebooting device...
    Done!
    22:34:18 [pytest] [ESP32] : DEVICE RESET TEST: [✔]
    Test Result: PASSED
    test_esp_serial.py::test_disconnect
    ---------------------------------------------------------------- live log call ----------------------------------------------------------------
    22:34:18 [pytest] [ESP32] : DEVICE DISCONNECT TEST
    22:34:18 [pytest] [ESP32] : DEVICE DISCONNECT TEST: [✔]
    Test Result: PASSED

    ============================================================== 7 passed in 5.20s ==============================================================

IDE INTEGRATION with PLATFORMIO TERMINAL
----------------------------------------

ATOM
^^^^

  To do this go to `Atom Settings --> Packages -->` Then search for `platformio-ide-terminal` and click on `Settings`. Here go to `Custom Texts` section: (There are up to 8 "custom texts" or commands that can be customised) These custom text will be pasted an executed in the Terminal when called. And this can be done with keybindings or key-shortcuts. For example:

  - **To automate upload the current file:**

    In `Custom text 1`  write:  `upydev put -f $F`

  - **To automate run the current file:**

    In `Custom text 2`  write:  `upydev run -f $F`

  - **To automate open the wrepl:**

    In `Custom text 3`  write:  `upydev wrepl`

  - **To automate diagnose:**

    In `Custom text 4`  write:  `upydev diagnose`



  Now configure the Keybindings, to do this go to `Settings --> Keybindings --> your keymap file`

  Then in `keymap.cson` add: (This is an example, the key combination can be changed)

  .. code-block:: console

    'atom-workspace atom-text-editor:not([mini])':
    'ctrl-shift-d': 'platformio-ide-terminal:insert-custom-text-4'
    'ctrl-cmd-u': 'platformio-ide-terminal:insert-custom-text-1'
    'ctrl-cmd-x': 'platformio-ide-terminal:insert-custom-text-2'
    'ctrl-cmd-w': 'platformio-ide-terminal:insert-custom-text-3'


  Save the file and now when pressing these key combinations should paste the command and run it in the Terminal.

Visual Studio Code
^^^^^^^^^^^^^^^^^^^

  Using tasks and adding the shortcut in keybinds.json file for example:

  Task:

  .. code-block:: json

    "version": "2.0.0",
        "tasks": [
            {
                "label": "upydev_upload",
                "type": "shell",
                "command": "upydev",
                "args": ["put", "-f", "${file}"],
                "options": { "cwd": "${workspaceFolder}"},
                "presentation": { "echo": true,
                    "reveal": "always",
                    "focus": true,
                    "panel": "shared",
                    "showReuseMessage": true,
                    "clear": false
                },
                "problemMatcher": []
            }]


Keybinding.json

.. code-block:: json

  { "key": "ctrl+cmd+u",
    "command": "workbench.action.tasks.runTask",
    "args": "upydev_upload"}
