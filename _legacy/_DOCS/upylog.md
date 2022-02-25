## Upylog 

MicroPython logging module with time format (predefined) and log to file support.



* **upylog.basicConfig**(level=INFO, filename=_filename, stream=None, format=None, sd=False)

  * *level*: same as logging, by <u>default</u> **upylog.INFO**
    * options: [upylog.DEBUG, upylog.INFO, upylog.WARNING, upylog.ERROR, upylog.CRITICAL]
  * *filename*: by <u>default</u> '**error.log**'
  * *stream*: by <u>default</u> **sys.stderr**

  * *format*: by <u>default</u> **"LVL_MSG"**, this will print [NAME] [LEVEL] MESSAGE
    * options: 
      * "LVL_MSG" --> [NAME] [LEVEL] MESSAGE
      * "TIME_LVL_MSG" --> TIME [NAME] [LEVEL] MESSAGE
  * *sd*: by <u>default</u> **False**; if set to True, 'error.log' file will be store in a mounted sd named 'sd'



* **If using time format, don't forget to set the RTC, otherwise it will start to count from 2000-01-01 00:00:00**

  

*Example:*

```python
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
 
```

*Output:*

```python
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

 # To see if the error was logged to file 
>>> cat('error.log')
2019-11-14 21:37:45 [errorlog_test] [ERROR] Exception Ocurred
Traceback (most recent call last):
  File "test_code.py", line 20, in <module>
ZeroDivisionError: divide by zero
```

