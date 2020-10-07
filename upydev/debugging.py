

DEBUGGING_HELP = """
> DEBUGGING: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - ping : pings the target to see if it is reachable, CTRL-C to stop

        - run : just calls import 'script', where 'script' is indicated by -f option
                (script must be in upydevice or in sd card indicated by -s option
                and the sd card must be already mounted as 'sd');
                * Supports CTRL-C to stop the execution and exits nicely.

        - timeit: to measure execution time of a module/script indicated with -f option.
                  This is an implementation of
                  https://github.com/peterhinch/micropython-samples/tree/master/timed_function

        - see: to get specific command help info indicated with -c option.

        - find: to get a list of possible upy devices. Scans the local network to find devices
                with port 8266 (WebREPL) open. Use -n option to perform n scans (A single scan
                may not find all the devices)

        - diagnose: to make a diagnostic test of the device (sends useful to commands
                    to get device state info), to save report to file see -rep, use -n to save
                    the report with a custom name (automatic name is "upyd_ID_DATETIME.txt")
                    Use "-md local" option if connected to esp AP.

        - errlog: if 'error.log' is present in the upydevice, this shows the content
                    (cat('error.log')), if 'error.log' in sd use -s sd

        - stream_test: to test download speed (from device to host). Default test is 10 MB of
                       random bytes are sent in chunks of 20 kB and received in chunks of 32 kB.
                       To change test parameters use -chunk_tx , -chunk_rx, and -total_size.

        - sysctl : to start/stop a script without following the output. To follow initiate
                   wrepl/srepl as normal, and exit with CTRL-x (webrepl) or CTRL-A,X (srepl)
                   TO START: use -start [SCRIPT_NAME], TO STOP: use -stop [SCRIPT_NAME]

        - log: to log the output of a upydevice script, indicate script with -f option, and
                the sys.stdout log level and file log level with -dslev and -dflev (defaults
                are debug for sys.stdout and error for file). To log in background use -daemon
                option, then the log will be redirected to a file with level -dslev.
                To stop the 'daemon' log mode use -stopd and indicate script with -f option.
                'Normal' file log and 'Daemon' file log are under .upydev_logs folder in $HOME
                directory, named after the name of the script. To follow an on going 'daemon'
                mode log, use -follow option and indicate the script with -f option.

        - debug: to execute a local script line by line in the target upydevice, use -f option
                to indicate the file. To enter next line press ENTER, to finish PRESS C
                then ENTER. To break a while loop do CTRL+C.

        - pytest: to run upydevice test with pytest, do "pytest-setup" first to enable selection
                 of specific device with -@ entry point.
                 """
