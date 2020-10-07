from upydevice import Device, DeviceException
from upydev.commandlib import _CMDDICT_
import sys

KEY_N_ARGS = {'du': ['f', 's'], 'df': ['s'], 'netstat_conn': ['wp'],
              'apconfig': ['ap'], 'i2c_config': ['i2c'],
              'spi_config': ['spi'], 'set_ntptime': ['utc']}

VALS_N_ARGS = ['f', 's', 'wp', 'ap', 'i2c', 'spi', 'utc']

ATTEN_DICT = {0: 'ADC.ATTN_0DB', 1: 'ADC.ATTN_2_5DB', 2: 'ADC.ATTN_6DB',
              3: 'ADC.ATTN_11DB'}
ATTEN_INFO = """
0 = ADC.ATTN_0DB: 0dB attenuation, gives a maximum input voltage of 1.00v
1 = ADC.ATTN_2_5DB: 2.5dB attenuation, gives a maximum input voltage of approximately 1.34v
2 = ADC.ATTN_6DB: 6dB attenuation, gives a maximum input voltage of approximately 2.00v
3 = ADC.ATTN_11DB: 11dB attenuation, gives a maximum input voltage of approximately 3.6v
"""

PROTOTYPE_COMMANDS_HELP = """
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
"""


def prototype_command(cmd, *args, **kargs):
    if cmd == 'pro':
        print(PROTOTYPE_COMMANDS_HELP)
