import time


def settime():
    with open('.uptime', 'wb') as _uptime:
        _uptime.write(str(time.localtime()).encode())

def gettime():
     with open('.uptime', 'rb') as _uptime:
         init_time = time.mktime(eval(_uptime.read()))
         t_now = time.time()
         up_time = t_now - init_time
     return up_time

def _dt_format(number):
    n = str(number)
    if len(n) == 1:
        n = "0{}".format(n)
        return n
    else:
        return n

def _ft_datetime(t_now):
    return([_dt_format(t_now[i]) for i in range(6)])

def get_datetime():
    t_now = time.localtime()
    date_time = '{}-{}-{} {}:{}:{}'.format(*_ft_datetime(t_now))
    return date_time

def uptime_str(uptime_tuple):
   t_now = time.localtime()
   ts = _ft_datetime(t_now)
   upt = [_dt_format(i) for i in uptime_tuple[1:]]
   up_str_0 = f"{ts[3]}:{ts[4]}  "
   up_str_1 = f"up {uptime_tuple[0]} days, "
   up_str_2 = f"{upt[0]}:{upt[1]}:{upt[2]}"
   return up_str_0 + up_str_1 + up_str_2


def uptime():
    # int uptime
    int_uptime = gettime()
    # (dd, hh, mm, ss)
    dd, hh, mm , ss = (0, 0, 0, 0)
    mm = int_uptime // 60
    ss = int_uptime % 60
    if mm:
        pass
    else:
        return uptime_str((dd, hh, mm, ss))
    hh = mm // 60
    if hh:
        mm = mm % 60
    else:
        return uptime_str((dd, hh, mm, ss))
    dd = hh // 24
    if dd:
        hh = hh % 24
    else:
        return uptime_str((dd, hh, mm, ss))

    return uptime_str((dd, hh, mm, ss))



