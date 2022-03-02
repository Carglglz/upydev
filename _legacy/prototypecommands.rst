Prototype
----------


INPUT
^^^^^
Sensors
""""""""
ADC
****
    * ON BOARD ADC:
              - **adc_config**: to configure analog pin to read from (see pinout, ``-po`` and ``-att``)
              - **aread**: to read from an analog pin previously configured

    * EXTERNAL ADC: (I2C) ADS1115 [#]_
                - **ads_init**: to initialize and configure ADS1115 and the channel to read from (see ``-ads``, ``-ch``)
                - **ads_read**: to read from analog pin previously configured (see ``-tm`` option for stream mode, and ``-f`` for logging)

      .. note::

                  * for one shot read, logging is also available with ``-f`` and ``-n`` option (for tagging)
                  * use ``-f now`` for automatic ``log_mode_datetime.txt`` name.
                  * for stream mode profiling use ``-tm [ms] -ads test``.

      .. [#] These commands need ``init_ADS.py`` in the device.

IMU (LSM9DS1) [#]_
******************

    - **imu_init**: initialize IMU, use ``-imu`` option to indicate the imu library. Default option is ``lsm9ds1``. [#]_
    - **imuacc**: one shot read of the IMU lineal accelerometer (g=-9.8m/s^2), (see ``-tm`` option for stream mode, and ``-f`` for logging.

    .. note::
            * for one shot read, logging is also available with ``-f`` and ``-n`` option (for tagging)
            * use ``-f now`` for automatic ``log_mode_datetime.txt`` name.
            * for stream mode profiling use ``-tm [ms] -imu test``.

            *stream mode and logging are supported in* ``imugy`` *and* ``imumag`` *also*.

    - **imuacc_sd**: log the acceleration data to the sd (The sd must be mounted, see ``-tm`` option for stream mode)
    - **imugy** :  one shot read of the IMU gyroscope (deg/s)
    - **imumag** : one shot read of the IMU magnetometer (gauss)

      .. [#] These commands need ``init_IMU.py`` in the device.
      .. note::
            .. [#] **Sensor requirements**:
                The sensor class must have for Lineal Acceleration a ``read_accel()`` method, for Angular Acceleration a ``read_gyro()`` method,
                for Magnetic Field a ``read_magnet()`` method.



WEATHER SENSOR: (BME280) [#]_
*****************************

    - **bme_init**: initialise bme sensor, use ``-bme`` option to indicate the weather sensor library. (default option is ``bme280``) [#]_

    - **bme_read**: to read values from bme, Temperature (°C), Pressure (Pa) and Rel.Humidity (%). See ``-tm`` option for stream mode, and ``-f`` for logging.


    .. note::
                * for one shot read, logging is also available with ``-f`` and ``-n`` option (for tagging)
                * use ``-f now`` for automatic ``log_mode_datetime.txt`` name.
                * for stream mode profiling use ``-tm [ms] -bme test``.

    .. [#] These commands need ``init_IMU.py`` in the device.

    .. note::
          .. [#] **Sensor requirements**. The sensor class must have a ``read_compensated_data()`` method.

POWER SENSOR: (INA219) [#]_
***************************

    - **ina_init**: initialise ina, use ``-ina`` option to indicate the power sensor library. Default option is ``ina219``. [#]_

    - **ina_read**: to read values from ina, Pot.Diff (Volts), Current(mA) and Power(mW). See ``-tm`` option for stream mode, and ``-f`` for logging.

            .. note::
                        * for one shot read, logging is also available with ``-f`` and ``-n`` option (for tagging)
                        * use ``-f now`` for automatic ``log_mode_datetime.txt`` name.
                        * for stream mode profiling use ``-tm [ms] -ina test``.

    - **ina_batt**: Use the sensor to profile battery usage and estimate battery life left.It will made 100 measurements during 5 seconds. indicate battery capacity with ``-batt`` option (in mAh)


      .. [#] These commands need ``init_INA219.py`` in the device.

      .. note::
            .. [#] **Sensor requirements**. The sensor class must have a ``read_compensated_data()`` method.

OUTPUT
^^^^^^
DAC
"""
    - **dac_config** : to configure analog pin to write to (use ``-po`` option)
    - **dac_write**: to write a value in volts (0-3.3V)
    - **dac_sig**:
            to write a signal use ``-sig`` for different options.
              * ``[type] [Amp] [frequency]``, where ``[type]`` can be ``sin`` or ``sq``, ``[Amp]`` can be ``0-1`` Volts and ``[frequency]``: ``0-50`` Hz
              * ``start`` : starts signal generation
              * ``stop`` : stops signal
              * ``mod [Amp] [frequency]``: modify the signal with the Amp and fq indicated.

BUZZER
"""""""
    - **buzz_config**: to configure PWM pin to drive the buzzer (use ``-po`` option)

    - **buzz_set_alarm**: to set an alarm at time indicated with option ``-at``. [#]_


    - **buzz_interrupt**: to configure an interrupt with pins indicated with ``-po``, use ``-md rev`` for interrupt reverse operation

    - **buzz_beep**: make the buzzer beep, with options set by ``-opt``, e.g ``$ upydev buzz_beep -opt [beep_ms] [number_of_beeps] [time_between_beeps] [fq]``

    .. [#]  Be aware that the rtc time must be set first with ``set_localtime`` or ``set_ntptime``.

DC MOTOR
"""""""""

    - **dcmotor_config**: to configure PWM pins to drive a DC motor (use ``-po`` option as ``-po [DIR1] [DIR2]``)

    - **dcmotor_move**: to move the motor to one direction ['R'] or the opposite ['L'], use ``-to`` option as ``-to [R or L] [VELOCITY]`` where ``VELOCITY`` can be ``60-512``

    - **dcmotor_stop**: to stop the DC motor.

SERVO
"""""
    - **servo_config**: to configure the servo pin with ``-po`` option.

    - **servo_angle**: to move the servo an angle indicated by ``-opt`` option.

STEPPER MOTOR
""""""""""""""

    - **stepper_config**: to configure the step and direction pin with ``-po`` option as ``-po [DIR_PIN] [STEP_PIN]``

    - **stepper_move**: to move the stepper to right or left, at a velocity and a numbers of steps indicated with ``-to`` option: ``[R or L] [velocity] [# steps]`` [#]_

       .. [#] R: right, L:left, velocity (1000-20000) (smaller is faster) and # steps (int), where 200 steps means a complete lap

NETWORKING
^^^^^^^^^^

MQTT
"""""
        - **mqtt_config**: to set id, broker address, user and password, use with ``-client`` option as ``mqtt_config -client [ID] [BROKER ADDRESS] [USER] [PASSWORD]``

        - **mqtt_conn**: to start a mqtt client and connect to broker; use ``mqtt_config`` first

        - **mqtt_sub**: to subscribe to a topic, use ``-to`` option as ``mqtt_sub -to [TOPIC]``

        - **mqtt_pub**: to publish to a topic, use ``-to`` option as ``mqtt_pub -to [TOPIC] [PAYLOAD]`` or ``mqtt_pub -to [PAYLOAD]`` if already subscribed to a topic.

        - **mqtt_check**: to check for new messages of the subscribed topics.

SOCKETS
"""""""
        - **socli_init**: to initiate a socket client use with ``-server`` option as ``socli_init -server [IP] [PORT] [BUFFER LENGTH]``

        - **socli_conn**: to connect the socket client to a server (inidcated by IP)

        - **socli_send**: to send a message to the server, use ``-n`` option to indicate the message

        - **socli_recv**: to receive a message from the server

        - **socli_close**: to close the client socket

        - **sosrv_init**: to initiate a socket server, use with ``server`` option as ``sosrv_init -server [PORT] [BUFFER LENGTH]``

        - **sosrv_start**: to start the server, waits for a connection.

        - **sosrv_send**: to send a message to the client, use ``-n`` option to indicate the message.

        - **sosrv_recv**: to receive a message from the client.

        - **sosrv_close**: to close the server socket.

UREQUEST
""""""""
        - **rget_json**: to make a request to API that returns a JSON response format (indicate API URL with ``-f`` option)
        - **rget_text**: to make a request to API that returns a text response format (indicate API URL with ``-f`` option)


BOARD [#]_
^^^^^^^^^^
- **battery** : if running on battery, gets battery voltage

- **pinout** : to see the pinout reference/info of a board, indicated by ``-b`` option, to request a single or a list of pins info use ``-po`` option

- **specs**: to see the board specs, indicated by ``-b`` option.

- **pin_status**: to see pin state, to request a specific set use ``-po`` option.

.. [#] Esp32 Huzzah only at the moment.
