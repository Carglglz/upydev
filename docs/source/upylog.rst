Upylog
======

MicroPython logging module with time format (predefined) and log to file support.


* **upylog.basicConfig** (level=INFO, filename=_filename, stream=None, format=None, sd=False)

    * *level*\: same as logging, by default **upylog.INFO**

        * options\: [upylog.DEBUG, upylog.INFO, upylog.WARNING, upylog.ERROR, upylog.CRITICAL] or strings "DEBUG", "INFO"...
    * *filename*\: by default '**error.log**'

    * *stream*\: by default **sys.stderr**

    * *format*\: by default **"LVL_MSG"**, this will print [NAME] [LEVEL] MESSAGE

        * options\:

            * "LVL_MSG" --> [NAME] [LEVEL] MESSAGE

            * "TIME_LVL_MSG" --> TIME [NAME] [LEVEL] MESSAGE

    * *sd*\: default **False**; if set to *True*, 'error.log' file will be store in a mounted sd named 'sd'


* **upylog.getLogger** (name, log_to_file=False, rotate=_rotate)

    * *name*\: the name of the logger.

    * *log_to_file*\: wether save log output in the log file.

    * *rotate*\: max size in bytes of the log file (default 2000).

    .. note::
      When max size is reached the log file will be renamed [logfile].log.1 and continue logging to [logfile].log, which means that
      if at all there would be two log files with max size of aprox. *rotate* bytes.

.. note::

    If using time format, don't forget to set the RTC, otherwise it will start to count from default EPOCH.


.. note::

   By default ``Logger`` log level and file log level will be the same but both can be changed
   with for log level ``Logger.setLevel(level)`` and file log level ``Logger.setLogfileLevel(level)``.


*Example:*


.. code-block:: python

    import upylog

    upylog.basicConfig(level=upylog.INFO, format='TIME_LVL_MSG')
    errlog = upylog.getLogger("errorlog_test", log_to_file=True) # This log to file 'error.log';
    log = upylog.getLogger("log_test") # This just prints to sys.stdout
    log.debug("Test message: %d(%s)", 100, "foobar")
    log.info("Test message2: %d(%s)", 100, "foobar")
    log.warning("Test message3: %d(%s)")
    log.error("Test message4")
    log.critical("Test message5")
    upylog.info("Test message6")

    try:
        1/0
    except Exception as e:
        log.exception(e, "Exception Ocurred") # This error is not logged to file
        pass

    try:
        5/0
    except Exception as e:
        errlog.exception(e, "Exception Ocurred") # This error IS logged to file
        pass


*Output:*

.. code-block:: console

  2019-11-14 21:37:45 [log_test] [INFO] Test message2: 100(foobar)
  2019-11-14 21:37:45 [log_test] [WARN] Test message3: %d(%s)
  2019-11-14 21:37:45 [log_test] [ERROR] Test message4
  2019-11-14 21:37:45 [log_test] [CRIT] Test message5
  2019-11-14 21:37:45 [None] [INFO] Test message6
  2019-11-14 21:37:45 [log_test] [ERROR] Exception Ocurred
  Traceback (most recent call last):
    File "test_code.py", line 14, in <module>
  ZeroDivisionError: divide by zero
  2019-11-14 21:37:45 [errorlog_test] [ERROR] Exception Ocurred
  Traceback (most recent call last):
    File "test_code.py", line 20, in <module>
  ZeroDivisionError: divide by zero


.. code-block:: console

 # To see if the error was logged to file

>>> cat('error.log')
2019-11-14 21:37:45 [errorlog_test] [ERROR] Exception Ocurred
Traceback (most recent call last):
  File "test_code.py", line 20, in <module>
ZeroDivisionError: divide by zero


.. note::

	To enable remote logging with ``ursyslogger.RsysLogger`` add remote logger to log with:

  .. code-block:: python

    ...
    >>> rsyslog = RsysLogger("server.local", port=514, hostname="mydevice", t_offset="+01:00")
    >>> log.remote_logger = rsyslog
    >>> log.info("Remote hello")
    2022-09-15 10:06:04 [esp32@mydevice] [INFO] Remote hello

  and in server e.g.

  .. code-block:: console

    $ tail -F mydevice.local.log
    Sep 15 10:06:04 mydevice.local esp32@mydevice Remote hello
