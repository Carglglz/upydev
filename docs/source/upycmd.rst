
Upy Commands
============

Description








General
-------

> GENERAL: do '$ upydev gc' to see General commmands help.

Usage '$ upydev COMMAND [opts]'
    COMMAND:
        - info : for upy device system info
        - id : for upy device unique id
        - upysh : to enable the upy shell in the upy device (then do 'upydev man' to
                access upysh manual info)
        - reset : to do a soft reset in upy device
        - kbi : sends CTRL-C signal to stop an ongoing loop, to be able to access repl again
        - uhelp : just calls micropython help
        - umodules: just calls micropython help('modules')
        - meminfo : for upy device RAM memory info; call it once to check actual memory,
                    call it twice and it will free some memory
        - du : to get the size of file in root dir (default) or sd with '-s sd' option;
                    if no file name indicated with -f option, prints all files
        - df : to get memory info of the file system, (total capacity, free, used),
                    (default root dir, -s option to change)
        - netinfo : for upy device network info if station is enabled and connected to an AP
        - netinfot : same as netinfo but in table format
        - netscan : for upy device network scan
        - netstat_on : to enable STA
        - netstat_off : to disable STA
        - netstat_conn : to connect to an AP , must provide essid and password (see -wp)
        - netstat : STA state ; returns True if enabled, False if disabled
        - ap_on : to enable AP
        - ap_off : to disable AP
        - apstat : AP state ; returns True if enabled, False if disabled
        - apconfig : AP configuration of essid and password with authmode WPA/WPA2/PSK,
                    (see -ap), needs first that the AP is enabled (do 'upydev ap_on')
        - apscan : scan devices connected to AP; returns number of devices and mac address
        - i2c_config : to configure the i2c pins (see -i2c, defaults are SCL=22, SDA=23)
        - i2c_scan : to scan i2c devices (must config i2c pins first)
        - spi_config: to configure the spi pins (see -spi, defaults are SCK=5,MISO=19,MOSI=18,CS=21)
        - set_localtime: to pass host localtime and set upy device rtc
        - set_ntptime: to set rtc from server, (see -utc for time zone)
        - get_datetime: to get date and time (must be set first, see above commands)


WiFi Utils
----------

> WIFI UTILS: do '$ upydev wu' to see Wifi utils commands help.

WIFI UTILS: Usage: '$ upydev COMMAND [opts]'
    *(needs wifiutils.py in upydevice, see upyutils in upydev github repo)*
    COMMAND:
        - wlan_init: Initiates wlan util (call this before the following commands)
        - wsta_config: Saves a "netowrk STA" configuration json file in upydevice, use with -wp option as -wp 'ssid' 'password'
        - wap_config: Saves a "netowrk AP" configuration json file in upydevice, use with -ap option as -ap 'ssid' 'password'
        - wsta_conn: Connects to the wlan configured with the command wsta_config
        - wap_conn: Enables the upydevice AP configured with the command wap_config



SD
---

> SD: do '$ upydev sd' to see SD utils commands help.

> SD: Usage '$ upydev COMMAND [opts]'
    COMMAND:
        - sd_enable: to enable/disable the LDO 3.3V regulator that powers the SD module
                     use -po option to indicate the Pin.
        - sd_init: to initialize the sd card; (spi must be configured first)
                   create sd object and mounts as a filesystem, needs sdcard.py see
                   https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md#sd_init
        - sd_deinit: to unmount sd card
        - sd_auto: experimental command, needs a sd module with sd detection pin
                   and the SD_AM.py script. Enable an Interrupt
                   with the sd detection pin, so it mounts the sd when is detected,
                   and unmount the sd card when is extracted. See more info in:
                   https://github.com/Carglglz/upydev/blob/master/DOCS/Documentation.md#sd_auto



Prototype
----------

> PROTOTYPE: do '$ upydev pro' to see Prototype utils commands help.


> PROTOTYPE: Usage '$ upydev COMMAND [opts]'
    COMMAND:
        >INPUT
        Sensors:
            * ADC:
                ^ON BOARD ADCS:
                - adc_config : to config analog pin to read from (see pinout, -po and -att)
                - aread : to read from an analog pin previously configured

                ^EXTERNAL ADC: (I2C) ADS1115 ***
                - ads_init : to initialize and configure ADS1115 and the channel to
                            read from (see -ads, -ch)
                - ads_read : to read from analog pin previously configured
                        (see -tm option for stream mode, and -f for logging*)
                        * for one shot read, logging is also available with -f and
                            -n option (for tagging)
                        * use '-f now' for automatic 'log_mode_datetime.txt' name.
                        * for stream mode profiling use -tm [ms] -ads test
            * IMU:
                - imu_init : initialize IMU, use -imu option to indicate the imu library.
                            (default option is 'lsm9ds1', see sensor requirements for more info')
                - imuacc : one shot read of the IMU lineal accelerometer (g=-9.8m/s^2),
                        (see -tm option for stream mode, and -f for logging*)
                        * for one shot read, logging is also available with -f and
                            -n option (for tagging)
                        * use '-f now' for automatic 'log_mode_datetime.txt' name.
                        * for stream mode profiling use -tm [ms] -imu test
                        ** stream mode and logging are supported in imugy and imumag also
                - imuacc_sd: log the imuacc data to the sd (must be mounted)
                            with the file format 'log_mode_datetime.txt'
                            (see -tm option for stream mode)
                - imugy :  one shot read of the IMU gyroscope (deg/s)
                - imumag : one shot read of the IMU magnetometer (gauss)
            * WEATHER SENSOR: (BME280)
                - bme_init: initialize bme, use -bme option to indicate the weather sensor library.
                            (default option is 'bme280', see sensor requirements for more info')
                - bme_read : to read values from bme (Temp(C), Pressure(Pa), Rel.Hummidity (percentage))
                        (see -tm option for stream mode, and -f for logging*)
                        * for one shot read, logging is also available with -f and
                            -n option (for tagging)
                        * use '-f now' for automatic 'log_mode_datetime.txt' name.
                        * for stream mode profiling use -tm [ms] -bme test
            * POWER SENSOR: (INA219)
                - ina_init: initialize ina, use -ina option to indicate the power sensor library.
                            (default option is 'ina219', see sensor requirements for more info')
                - ina_read : to read values from ina (Pot.Diff (Volts), Current(mA), Power(mW))
                        (see -tm option for stream mode, and -f for logging*)
                        * for one shot read, logging is also available with -f and
                            -n option (for tagging)
                        * use '-f now' for automatic 'log_mode_datetime.txt' name.
                        * for stream mode profiling use -tm [ms] -ina test
                - ina_batt: Use the sensor to profile battery usage and estimate battery life left.
                            It will made 100 measurements during 5 seconds. Indicate battery capacity
                            with -batt option; (in mAh)

        >OUTPUT:
            * DAC:
                - dac_config: to config analog pin to write to (use -po option)
                - dac_write: to write a value in volts (0-3.3V)
                - dac_sig: to write a signal use -sig for different options:
                          > [type] [Amp] [frequency]
                            (type: 'sin, sq'; Amp 0-1 V ; fq:0-50 (above that fq loses quality))
                          > start : starts signal generation
                          > stop : stops signal
                          > mod [Amp] [frequency]: modify the signal with the Amp and fq indicated.
            * BUZZER:
                - buzz_config: to config PWM pin to drive the buzzer (use -po option)
                - buzz_set_alarm: to set an alarm at time indicated with option -at, be
                                 aware that the rtc time must be set first with set_localtime
                                 or set_ntptime
                - buzz_interrupt: to configure an interrupt with pins indicated with -po,
                                use -md 'rev' for interrupt reverse operation
                - buzz_beep: make the buzzer beep, with options set by -opt,
                            usage: buzz_beep -opt [beep_ms] [number_of_beeps] [time_between_beeps] [fq]
            * DC MOTOR:
                - dcmotor_config: to config PWM pins to drive a DC motor (use -po option as -po [DIR1] [DIR2])
                - dcmotor_move: to move the motor to one direction ['R'] or the opposite ['L']
                                use -to option as -to ['R' or 'L'] [VELOCITY] (60-512)
                - dcmotor_stop: to stop the DC motor
            * SERVO:
                - servo_config: to configure the servo pin with -po option
                - servo_angle: to move the servo an angle indicated by -opt option
            * STEPPER MOTOR:
                - stepper_config: to configure the step and direction pin with -po option
                                    *( -po [DIR_PIN] [STEP_PIN])
                - stepper_move: to move the stepper to right or left, at a velocity and
                               a numbers of steps indicated with -to option: [R or L] [velocity] [# steps]
                               R: right, L:left, velocity (1000-20000) (smaller is faster) and
                               # steps (int), where 200 steps means a complete lap

        NETWORKING:
            * MQTT:
                - mqtt_config: to set id, broker address, user and password, use with -client option
                               as "mqtt_config -client [ID] [BROKER ADDRESS] [USER] [PASSWORD]"
                - mqtt_conn: to start a mqtt client and connect to broker; use mqtt_config first
                - mqtt_sub: to subscribe to a topic, use -to option as "mqtt_sub -to [TOPIC]"
                - mqtt_pub: to publish to a topic, use -to option as "mqtt_pub -to [TOPIC] [PAYLOAD]" or
                            "mqtt_pub -to [PAYLOAD]" if already subscribed to a topic.
                - mqtt_check: to check for new messages of the subscribed topics.
            * SOCKETS:
                - socli_init: to initiate a socket client use with -server option as
                              "socli_init -server [IP] [PORT] [BUFFER LENGTH]"
                - socli_conn: to connect the socket client to a server (inidcated by IP)
                - socli_send: to send a message to the server, use -n option to indicate
                              the message
                - socli_recv: to receive a message from the server
                - socli_close: to close the client socket
                - sosrv_init: to initiate a socket server, use with -server option as
                              "sosrv_init -server [PORT] [BUFFER LENGTH]"
                - sosrv_start: to start the server, waits for a connection
                - sosrv_send: to send a message to the client, use -n option to indicate
                              the message
                - sosrv_recv: to receive a message from the client
                - sosrv_close: to close the server socket
            * UREQUEST:
                - rget_json: to make a request to API that returns a JSON response format
                            (indicate API URL with -f option)
                - rget_text: to make a request to API that returns a text response format
                            (indicate API URL with -f option)

        Port/board specific commands:
        - battery : if running on battery, gets battery voltage (esp32 huzzah feather)
        - pinout : to see the pinout reference/info of a board, indicated by -b option,
                   to request a single or a list of pins info use -po option
        - specs : to see the board specs, indicated by -b option
        - pin_status: to see pin state, to request a specific set use -po option ***

        * ESP32: (Not implemented yet)
            - touch
            - hall
            - deepsleep
            - temp
