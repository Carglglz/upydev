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
