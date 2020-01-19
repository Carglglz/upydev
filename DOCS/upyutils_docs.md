# Upyutils scripts



### *This collection of scripts needs to be uploaded to the upy device to use some commands.*



**SD_AM.py:** This script is used with sd_auto command, see [documentation](Documentation.md#sd_auto) for more info

**bme280.py**: This lib is for the 'weather' sensor BME280 , source: [@robert-hh](https://github.com/robert-hh/BME280)

**init_BME280.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**servo.py**: a lib to control servos, source: [@deshipu](https://bitbucket.org/thesheep/micropython-servo/src/default/)

**ads1115.py**: this lib is for the ADC ads1115 module,  [@robert-hh](https://github.com/robert-hh/ads1x15)

**init_ADS.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**lsm9ds1.py**: this lib is for the IMU lsm9ds1, source: [@hoihu](https://github.com/hoihu/projects/blob/master/raspi-hat/lsm9ds1.py)

**init_IMU.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**socket_client_server.py**: a tiny wrapper to test clients/servers with tcp sockets

**buzzertools.py**: some utility methods to drive a buzzer (beep, alarm, and hardware interrupts)

**ina219.py**: this lib is for the INA219 voltage/current/power sensor, source: [@chrisb2](https://github.com/chrisb2/pyb_ina219)

**init_INA219.py**: a tiny wrapper to add some methods ( read, stream, log, test...)

**stepper.py**: this lib is to control a stepper motor, with a stepper motor driver (tested on [A4988](https://www.pololu.com/file/0J450/a4988_DMOS_microstepping_driver_with_translator.pdf))

**dac_signal_gen.py**: this lib is to generate signals with the on board DAC (sine and square waves)

**sync_tool.py**: this script is to get large files from the upy device faster (files > 100 kB)

**dcmotor.py**: this lib is to control a dc motor, with a dc motor driver (tested on [DRV8871](https://cdn-shop.adafruit.com/product-files/3190/drv8871.pdf))

**mqtt_client.py**: a tiny wrapper to add automatic print message callback

**time_it.py**: a script to measure execution time of other scripts, implemented from, [@peterhinch](https://github.com/peterhinch) [timed_fuction](https://github.com/peterhinch/micropython-samples/tree/master/timed_function)

**sdcard.py**: a lib to read/write to an sd card using spi interface, source [@peterhinch](https://github.com/peterhinch)

**wifiutils.py**: to make easier to save/load wifi configuration (STA and AP ) and connect to an access point or enable its own.

**upylog.py**: a modified version of MicroPython logging module, with time format logging and log to file option

(default file: 'error.log')

**upynotify.py** : a module to notify events with beeps (buzzer needed) and blinks. This is useful to "physical debugging".

**upysecrets.py**: a module to enable end-to-end-encryption and random password generation

**ssl_repl.py**: a module to enable SSL repl

**ssl_socket_client_server.py**: a tiny wrapper to test clients/servers with SSL wrapped tcp sockets

**uping.py**: to make the device send ICMP ECHO_REQUEST packets to network hosts, (this adds statistics and continuous ping) (original [uping.py](https://gist.github.com/shawwwn/91cc8979e33e82af6d99ec34c38195fb) from [@shawwwn](https://github.com/shawwwn))

