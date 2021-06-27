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


------

BLUETOOTH LOW ENERGY DEVICES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See `Bleak Troubleshooting <https://bleak.readthedocs.io/en/latest/troubleshooting.html#capture-bluetooth-traffic>`_

------


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
