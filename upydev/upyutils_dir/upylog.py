import sys
from micropython import const
import time


CRITICAL = const(50)
ERROR = const(40)
WARNING = const(30)
INFO = const(20)
DEBUG = const(10)
NOTSET = const(0)

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_format_dict = {"LVL_MSG": "[{}] [{}] ", "TIME_LVL_MSG": "{} [{}] [{}] "}

_stream = sys.stderr
_level = INFO
_loggers = {}
_filename = 'error.log'
_format = _format_dict["LVL_MSG"]
_asciitime = False
_sdlog = False


class Logger:
    def __init__(self, name, l_level=_level, log_to_file=False, logfile=_filename, f_time=False, l_format=_format):
        self.name = name
        self.level = l_level
        self.logfile = logfile
        self.log_to_file = log_to_file
        self.l_format = l_format
        self.log_message = None
        self.log_message_info = None
        self.f_time = f_time
        self._t_now = None
        self.date_time = None
        self._n = None
        self._dt_list = [0, 1, 2, 3, 4, 5]

    def _level_str(self, level):
        lev = _level_dict.get(level)
        if lev is not None:
            return lev
        return "LVL: {}".format(level)

    def setLevel(self, level):
        self.level = level

    def _dt_format(self, number):
        self._n = str(number)
        if len(self._n) == 1:
            self._n = "0{}".format(self._n)
            return self._n
        else:
            return self._n

    def _ft_datetime(self, t_now):
        return([self._dt_format(t_now[i]) for i in self._dt_list])

    def get_datetime(self):
        self.t_now = time.localtime()
        self.date_time = '{}-{}-{} {}:{}:{}'.format(*self._ft_datetime(self.t_now))
        return self.date_time

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def file_log_msg(self, msg):
        with open(self.logfile, 'ab') as flog:
            flog.write(msg)
            flog.write('\n')

    def file_log_exception(self, ex):
        with open(self.logfile, 'ab') as flog:
            sys.print_exception(ex, flog)
            flog.write('\n')

    def log(self, level, msg, *args):
        if level >= (self.level or _level):
            if self.f_time:
                self.get_datetime()
                self.log_message_info = self.l_format.format(self.date_time,
                                                             self.name,
                                                             self._level_str(level),
                                                             )
            else:
                self.log_message_info = self.l_format.format(self.name,
                                                             self._level_str(level),
                                                             )
            _stream.write(self.log_message_info)
            if not args:
                print(' '.join([msg]), file=_stream)
                if self.log_to_file:
                    self.file_log_msg(''.join([self.log_message_info, msg]))
            else:
                print(' '.join([msg % args]), file=_stream)
                if self.log_to_file:
                    self.file_log_msg(''.join([self.log_message_info, msg % args]))

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

    def exception(self, e, msg, *args):
        self.log(ERROR, msg, *args)
        sys.print_exception(e, _stream)
        if self.log_to_file:
            self.file_log_exception(e)


def getLogger(name, log_to_file=False):
    global _level, _stream, _filename, _format, _format_dict, _asciitime, _sdlog
    if name in _loggers:
        return _loggers[name]
    ulogger = Logger(name, l_level=_level,
                     log_to_file=log_to_file, logfile=_filename,
                     f_time=_asciitime, l_format=_format)
    _loggers[name] = ulogger
    return ulogger


def info(msg, *args):
    getLogger(None).info(msg, *args)


def debug(msg, *args):
    getLogger(None).debug(msg, *args)


def basicConfig(level=INFO, filename=_filename, stream=None, format=None, sd=False):
    global _level, _stream, _filename, _format, _format_dict, _asciitime, _sdlog
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
        _filename = filename
    if format is not None:
        if format not in _format_dict.keys():
            print('Not supported format; Supported format are : {}'.format(_format_dict.keys()))
        else:
            _format = _format_dict[format]
            if format == 'TIME_LVL_MSG':
                _asciitime = True
    if sd:
        _sdlog = True
        if filename is not None:
            _filename = "/sd/{}".format(filename)
