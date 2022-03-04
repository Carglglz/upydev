Upyutils
========


*This collection of scripts needs to be uploaded to the device to use some commands.*

Bluetooth Low Energy
^^^^^^^^^^^^^^^^^^^^

**ble_advertising.py**: helper module to do bluetooth low energy advertising easier

**ble_uart_peripheral.py**: helper module for bluetooth low energy UART GATT profile

**ble_uart_repl.py**: module to enable bluetooth low energy REPL through UART GATT profile

**otable.py**: module to enable bluetooth low energy DFU mode in esp32 and do OTA firmware updates.

Config
^^^^^^
**config**: *(__init__.py, configfuncs.py, params.py)*
config module to easily configure/set parameters as named tuples.

Cryptography
^^^^^^^^^^^^

**rsa**: module to perform asymmetric encryption with RSA algorithms

**qrcode.py**: module to be used with ``uqr`` lib and do pretty prints in terminal.

**shasum.py**: module to mimic ``shasum`` (compute hash SHA256 of file or check shafiles)

**upysecrets.py**: module to generate random passwords.

Develop
^^^^^^^

**buzzertools.py**: some utility methods to drive a buzzer (beep, alarm, and hardware interrupts)

**dac_signal_gen.py**: this lib is to generate signals with the on board DAC (sine and square waves)

**test_code.py**: a example test code script

**time_it.py**: a script to measure execution time of other scripts, implemented from, `@peterhinch <https://github.com/peterhinch>`_  `timed_fuction <https://github.com/peterhinch/micropython-samples/tree/master/timed_function>`_

**upylog.py**: a modified version of MicroPython logging module, with time format logging and log to file option (default file: 'error.log')

**upynotify.py** : a module to notify events with beeps (buzzer needed) and blinks. This is useful for "physical debugging".

IRQ
^^^

**irq_controller.py**: a module to controll hardware interrupts

Motor
^^^^^

**dcmotor.py**: this lib is to control a dc motor, with a dc motor driver (tested on `DRV8871 <https://cdn-shop.adafruit.com/product-files/3190/drv8871.pdf>`_ )

**servo.py**: a lib to control servos, source: `@deshipu <https://bitbucket.org/thesheep/micropython-servo/src/default/>`_

**stepper.py**: this lib is to control a stepper motor, with a stepper motor driver (tested on `A4988 <https://www.pololu.com/file/0J450/a4988_DMOS_microstepping_driver_with_translator.pdf>`_ )

Network
^^^^^^^

**mqtt_client.py**: a tiny wrapper to add automatic print message callback

**ota.py**: a module to do OTA firmware updates for esp32

**socket_client_server.py**: a tiny wrapper to test clients/servers with tcp sockets

**ssl_repl.py**: a module to enable SSL repl

**ssl_socket_client_server.py**: a tiny wrapper to test clients/servers with SSL wrapped tcp sockets

**sync_tool.py**: this script is to get large files from the upy device faster (files > 100 kB)

**uping.py**: to make the device send ICMP ECHO_REQUEST packets to network hosts, (this adds statistics, continuous ping, and esp8266 compatibility) (original `uping.py <https://gist.github.com/shawwwn/91cc8979e33e82af6d99ec34c38195fb>`_ from  `@shawwwn <https://github.com/shawwwn>`_ )

**wifiutils.py**: to make easier to save/load wifi configuration (STA and AP ) and connect to an access point or enable its own.

**wpa_supplicant.py**: a module to mimic ``wpa_supplicant`` function, (connect to closest AP based on wpa_supplicant.config file)

**wss_helper.py**: to enable WebSecureREPL (server and client handshakes)

**wss_repl.py**: tiny wrapper of webrepl.py module to enable WebSecureREPL

SD
^^^

**SD_AM.py:** This script is used with ``sd_auto`` command, see `sd_auto <https://upydev.readthedocs.io/en/latest/upycmd.html>`_ for more info

**sdcard.py**: a lib to read/write to an sd card using spi interface, source `@peterhinch <https://github.com/peterhinch>`_

Sensors
^^^^^^^^

**ads1115.py**: this lib is for the ADC ads1115 module, `@robert-hh <https://github.com/robert-hh/ads1x15>`_

**bme280.py**: This lib is for the 'weather' sensor BME280 , source: `@robert-hh <https://github.com/robert-hh/BME280>`_

**ina219.py**: this lib is for the INA219 voltage/current/power sensor, source: `@chrisb2 <https://github.com/chrisb2/pyb_ina219>`_

**lsm9ds1.py**: this lib is for the IMU lsm9ds1, source: `@hoihu <https://github.com/hoihu/projects/blob/master/raspi-hat/lsm9ds1.py>`_

**init_ADS.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**init_BME280.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**init_INA219.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**init_IMU.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

Shell
^^^^^^

**upysh2.py**: upysh extesion with tree, du, and rm -r commands.

**upysh.py**: upysh custom version with ls, cat extended with pprint output and matching patterns.

**nanoglob.py**: glob module to match any pattern in device filesystem.
