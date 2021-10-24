from upydevice import Device, DeviceException
import sys
import socket
import struct
import time
from datetime import datetime
import netifaces
import json
import os
import upydev


KEY_N_ARGS = {'du': ['f', 's'], 'df': ['s'], 'netstat_conn': ['wp'],
              'apconfig': ['ap'], 'i2c_config': ['i2c'],
              'spi_config': ['spi'], 'set_ntptime': ['utc']}

VALS_N_ARGS = ['f', 's', 'wp', 'ap', 'i2c', 'spi', 'utc']

ADC_PINS_DICT = {'esp32h': [i for i in range(32, 40)]}

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


# def run_command_rl(command):
#     end = False
#     lines = []
#     process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
#     while end is not True:
#         if process.poll() is None:
#             output = process.stdout.readline()
#             if output == '' and process.poll() is not None:
#                 break
#             if output:
#                 line = output.strip().decode()
#                 lines.append(line)
#                 if output.strip() == b'### closed ###':
#                     end = True
#         else:
#             break
#     rc = process.poll()
#     return rc, lines


def get_ip():
    try:
        ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_soc.connect(('8.8.8.8', 1))
        local_ip = ip_soc.getsockname()[0]
        ip_soc.close()
        return local_ip
    except Exception as e:
        return [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for
                iface in netifaces.interfaces() if netifaces.AF_INET in
                netifaces.ifaddresses(iface)][-1]


def get_live_stream(args, run_cmd, dev, sensorlib, filename=None,
                    r_format='fff', nb=12, log=False, variables=None):
    if args.lh is None:
        local_ip = get_ip()
    if args.lh is not None:
        local_ip = args.lh

    # START A LOCAL SERVER
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_ip, 8005))
    server_socket.listen(1)
    dev.wr_cmd('{}.connect_SOC({})'.format(sensorlib, "'{}'".format(
                                                 local_ip)), silent=True, follow=False)
    # dev.disconnect()
    conn, addr = server_socket.accept()
    conn.settimeout(1)
    flushed = 0
    while flushed == 0:
        try:
            conn.recv(1024)
        except Exception as e:
            flushed = 1
    if args.tm > 500:
        conn.settimeout((args.tm/1000)*3)  # for long periodic shots
    dev.wr_cmd(run_cmd, silent=True, follow=False)
    print(('{:^15}'*len(variables)).format(*variables))
    try:
        if log:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      struct.unpack(r_format, data_acc)))
                    decode_print = dict(zip(variables,
                                            [format(val, '.4f') for val in struct.unpack(r_format, data_acc)]))
                    sys.stdout.write("\033[K")
                    print(('{:^15}'*len(decode_print.values())
                           ).format(*decode_print.values()), end='\r')
                    sys.stdout.flush()
                    with open(filename, 'a') as logfile:
                        logfile.write(json.dumps(decode))
                        logfile.write('\n')
                except Exception as e:
                    print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break
        else:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      [format(val, '.4f') for val in struct.unpack(r_format, data_acc)]))
                    sys.stdout.write("\033[K")
                    print(('{:^15}'*len(decode.values())
                           ).format(*decode.values()), end='\r')
                    sys.stdout.flush()
                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break

    except KeyboardInterrupt:
        try:
            print('\n')
            print('...closing...')
            conn.shutdown(socket.SHUT_RDWR)
            time.sleep(1)
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            print('Done!')
            conn.close()
        except KeyboardInterrupt:
            print('...wait for closing...')
            conn.shutdown(socket.SHUT_RDWR)
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            time.sleep(1)
            conn.close()
            print('Done!')
        dev.disconnect()


def test_stream(args, run_cmd, dev, sensorlib, filename=None,
                r_format='fff', nb=12, log=False, variables=None, BUFFERSIZE=1):
    if args.lh is None:
        local_ip = get_ip()
    if args.lh is not None:
        local_ip = args.lh

    # START A LOCAL SERVER
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_ip, 8005))
    server_socket.listen(1)
    dev.wr_cmd('{}.connect_SOC({})'.format(sensorlib, "'{}'".format(
                                                 local_ip)), silent=True, follow=False)
    conn, addr = server_socket.accept()
    conn.settimeout(1)
    flushed = 0
    while flushed == 0:
        try:
            conn.recv(1024)
        except Exception as e:
            flushed = 1
    if args.tm > 500:
        conn.settimeout((args.tm/1000)*3)  # for long periodic shots
    dev.wr_cmd(run_cmd, silent=True, follow=False)
    print(('{:^15}'*len(variables)).format(*variables))
    t0 = time.time()
    test_val = []
    try:
        if log:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      struct.unpack(r_format, data_acc)))
                    decode_print = dict(zip(variables,
                                            [format(val, '.4f') for val in struct.unpack(r_format, data_acc)]))
                    sys.stdout.write("\033[K")
                    print(('{:^15}'*len(decode_print.values())
                           ).format(*decode_print.values()), end='\r')
                    sys.stdout.flush()
                    with open(filename, 'a') as logfile:
                        logfile.write(json.dumps(decode))
                        logfile.write('\n')
                except Exception as e:
                    print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break
        else:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      struct.unpack(r_format, data_acc)))
                    decode_p = dict(zip(variables,
                                        [format(val, '.4f') for val in struct.unpack(r_format, data_acc)]))
                    sys.stdout.write("\033[K")
                    print(('{:^15}'*len(decode_p.values())
                           ).format(*decode_p.values()), end='\r')
                    sys.stdout.flush()
                    test_val.append(decode)
                    if t0 == 0:
                        t0 = time.time()

                    final_time = abs(time.time()-t0)
                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break

    except KeyboardInterrupt:
        try:
            print('\n')
            print('...closing...')
            conn.shutdown(socket.SHUT_RDWR)
            time.sleep(1)
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            print('Done!')
            print('TEST RESULTS ARE:')
            print('TEST DURATION : {} (s)'.format(final_time))
            # # FIND SAMPLING RATE
            # Method 1:
            N_DATA_PACKETS = len(test_val)  # Number of batches received
            print('DATA PACKETS : {} packets'.format(N_DATA_PACKETS))
            # (assuming al batches = buffer_size long)
            Fs = ((N_DATA_PACKETS+1)*BUFFERSIZE/final_time)
            print('SAMPLES PER PACKET : {}'.format(BUFFERSIZE))
            print('VARIABLES PER SAMPLE : {}; {}'.format(
                len(variables), variables))
            print('SIZE OF PACKETS: {} bytes'.format(nb))
            #  32 is batch/buffer size ,
            # so total samples is n_batches (len(vals)) x size_batch
            # print('Period: {} ms ; Fs:{} Hz'.format(
            # timestamp[:].mean()/1e3,1/((timestamp[:].mean())/1e6))
            conn.close()
            print('Period: {} ms ; Fs:{} Hz, Data send rate: {} packets/s of {} samples'.format(
                round((1/Fs)*1e3), round(Fs, -1),
                round(N_DATA_PACKETS/final_time), BUFFERSIZE))
            print(
                'DATA TRANSFER RATE: {} KB/s'.format(round(N_DATA_PACKETS/final_time)*nb/1024))
        except KeyboardInterrupt:
            conn.shutdown(socket.SHUT_RDWR)
            print('...wait for closing...')
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            time.sleep(1)
            conn.close()
            print('Done!')
        dev.disconnect()


def get_live_stream_chunk(args, run_cmd, dev, sensorlib, filename=None,
                          r_format='h'*20, nb=40, log=False, variables=None):
    if args.lh is None:
        local_ip = get_ip()
    if args.lh is not None:
        local_ip = args.lh

    # START A LOCAL SERVER
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_ip, 8005))
    server_socket.listen(1)
    dev.wr_cmd('{}.connect_SOC({})'.format(sensorlib, "'{}'".format(
                                                 local_ip)), silent=True, follow=False)
    conn, addr = server_socket.accept()
    conn.settimeout(1)
    flushed = 0
    while flushed == 0:
        try:
            conn.recv(1024)
        except Exception as e:
            flushed = 1
    if args.tm > 500:
        conn.settimeout((args.tm/1000)*3)  # for long periodic shots
    dev.wr_cmd(run_cmd, silent=True)
    time.sleep(0.5)
    print(('{:^15}'*len(variables)).format(*variables))
    try:
        if log:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      [struct.unpack(r_format, data_acc)]))
                    # print(decode)
                    for chunk in decode.values():
                        value = sum([val for val in chunk])/len(chunk)
                        sys.stdout.write("\033[K")
                        decode_p = dict(zip(variables,
                                            [format(value, '.4f')]))
                        print(('{:^15}'*len(decode_p.values())
                               ).format(*decode_p.values()), end='\r')
                        sys.stdout.flush()
                    with open(filename, 'a') as logfile:
                        logfile.write(json.dumps(decode))
                        logfile.write('\n')
                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break
        else:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      [struct.unpack(r_format, data_acc)]))
                    # print(decode)
                    for chunk in decode.values():
                        value = sum([val for val in chunk])/len(chunk)
                        sys.stdout.write("\033[K")
                        decode_p = dict(zip(variables,
                                            [format(value, '.4f')]))
                        print(('{:^15}'*len(decode_p.values())
                               ).format(*decode_p.values()), end='\r')
                        sys.stdout.flush()
                        # print(dict(zip(variables, [value])))

                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        print(e)
                        break

    except KeyboardInterrupt:
        try:
            print('\n')
            print('...closing...')
            conn.shutdown(socket.SHUT_RDWR)
            time.sleep(1)
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            print('Done!')
            conn.close()
        except KeyboardInterrupt:
            conn.shutdown(socket.SHUT_RDWR)
            print('...wait for closing...')
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            time.sleep(1)
            conn.close()
            print('Done!')
        dev.disconnect()


def test_stream_chunk(args, run_cmd, dev, sensorlib, filename=None,
                      r_format='h'*20, nb=40, log=False, variables=None, BUFFERSIZE=20):
    if args.lh is None:
        local_ip = get_ip()
    if args.lh is not None:
        local_ip = args.lh

    # START A LOCAL SERVER
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_ip, 8005))
    server_socket.listen(1)
    dev.wr_cmd('{}.connect_SOC({})'.format(sensorlib, "'{}'".format(
                                                 local_ip)), silent=True, follow=False)
    conn, addr = server_socket.accept()
    conn.settimeout(1)
    flushed = 0
    while flushed == 0:
        try:
            conn.recv(1024)
        except Exception as e:
            flushed = 1
    if args.tm > 500:
        conn.settimeout((args.tm/1000)*3)  # for long periodic shots
    dev.wr_cmd(run_cmd, silent=True)
    time.sleep(0.5)
    t0 = time.time()
    test_val = []
    print(('{:^15}'*len(variables)).format(*variables))
    try:
        if log:
            while True:
                try:
                    data_acc = conn.recv(nb)
                    decode = dict(zip(variables,
                                      [struct.unpack(r_format, data_acc)]))
                    # print(decode)
                    for chunk in decode.values():
                        value = sum([val for val in chunk])/len(chunk)
                        sys.stdout.write("\033[K")
                        decode_p = dict(zip(variables,
                                            [format(value, '.4f')]))
                        print(('{:^15}'*len(decode_p.values())
                               ).format(*decode_p.values()), end='\r')
                        sys.stdout.flush()
                    with open(filename, 'a') as logfile:
                        logfile.write(json.dumps(decode))
                        logfile.write('\n')
                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break
        else:
            while True:
                try:
                    data_recv = conn.recv(nb)
                    decode = dict(zip(variables,
                                      [struct.unpack(r_format, data_recv)]))
                    # print(decode)
                    for chunk in decode.values():
                        value = sum([val for val in chunk])/len(chunk)
                        sys.stdout.write("\033[K")
                        decode_p = dict(zip(variables,
                                            [format(value, '.4f')]))
                        print(('{:^15}'*len(decode_p.values())
                               ).format(*decode_p.values()), end='\r')
                        sys.stdout.flush()
                    test_val.append(decode)
                    if t0 == 0:
                        t0 = time.time()

                    final_time = abs(time.time()-t0)
                except Exception as e:
                    # print(e)
                    if str(e) == 'timed out':
                        pass
                    else:
                        break

    except KeyboardInterrupt:
        try:
            print('\n')
            print('...closing...')
            conn.shutdown(socket.SHUT_RDWR)
            time.sleep(1)
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            print('Done!')
            print('TEST RESULTS ARE:')
            print('TEST DURATION : {} (s)'.format(final_time))
            # # FIND SAMPLING RATE
            # Method 1:
            N_DATA_PACKETS = len(test_val)  # Number of batches received
            print('DATA PACKETS : {} packets'.format(N_DATA_PACKETS))
            # (assuming al batches = buffer_size long)
            Fs = ((N_DATA_PACKETS+1)*BUFFERSIZE/final_time)
            print('SAMPLES PER PACKET : {}'.format(BUFFERSIZE))
            print('VARIABLES PER SAMPLE : {}; {}'.format(
                len(variables), variables))
            print('SIZE OF PACKETS: {} bytes'.format(nb))
            #  32 is batch/buffer size ,
            # so total samples is n_batches (len(vals)) x size_batch
            # print('Period: {} ms ; Fs:{} Hz'.format(
            # timestamp[:].mean()/1e3,1/((timestamp[:].mean())/1e6))
            conn.close()
            print('Period: {} ms ; Fs:{} Hz, Data send rate: {} packets/s of {} samples'.format(
                round((1/Fs)*1e3), round(Fs, -1),
                round(N_DATA_PACKETS/final_time), BUFFERSIZE))
            print(
                'DATA TRANSFER RATE: {} KB/s'.format(round(N_DATA_PACKETS/final_time)*nb/1024))
        except KeyboardInterrupt:
            conn.shutdown(socket.SHUT_RDWR)
            print('...wait for closing...')
            # Flush error keyboardinterrupt
            cmd = '{}.stop_send();gc.collect()'.format(sensorlib)
            dev.wr_cmd(cmd, silent=True)
            time.sleep(1)
            conn.close()
            print('Done!')

        dev.disconnect()


# LOGGING DATETIME NOW:
def lognow(filename, sensor):
    if filename == 'now':
        return 'log_{}_{}.txt'.format(sensor,
                                      datetime.now().strftime("%m_%d_%Y_%H_%M_%S"))
    else:
        return filename


def prototype_command(args, **kargs):
    if args.m == 'pro':
        print(PROTOTYPE_COMMANDS_HELP)

    #############################################
    # SENSOR SPECIFIC COMMANDS

    #  * ADC *

    # ADC CONFIG
    # dev_name = kargs.get('device')
    # dt = check_device_type(args.t)
    elif args.m == 'adc_config':
        if args.att == 'info':
            print(ATTEN_INFO)
        else:
            if args.b is not None:
                print('Available ADC pins for {} board are : {}'.format(
                    args.b, ADC_PINS_DICT[args.b]))
            else:
                adc_pin = args.po[0]
                analog_cmd = "from machine import ADC,Pin;analog_pin = ADC(Pin({}));".format(
                    adc_pin)
                analog_atten = "analog_pin.atten({});gc.collect()".format(
                    ATTEN_DICT[int(args.att)])
                adc_cmd = analog_cmd + analog_atten
                dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
                dev.wr_cmd(adc_cmd)
                dev.disconnect()
                print('Pin {} configured as Analog Input with {} attenuation'.format(
                    adc_pin, ATTEN_DICT[int(args.att)][4:]))
            sys.exit()

    # ADC READ
    elif args.m == 'aread':
        adc_cmd = "((analog_pin.read())/4095)*3.6;gc.collect()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        analog_info = dev.wr_cmd(adc_cmd, silent=True, rtn_resp=True)
        dev.disconnect()
        if analog_info:
            volts = analog_info
            print('Volts: {}'.format(volts))
        sys.exit()

    # * ADS *
    # ADS_INIT
    elif args.m == 'ads_init':
        ads_lib = args.ads
        import_ads_cmd = "from {} import {};import init_ADS as ads;".format(
            args.ads, args.ads.upper())
        print('Initialazing ads...')
        ads_init_cmd = "my_ads = ads.MY_ADS({},ads.i2c,None,channel={});".format(
            args.ads.upper(), args.ch)
        if args.i2c != [22, 23]:
            ads_init_cmd = "{};my_ads = ads.MY_ADS({},{},None,channel={});".format(
                'from machine import I2C', args.ads.upper(), 'I2C(scl=Pin({}), sda=Pin({}))'.format(*args.i2c), args.ch)
        ads_final_init = "my_ads.init();gc.collect()"
        ads_init_cmd_str = import_ads_cmd + ads_init_cmd + ads_final_init
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

        dev.wr_cmd(ads_init_cmd_str)
        dev.disconnect()
        sys.exit()

    # ADS_READ
    elif args.m == 'ads_read':
        if args.tm is None:
            ads_cmd = "my_ads.read_V();"
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            ads_info = dev.wr_cmd(ads_cmd, silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
            dev.disconnect()
            if ads_info:
                my_read = round(ads_info, 2)
                print('{} V'.format(my_read))
                if args.f is not None:
                    data_shot = [my_read]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {'VAR': ['V', 'TS'], 'UNIT': 'Volts'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))

        elif args.ads == 'test':
            stream_ads = "my_ads.start_send(my_ads.chunk_send_V,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            ch = dev.wr_cmd('my_ads.channel', silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            # dev.disconnect()
            print('Streaming ADS: A{} (voltage),fq={}Hz'.format(ch, fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['V'], 'UNIT': 'VOLTS',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                test_stream_chunk(args, stream_ads, dev, 'my_ads',
                                  filename=args.f, log=True,
                                  r_format='f'*20, nb=80, variables=header['VAR'])
            else:
                header = {'VAR': ['V'], 'UNIT': 'VOLTS',
                          'fq(hz)': fq}
                test_stream_chunk(args, stream_ads, dev, 'my_ads',
                                  variables=header['VAR'], r_format='f'*20, nb=80)
        else:
            # Do connect
            stream_ads = "my_ads.start_send(my_ads.chunk_send_V,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            ch = dev.wr_cmd('my_ads.channel', silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            # dev.disconnect()
            print('Streaming ADS: A{} (voltage),fq={}Hz'.format(ch, fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['V'], 'UNIT': 'VOLTS',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream_chunk(args, stream_ads, dev, 'my_ads',
                                      filename=args.f, log=True,
                                      r_format='f'*20, nb=80, variables=header['VAR'])
            else:
                header = {'VAR': ['V'], 'UNIT': 'VOLTS',
                          'fq(hz)': fq}
                get_live_stream_chunk(args, stream_ads, dev, 'my_ads',
                                      variables=header['VAR'], r_format='f'*20, nb=80)
        sys.exit()
    # * IMU *
    # IMU_INIT

    elif args.m == 'imu_init':
        imu_lib = args.imu
        import_imu_cmd = "from {} import {};import init_IMU as imu;".format(
            args.imu, args.imu.upper())
        print('Initialazing imu...')
        imu_init_cmd = "my_imu = imu.MY_IMU({},imu.i2c,None);".format(
            args.imu.upper())
        if args.i2c != [22, 23]:
            imu_init_cmd = "{};my_imu = imu.MY_IMU({},{},None);".format(
                'from machine import I2C', args.imu.upper(), 'I2C(scl=Pin({}), sda=Pin({}))'.format(*args.i2c))
        imu_final_init = "my_imu.init()"
        imu_init_cmd_str = import_imu_cmd + imu_init_cmd + imu_final_init
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(imu_init_cmd_str)
        dev.disconnect()
        sys.exit()

    #  IMUACC

    elif args.m == 'imuacc':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.tm is None:
            imu_cmd = "my_imu.read_acc()"
            # dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            imu_info = dev.wr_cmd(imu_cmd, silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)

            dev.disconnect()
            if imu_info:
                print('X:{},Y:{},Z:{}'.format(*imu_info))
                if args.f is not None:
                    data_shot = [*imu_info]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {'VAR': ['X', 'Y', 'Z', 'TS'], 'UNIT': 'g=-9.8m/s^2'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))
        elif args.imu == 'test':
            # Do connect
            stream_acc = "my_imu.start_send(my_imu.sample_send_acc,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_imu", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming IMU ACCELEROMETER: X, Y, Z (g=-9.8m/s^2),fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                test_stream(args, stream_acc, dev, 'my_imu',
                            filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                          'fq(hz)': fq}
                test_stream(args, stream_acc, dev, 'my_imu',
                            variables=header['VAR'])

        else:
            # Do connect
            stream_acc = "my_imu.start_send(my_imu.sample_send_acc,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            dev.wr_cmd("my_imu", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            fq = 1/(args.tm/1000)
            print('Streaming IMU ACCELEROMETER: X, Y, Z (g=-9.8m/s^2),fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream(args, stream_acc, dev, 'my_imu',
                                filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                          'fq(hz)': fq}
                get_live_stream(args, stream_acc, dev, 'my_imu',
                                variables=header['VAR'])

        sys.exit()

    # IMUACC SD
    elif args.m == 'imuacc_sd':
        # Do connect
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        fq = 1/(args.tm/1000)
        header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                  'fq(hz)': fq}
        stream_acc = "my_imu.start_send_SD(my_imu.sample_send_acc_SD,'ACC','{}',timeout={})".format(
            header['UNIT'], args.tm)
        # run_live(stream_acc, args.t, args.p)
        # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
        dev.wr_cmd("my_imu", silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
                dev.disconnect()
                sys.exit()
        print('Streaming IMU ACCELEROMETER: X, Y, Z (g=-9.8m/s^2),fq={}Hz'.format(fq))
        get_live_stream(args, stream_acc, dev, 'my_imu',
                        variables=header['VAR'])
    # IMUGY

    elif args.m == 'imugy':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.tm is None:
            imu_cmd = "my_imu.read_gy()"
            # dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            imu_info = dev.wr_cmd(imu_cmd, silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
            dev.disconnect()
            if imu_info:
                print('X:{},Y:{},Z:{}'.format(*imu_info))
                if args.f is not None:
                    data_shot = [*imu_info]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {'VAR': ['X', 'Y', 'Z', 'TS'], 'UNIT': 'deg/s'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))
        else:
            # Do connect
            stream_ = "my_imu.start_send(my_imu.sample_send_gy,timeout={})".format(
                args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_imu", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming IMU GYRO: X, Y, Z (deg/s),fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'deg/s',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream(args, stream_, dev, 'my_imu',
                                filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'deg/s',
                          'fq(hz)': fq}
                get_live_stream(args, stream_, dev, 'my_imu',
                                variables=header['VAR'])

        sys.exit()

    # IMUMAG

    elif args.m == 'imumag':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.tm is None:
            imu_cmd = "my_imu.read_mag()"
            # dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            imu_info = dev.wr_cmd(imu_cmd, silent=True, rtn_resp=True)

            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)

            dev.disconnect()
            if imu_info:
                print('X:{},Y:{},Z:{}'.format(*imu_info))
                if args.f is not None:
                    data_shot = [*imu_info]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {'VAR': ['X', 'Y', 'Z', 'TS'], 'UNIT': 'gauss'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))
        else:
            # Do connect
            stream_ = "my_imu.start_send(my_imu.sample_send_mag,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_imu", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming IMU MAGNETOMETER: X, Y, Z (gauss),fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'gauss',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream(args, stream_, dev, 'my_imu',
                                filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'gauss',
                          'fq(hz)': fq}
                get_live_stream(args, stream_, dev, 'my_imu',
                                variables=header['VAR'])

        sys.exit()

    # * BME280 *
    # BME_INIT

    elif args.m == 'bme_init':
        bme_lib = args.bme
        import_bme_cmd = "from {} import {};import init_BME280 as bme280;".format(
            args.bme, args.bme.upper())
        print('Initialazing bme280...')
        bme_init_cmd = "my_bme = bme280.MY_BME280({},bme280.i2c);".format(
            args.bme.upper())
        if args.i2c != [22, 23]:
            bme_init_cmd = "{};my_bme = bme280.MY_BME280({},{});".format(
                'from machine import I2C', args.bme.upper(), 'I2C(scl=Pin({}), sda=Pin({}))'.format(*args.i2c))
        bme_final_init = "my_bme.init()"
        bme_init_cmd_str = import_bme_cmd + bme_init_cmd + bme_final_init
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

        dev.wr_cmd(bme_init_cmd_str)
        dev.disconnect()
        sys.exit()

    #  BME_READ

    elif args.m == 'bme_read':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.tm is None:
            bme_cmd = "my_bme.read_values()"
            # dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            bme_info = dev.wr_cmd(bme_cmd, silent=True, rtn_resp=True)
            dev.wr_cmd("my_bme", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)

            dev.disconnect()
            if bme_info:
                print('{} C, {} Pa , {} % RH '.format(*bme_info))
                if args.f is not None:
                    data_shot = [*bme_info]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {
                        'VAR': ['Temp(C)', 'Pressure(Pa)', 'RH(%)', 'TS'], 'UNIT': 'T: C; P: Pa; RH: %'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))
        elif args.bme == 'test':
            # Do connect
            stream_bme = "my_bme.start_send(my_bme.sample_send_data,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_bme", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming BME280: Temp (C), Pressure (Pa), Rel. Hummidity (%) ,fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['Temp(C)', 'Pressure(Pa)', 'RH(%)', 'TS'], 'UNIT': 'T: C; P: Pa; RH: %',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                test_stream(args, stream_bme, dev, 'my_bme',
                            filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['Temp(C)', 'Pressure(Pa)', 'RH(%)', 'TS'], 'UNIT': 'T: C; P: Pa; RH: %',
                          'fq(hz)': fq}
                test_stream(args, stream_bme, dev, 'my_bme',
                            variables=header['VAR'])

        else:
            # Do connect
            stream_bme = "my_bme.start_send(my_bme.sample_send_data,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_bme", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming BME280: Temp (C), Pressure (Pa), Rel. Hummidity (%) ,fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['Temp(C)', 'Pressure(Pa)', 'RH(%)'], 'UNIT': 'T: C; P: Pa; RH: %',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream(args, stream_bme, dev, 'my_bme',
                                filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['Temp(C)', 'Pressure(Pa)', 'RH(%)'], 'UNIT': 'T: C; P: Pa; RH: %',
                          'fq(hz)': fq}
                get_live_stream(args, stream_bme, dev, 'my_bme',
                                variables=header['VAR'])

        sys.exit()

    # * INA219 *
    # INA_INIT

    elif args.m == 'ina_init':
        ina_lib = args.ina
        import_ina_cmd = "from {} import {};import init_INA219 as ina219;".format(
            args.ina, args.ina.upper())
        print('Initialazing ina219...')
        ina_init_cmd = "my_ina = ina219.MY_INA219({},ina219.i2c);".format(
            args.ina.upper())
        if args.i2c != [22, 23]:
            ina_init_cmd = "{};my_ina = ina219.MY_INA219({},{});".format(
                'from machine import I2C', args.ina.upper(), 'I2C(scl=Pin({}), sda=Pin({}))'.format(*args.i2c))
        ina_final_init = "my_ina.init()"
        ina_init_cmd_str = import_ina_cmd + ina_init_cmd + ina_final_init
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(ina_init_cmd_str)
        dev.disconnect()
        sys.exit()

    #  INA_READ

    elif args.m == 'ina_read':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.tm is None:
            ina_cmd = "my_ina.read_values()"
            # dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

            ina_info = dev.wr_cmd(ina_cmd, silent=True, rtn_resp=True)
            dev.wr_cmd("my_ina", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)

            dev.disconnect()
            if ina_info:
                print('{} V, {} mA , {} mW '.format(*ina_info))
                if args.f is not None:
                    data_shot = [*ina_info]
                    tag_tstamp = datetime.now().strftime("%H:%M:%S")
                    time_stamp = tag_tstamp
                    if args.n is not None:
                        tag_tstamp = args.n
                    data_shot.append(tag_tstamp)
                    header = {'VAR': [
                        'Voltage(V)', 'Current(mA)', 'Power(mW)', 'TS'], 'UNIT': 'V: v; C: mA; P: mW'}
                    if args.f not in os.listdir():
                        with open(args.f, 'w') as file_log:
                            file_log.write(json.dumps(header))
                            file_log.write('\n')
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    else:
                        with open(args.f, 'a') as file_log:
                            file_log.write(json.dumps(dict(zip(header['VAR'],
                                                               data_shot))))
                            file_log.write('\n')
                    print('Logged at {}'.format(time_stamp))
        elif args.ina == 'test':
            # Do connect
            stream_ina = "my_ina.start_send(my_ina.sample_send_data,timeout={})".format(
                args.tm)
            # run_live(stream_acc, args.t, args.p)
            # "imu.stream_acc(soc=cli_soc, timeout={})".format(args.tm)
            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_ina", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming ina219: Volts (V), Current (mA), Power (mW) ,fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['Voltage(V)', 'Current(mA)', 'Power(mW)'], 'UNIT': 'V: v; C: mA; P: mW',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                test_stream(args, stream_ina, dev, 'my_ina',
                            filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['Voltage(V)', 'Current(mA)', 'Power(mW)'], 'UNIT': 'V: v; C: mA; P: mW',
                          'fq(hz)': fq}
                test_stream(args, stream_ina, dev, 'my_ina',
                            variables=header['VAR'])

        else:
            # Do connect
            stream_ina = "my_ina.start_send(my_ina.sample_send_data,timeout={})".format(
                args.tm)

            fq = 1/(args.tm/1000)
            dev.wr_cmd("my_ina", silent=True, rtn_resp=True)
            if dev._traceback.decode() in dev.response:
                try:
                    raise DeviceException(dev.response)
                except Exception as e:
                    print(e)
                    dev.disconnect()
                    sys.exit()
            print('Streaming ina219: Volts (V), Current (mA), Power (mW) ,fq={}Hz'.format(fq))
            if args.f is not None:
                args.f = lognow(args.f, args.m)
                print('Saving file {} ...'.format(args.f))
                header = {'VAR': ['Voltage(V)', 'Current(mA)', 'Power(mW)'], 'UNIT': 'V: v; C: mA; P: mW',
                          'fq(hz)': fq}
                with open(args.f, 'w') as file_log:
                    file_log.write(json.dumps(header))
                    file_log.write('\n')
                get_live_stream(args, stream_ina, dev, 'my_ina',
                                filename=args.f, log=True, variables=header['VAR'])
            else:
                header = {'VAR': ['Voltage(V)', 'Current(mA)', 'Power(mW)'], 'UNIT': 'V: v; C: mA; P: mW',
                          'fq(hz)': fq}
                get_live_stream(args, stream_ina, dev, 'my_ina',
                                variables=header['VAR'])

        sys.exit()

    # INA_BATT
    elif args.m == 'ina_batt':
        print('\n')
        print(' {:>15}'.format('Battery Life expectancy profiling... '))
        ina_cmd = "my_ina.batt_ts_raw()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

        ina_info = dev.wr_cmd(ina_cmd, silent=True, rtn_resp=True)
        if dev._traceback.decode() in dev.response:
            try:
                raise DeviceException(dev.response)
            except Exception as e:
                print(e)
        dev.disconnect()
        if ina_info:
            volts_v, current_v, power_v = ina_info['V'], ina_info['C'], ina_info['P']
            volts = sum(volts_v)/len(volts_v)
            current = sum(current_v)/len(current_v)
            power = sum(power_v)/len(power_v)
            print('\n')
            print('{0:^15} {1:^15}'.format(
                '', '{}  {:>15}  {:>15}'.format('VOLTAGE', 'CURRENT', 'POWER')))
            print('  {0:>15}'.format('='*60))
            print('{0:^15} {1:^15}'.format('| Average |',
                                           '{:.2f} V {:>15.2f} mA  {:>15.2f} mW '.format(volts, current, power)))
            print('{0:^15}'.format('-'*len('| Average |')))
            print('{0:^15} {1:^15}'.format('|   MAX   |', '{:.2f} V {:>15.2f} mA  {:>15.2f} mW '.format(
                max(volts_v), max(current_v), max(power_v))))
            print('{0:^15}'.format('-'*len('| Average |')))
            print('{0:^15} {1:^15}'.format('|   MIN   |', '{:.2f} V {:>15.2f} mA  {:>15.2f} mW '.format(
                min(volts_v), min(current_v), min(power_v))))
            print('{0:^15}'.format('-'*len('| Average |')))
            print('\n')
            if current > 0:
                state = 'Discharging'
            else:
                state = 'Charging'
            percentage = round((volts-3.3)/(4.23-3.4)*100, 1)
            batt_le_full = (args.batt[0]/current)*0.70
            batt_le_now = round((batt_le_full * percentage)/100, 2)
            header = ' | {0:^15} | {1:^15} | {2:^15} | {3:^15} | {4:^20}  |'.format(
                'CAPACITY (mAh)', 'VOLTAGE (V)', 'LEVEL (%)', 'STATE', 'TIME LEFT (Hours)')
            print('  {0:^15}   {1:^15}   {2:^15}   {3:^15}   {4:^20}  '.format(
                '', '', 'BATTERY INFO', '', ''))
            print(' {0:>15}'.format('='*(len(header)-1)))
            print(header)
            print(' {0:>15}'.format('-'*(len(header)-1)))
            # print('| {0:^15} | {1:^15} | {2:^15} | {3:^15} | {4:^20} |'.format('', '', '', '', ''))
            print(' | {0:^15} | {1:^15.2f} | {2:^15} | {3:^15} | {4:^20}  |'.format(
                args.batt[0], volts, percentage, state, batt_le_now))
            # print('| {0:^15} | {1:^15} | {2:^15} | {3:^15} | {4:^20} |'.format('', '', '', '', ''))
            # print(' {0:>15}'.format('='*len(header)))
            print('\n')
            # if args.f is not None:
            #     data_shot = [*ast.literal_eval(ina_info_list[0])]
            #     tag_tstamp = datetime.now().strftime("%H:%M:%S")
            #     time_stamp = tag_tstamp
            #     if args.n is not None:
            #         tag_tstamp = args.n
            #     data_shot.append(tag_tstamp)
            #     header = {'VAR': ['Voltage(V)', 'Current(mA)', 'Power(mW)', 'TS'], 'UNIT': 'V: v; C: mA; P: mW'}
            #     if args.f not in os.listdir():
            #         with open(args.f, 'w') as file_log:
            #             file_log.write(json.dumps(header))
            #             file_log.write('\n')
            #             file_log.write(json.dumps(dict(zip(header['VAR'],
            #                                                data_shot))))
            #             file_log.write('\n')
            #     else:
            #         with open(args.f, 'a') as file_log:
            #             file_log.write(json.dumps(dict(zip(header['VAR'],
            #                                                data_shot))))
            #             file_log.write('\n')
            #     print('Logged at {}'.format(time_stamp))
    #############################################
    # * DAC *

    # DAC CONFIG
    elif args.m == 'dac_config':
        if args.b is not None:
            print('Available DAC pins for {} board are : {}'.format(
                args.b, ADC_PINS_DICT[args.b]))
        else:
            dac_pin = args.po[0]
            analog_cmd = "from machine import DAC;analogdac_pin = DAC(Pin({}));".format(
                dac_pin)
            dac_cmd = analog_cmd
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            dev.wr_cmd(dac_cmd)
            dev.disconnect()
            print('Pin {} configured as Analog Output'.format(
                dac_pin))
        sys.exit()

    # DAC WRITE ## 8 BITS, 0-255
    elif args.m == 'dac_write':
        val_from_v = int((float(args.sig[0])/3.3)*255)
        analog_write = "analogdac_pin.write({});gc.collect()".format(val_from_v)
        dac_cmd = analog_write
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(dac_cmd)
        dev.disconnect()
        sys.exit()

    # DAC_SIG

    elif args.m == 'dac_sig':
        cmds = ['start', 'stop', 'mod']
        if args.sig[0] not in cmds:
            signal_class = "from dac_signal_gen import SIGNAL_GENERATOR;"
            signal_cmd = "sig=SIGNAL_GENERATOR(analogdac_pin,'{}',{},{})".format(
                *args.sig)
            conf_dac_sig = signal_class + signal_cmd
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            dev.wr_cmd(conf_dac_sig)
            print('Signal type {} with Amplitude {} V and fq {} Hz configured'.format(
                *args.sig))
        elif args.sig[0] == cmds[0]:
            signal_cmd = "sig.start()"
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            dev.wr_cmd(signal_cmd)
            print('Signal started!')

        elif args.sig[0] == cmds[1]:
            signal_cmd = "sig.stop()"
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            dev.wr_cmd(signal_cmd)
            print('Signal stopped!')

        elif args.sig[0] == cmds[2]:
            signal_cmd = "sig.modsig({},{})".format(args.sig[1], args.sig[2])
            dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
            dev.wr_cmd(signal_cmd)
            print('Signal modified to Amplitude: {} V, fq: {} Hz'.format(
                args.sig[1], args.sig[2]))

        dev.disconnect()
        sys.exit()

    #############################################
    # * BUZZER *
    # BUZZ CONFIG
    elif 'buzz' in args.m:
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        if args.m == 'buzz_config':
            BUZZ_pin = args.po[0]
            buzz_cmd = "from buzzertools import BUZZER;my_buzz = BUZZER({});".format(
                BUZZ_pin)

            dev.wr_cmd(buzz_cmd, silent=True)
            print('Pin {} configured as PWM to drive the buzzer'.format(
                BUZZ_pin))

        # BUZZ SET_ALARM
        elif args.m == 'buzz_set_alarm':
            if len(args.at) < 3:
                hour, minute = args.at
                seconds = 0
            else:
                hour, minute, seconds = args.at
            buzz_cmd = "my_buzz.set_alarm_at({},{},{});".format(hour, minute, seconds)

            dev.wr_cmd(buzz_cmd, silent=True)
            print('Alarm set at {}:{}:{}'.format(hour, minute, seconds))

        # BUZZ INTERRUPT
        elif args.m == 'buzz_interrupt':
            buzz_cmd = "my_buzz.active_button({},{});".format(*args.po)
            if args.md is not None:
                if args.md[0] == 'rev':
                    buzz_cmd = "my_buzz.active_button_rev({},{});".format(*args.po)

            dev.wr_cmd(buzz_cmd, silent=True)
            print('Button interrupt set at Pins; {},{}'.format(*args.po))

        # BUZZ BEEP
        elif args.m == 'buzz_beep':
            buzz_cmd = "my_buzz.buzz_beep({},{},{},{});".format(*args.opt)

            dev.wr_cmd(buzz_cmd, silent=True)
            print('Beep! '*args.opt[1])
        dev.disconnect()
        sys.exit()

    #############################################
    #  * MOTORS *

    #  * SERVO *
    # SERVO_CONFIG
    elif args.m == 'servo_config':
        servo_pin = args.po[0]
        servo_cmd = "from servo import Servo;my_servo = Servo(Pin({}));".format(
            servo_pin)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(servo_cmd)
        dev.disconnect()
        print('Pin {} configured as PWM to drive the Servo motor'.format(
            servo_pin))
        sys.exit()

    elif args.m == 'servo_angle':
        servo_angle = args.opt[0]
        servo_cmd = "my_servo.write_angle({});".format(
            servo_angle)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(servo_cmd)
        dev.disconnect()
        print('Servo moved to {} degrees!'.format(
            servo_angle))
        sys.exit()

    # * DC MOTOR *

    # DCMOTOR_CONFIG

    elif args.m == 'dcmotor_config':
        dir_pin, oppo_pin = args.po
        dcmotor_cmd = "from dcmotor import DCMOTOR;my_dcmotor = DCMOTOR({},{});".format(
            dir_pin, oppo_pin)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(dcmotor_cmd)
        dev.disconnect()
        print('DC motor configured: Direction Pin:{}, Opposite direction Pin: {}'.format(
            dir_pin, oppo_pin))
        sys.exit()

    # DCMOTOR_MOVE
    elif args.m == 'dcmotor_move':
        dcmotor_dir_dic = {'R': 0, 'L': 1}
        dcmotor_direction, velocity = args.to
        dcmotor_cmd = "my_dcmotor.move({},{});".format(
            dcmotor_dir_dic[dcmotor_direction], velocity)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(dcmotor_cmd)
        dev.disconnect()
        print('DC motor moving to {}!'.format(dcmotor_direction))
        sys.exit()

    # DCMOTOR_STOP
    elif args.m == 'dcmotor_stop':
        dcmotor_cmd = "my_dcmotor.stop();"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(dcmotor_cmd)
        dev.disconnect()
        print('DC motor stopped')
        sys.exit()
    # * STEPPER MOTOR *

    # STEPPER_CONFIG

    elif args.m == 'stepper_config':
        dir_pin, step_pin = args.po
        stepper_cmd = "from stepper import STEPPER;my_stepper = STEPPER({},{});".format(
            dir_pin, step_pin)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(stepper_cmd)
        dev.disconnect()
        print('Stepper motor configured: Direction Pin:{}, Step Pin: {}'.format(
            dir_pin, step_pin))
        sys.exit()

    # STEPPER_MOVE

    elif args.m == 'stepper_move':
        step_dir_dic = {'R': 0, 'L': 1}
        step_direction, velocity, steps = args.to
        stepper_cmd = "my_stepper.move_n_steps({},{},{});".format(
            step_dir_dic[step_direction], velocity, steps)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(stepper_cmd)
        dev.disconnect()
        print('Stepper moved {} steps to {} !'.format(
            steps, step_direction))
        sys.exit()

    #############################################
    #  * NETWORKING *

    #  * MQTT *

    # MQTT_CONFIG

    elif args.m == 'mqtt_config':
        if len(args.client) < 4:
            id, b_addr = args.client
            client_cmd = "from mqtt_client import mqtt_client ;my_mqtt = mqtt_client('{}','{}');".format(
                id, b_addr)
        else:
            id, b_addr, user, passwd = args.client
            client_cmd = "from mqtt_client import mqtt_client ;my_mqtt = mqtt_client('{}','{}',user = '{}', password = '{}');".format(
                id, b_addr, user, passwd)

        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(client_cmd)
        dev.disconnect()
        print('MQTT Client configured: ID: {}, BROKER: {}'.format(
            id, b_addr))
        sys.exit()

    # MQTT_CONN
    elif args.m == 'mqtt_conn':
        conn_cmd = "my_mqtt.connect();my_mqtt.set_def_callback();gc.collect()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(conn_cmd)
        dev.disconnect()
        print('MQTT Client connected!')
        sys.exit()

    # MQTT_SUB
    elif args.m == 'mqtt_sub':
        sub_cmd = "my_mqtt.subs('{}');gc.collect()".format(*args.to)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(sub_cmd)
        dev.disconnect()
        print('MQTT Client subscribed to TOPIC: {}'.format(*args.to))
        sys.exit()

    # MQTT_PUB
    elif args.m == 'mqtt_pub':
        if len(args.to) > 1:
            pub_cmd = "my_mqtt.pub(topic='{}',paylod='{}');gc.collect()".format(
                *args.to)
        else:
            pub_cmd = "my_mqtt.pub('{}');gc.collect()".format(*args.to)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(pub_cmd)
        dev.disconnect()
        if len(args.to) > 1:
            print('MQTT Client published message: {} to TOPIC: {}'.format(*args.to))
        else:
            print('MQTT Client published the message: {}'.format(*args.to))
        sys.exit()

    # MQTT_CHECK

    elif args.m == 'mqtt_check':
        check_cmd = "my_mqtt.check_msg();gc.collect()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(check_cmd)
        dev.disconnect()
        sys.exit()

    # * SOCKETS *

    # SOCLI_INIT
    elif args.m == 'socli_init':
        if len(args.server) > 2:
            host, port, buff = args.server
            socli_init_cmd = "my_cli=socket_client('{}',{},{})".format(
                host, port, buff)
        else:
            host, port = args.server
            socli_init_cmd = "my_cli=socket_client('{}',{})".format(host, port)
        socli_imp_cmd = "from socket_client_server import socket_client;"
        socli_comp_cmd = '{}{}'.format(socli_imp_cmd, socli_init_cmd)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(socli_comp_cmd)
        dev.disconnect()
        print('Initialized client socket to connect to server :{} on port {}'.format(host, port))
        sys.exit()

    # SOCLI_CONN
    elif args.m == 'socli_conn':
        socli_conn_cmd = "my_cli.connect_SOC();"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(socli_conn_cmd)
        dev.disconnect()

        print('Client connected!')
        sys.exit()

    # SOCLI_SEND
    elif args.m == 'socli_send':
        socli_send_cmd = "my_cli.send_message('{}');".format(args.n)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(socli_send_cmd)
        dev.disconnect()
        print('Message sent!')
        sys.exit()

    # SOCLI_RECV
    elif args.m == 'socli_recv':
        socli_recv_cmd = "my_cli.recv_message();"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(socli_recv_cmd)
        dev.disconnect()
        sys.exit()

    # SOCLI_CLOSE
    elif args.m == 'socli_close':
        socli_close_cmd = "my_cli.cli_soc.close();"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(socli_close_cmd)
        dev.disconnect()
        print('Client Socket closed!')
        sys.exit()

    # SOSRV_INIT
    elif args.m == 'sosrv_init':
        if len(args.server) > 1:
            port, buff = args.server
            sosrv_init_cmd = "my_serv=socket_server({},{})".format(port, buff)
        else:
            port = args.server[0]
            sosrv_init_cmd = "my_serv=socket_server({})".format(port)
        sosrv_imp_cmd = "from socket_client_server import socket_server;"
        sosrv_comp_cmd = '{}{}'.format(sosrv_imp_cmd, sosrv_init_cmd)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        serv_info = dev.wr_cmd(sosrv_comp_cmd, silent=True, rtn_resp=True)
        dev.disconnect()
        if len(serv_info) > 0:
            print('Server initialized. IP: {} PORT:{}'.format(serv_info, port))
        sys.exit()

    # SOSRV_START
    elif args.m == 'sosrv_start':
        sosrv_start_cmd = "my_serv.start_SOC();"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(sosrv_start_cmd)
        dev.disconnect()

        sys.exit()

    # SOSRV_SEND
    elif args.m == 'sosrv_send':
        sosrv_send_cmd = "my_serv.send_message('{}')".format(args.n)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(sosrv_send_cmd)
        dev.disconnect()
        print('Message sent!')
        sys.exit()

    # SOSRV_RECV
    elif args.m == 'sosrv_recv':
        sosrv_recv_cmd = "my_serv.recv_message()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(sosrv_recv_cmd)
        dev.disconnect()
        sys.exit()

    # SOSRV_CLOSE
    elif args.m == 'sosrv_close':
        sosrv_close_cmd = "my_serv.serv_soc.close()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(sosrv_close_cmd)
        dev.disconnect()
        print('Server Socket closed!')
        sys.exit()

    # * REQUEST *
    # RGET_JSON
    elif args.m == 'rget_json':
        rq_import_cmd = "import urequests as requests;"
        rq_query_cmd = "resp=requests.get('{}');".format(args.f)
        rq_json_cmd = "resp.json()"
        rq_comp_cmd = "{}{}{}".format(rq_import_cmd, rq_query_cmd, rq_json_cmd)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(rq_comp_cmd)
        dev.disconnect()
        sys.exit()

    # RGET_TEXT
    elif args.m == 'rget_text':
        rq_import_cmd = "import urequests as requests;"
        rq_query_cmd = "resp=requests.get('{}');".format(args.f)
        rq_text_cmd = "resp.text"
        rq_comp_cmd = "{}{}{}".format(rq_import_cmd, rq_query_cmd, rq_text_cmd)
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        dev.wr_cmd(rq_comp_cmd)
        dev.disconnect()
        sys.exit()
    #############################################
    #  * PORT SPECIFIC COMMANDS *

    # BATTERY

    elif args.m == 'battery':
        batt_cmd = "from machine import ADC;bat = ADC(Pin(35));bat.atten(ADC.ATTN_11DB);((bat.read()*2)/4095)*3.6;gc.collect()"
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)

        batlev = dev.wr_cmd(batt_cmd, silent=True, rtn_resp=True)
        dev.disconnect()
        try:
            if batlev > 0:
                volts = batlev
                percentage = round((volts - 3.3) / (4.23 - 3.3) * 100, 1)
                print('Battery Voltage : {} V; Level:{} %'.format(
                    round(volts, 2), percentage))
        except Exception as e:
            print('Battery Voltage : ? V; Level:? %')
        return

    # SPECS REF

    elif args.m == 'specs':
        try:
            board = args.b
            file_board = '{}/{}.config'.format(upydev.__path__[0], board)
            with open(file_board, 'r') as esp32ref:
                ref_dict = json.loads(esp32ref.read())

            print(ref_dict['SPECS'])

        except Exception as e:
            print("""reference board file not found""")
            sys.exit()

    # PIN OUT REF

    elif args.m == 'pinout':
        try:
            board = args.b
            file_board = '{}/{}.config'.format(upydev.__path__[0], board)
            with open(file_board, 'r') as esp32ref:
                ref_dict = json.loads(esp32ref.read())

            if args.po is not None:
                pin_query = args.po
                for query in pin_query:
                    print('PIN: {}: {}'.format(
                        query, ref_dict['PINOUT'][str(query)]))
            else:
                for key in ref_dict['PINOUT']:
                    print('PIN: {}: {}'.format(key, ref_dict['PINOUT'][key]))

        except Exception as e:
            print(str(e), ' Pin not Found or')
            print("""reference board file not found""")
            sys.exit()

        sys.exit()

    elif args.m == 'pin_status':
        dev = Device(args.t, args.p, init=True, ssl=args.wss, auth=args.wss)
        pinlist = "[16, 17, 26, 25, 34, 39, 36, 4, 21, 13, 12, 27, 33, 15, 32, 14, 22, 23, 5, 18, 19]"
        machine_pin = "pins=[machine.Pin(i, machine.Pin.IN) for i in pin_list]"
        status = "dict(zip([str(p) for p in pins],[p.value() for p in pins]))"
        pin_status_cmd = "import machine;pin_list={};{};{};gc.collect()".format(
            pinlist, machine_pin, status)
        pin_dict = dev.wr_cmd(pin_status_cmd, silent=True, rtn_resp=True)
        dev.disconnect()
        if pin_dict:
            if args.po is not None:
                pin_rqst = ['Pin({})'.format(po) for po in args.po]
                for key in pin_dict.keys():
                    if key in pin_rqst:
                        if pin_dict[key] == 1:
                            print('{0:^10} | {1:^5} | HIGH'.format(
                                key, pin_dict[key]))
                        else:
                            print('{0:^10} | {1:^5} |'.format(key, pin_dict[key]))

            else:
                for key in pin_dict.keys():
                    if pin_dict[key] == 1:
                        print('{0:^10} | {1:^5} | HIGH'.format(key, pin_dict[key]))
                    else:
                        print('{0:^10} | {1:^5} |'.format(key, pin_dict[key]))

        sys.exit()
