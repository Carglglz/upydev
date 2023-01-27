# sysctl for async tasks

import uasyncio as asyncio
import time
import aioctl

_AIOCTL_SCHEDULE_GROUP = {}
_AIOCTL_SCHEDULE_T0 = 0
_dt_list = [0, 1, 2, 3, 4, 5]


def schedule_task(**sch_kwargs):
    # print(sch_kwargs)

    def deco_schedule(f):
        def _schedule(*args, **kwargs):
            # print(args, kwargs)
            value, name = f[0](*args, **kwargs), f[1]
            # print(value, name)
            return value, name

        schedule(f[1], **sch_kwargs)
        return _schedule

    return deco_schedule


def schedule(f, *args, **kwargs):
    global _AIOCTL_SCHEDULE_GROUP
    # add task to schedule group
    _AIOCTL_SCHEDULE_GROUP[f] = kwargs


def unschedule(f):
    group().pop(f)


def _dt_format(number):
    n = str(number)
    if len(n) == 1:
        n = "0{}".format(n)
        return n
    else:
        return n


def _ft_datetime(t_now):
    return [_dt_format(t_now[i]) for i in _dt_list]


def get_datetime(_dt):
    return "{}-{}-{} {}:{}:{}".format(*_ft_datetime(_dt))


def time_str(uptime_tuple):
    upt = [_dt_format(i) for i in uptime_tuple[1:]]
    up_str_1 = f"{uptime_tuple[0]} days, "
    up_str_2 = f"{upt[0]}:{upt[1]}:{upt[2]}"
    if uptime_tuple[0] > 0:
        return up_str_1 + up_str_2
    elif uptime_tuple[-2] > 0:
        return up_str_2
    return f"{uptime_tuple[-1]} s"


def tmdelta_fmt(dt):
    if dt < 0:
        return f"the past by {tmdelta_fmt(abs(dt))} s"
    dd, hh, mm, ss = (0, 0, 0, 0)
    mm = dt // 60
    ss = dt % 60
    if mm:
        pass
    else:
        return time_str((dd, hh, mm, ss))
    hh = mm // 60
    if hh:
        mm = mm % 60
    else:
        return time_str((dd, hh, mm, ss))
    dd = hh // 24
    if dd:
        hh = hh % 24
    else:
        return time_str((dd, hh, mm, ss))

    return time_str((dd, hh, mm, ss))


async def schedule_loop(alog=None):
    #  global schedule group
    global _AIOCTL_SCHEDULE_GROUP, _AIOCTL_SCHEDULE_T0

    def do_start_task(c_task):
        if alog:
            alog.info(f"[schedule_loop] starting task {c_task}")
        if c_task not in aioctl.group().tasks:
            pass
        else:
            if aioctl.group().tasks[c_task].task.done():
                aioctl.start(c_task)
        _AIOCTL_SCHEDULE_GROUP[c_task]["start_in"] = -1
        _AIOCTL_SCHEDULE_GROUP[c_task]["last"] = time.time()
        _AIOCTL_SCHEDULE_GROUP[c_task]["last_dt"] = time.localtime()

    # stop everything
    for _sch_task in _AIOCTL_SCHEDULE_GROUP.keys():
        if alog:
            alog.info(f"stoping {_sch_task}")
        aioctl.stop(_sch_task)
    t0 = time.time()
    _AIOCTL_SCHEDULE_T0 = t0
    while True:
        if alog:
            alog.info("[schedule_loop] looping...")
        # first solve short term.
        for _sch_task, cond in _AIOCTL_SCHEDULE_GROUP.items():
            if alog:
                alog.info(f"[schedule_loop] {_sch_task} {cond} @ {time.time()-t0}")
            start_in = cond.get("start_in")
            repeat = cond.get("repeat")
            if start_in:
                if isinstance(start_in, tuple):
                    start_in = time.mktime(start_in) - time.time()
                    _AIOCTL_SCHEDULE_GROUP[_sch_task]["start_in"] = start_in
                if start_in == 0:
                    do_start_task(_sch_task)
                if start_in > 0:
                    if time.time() - t0 >= start_in:
                        do_start_task(_sch_task)
            if repeat is True:
                repeat = start_in
                _AIOCTL_SCHEDULE_GROUP[_sch_task]["repeat"] = repeat
            if repeat:
                last = _AIOCTL_SCHEDULE_GROUP[_sch_task].get("last", None)
                if last:
                    if (time.time() - last) >= repeat:
                        do_start_task(_sch_task)

        # start_in and repeat for short term
        # at and repeat_dt for long term
        # or a mix of both
        # aioctl.add for first time and aioctl.start for the following
        await asyncio.sleep(1)


def status_sc(name, debug=False):
    global _AIOCTL_SCHEDULE_GROUP, _AIOCTL_SCHEDULE_T0
    if not name:
        return status_sc_all()
    if name in _AIOCTL_SCHEDULE_GROUP:
        last = _AIOCTL_SCHEDULE_GROUP[name].get("last_dt")
        _last_tm = _AIOCTL_SCHEDULE_GROUP[name].get("last")
        repeat = _AIOCTL_SCHEDULE_GROUP[name].get("repeat")
        _schedule = _AIOCTL_SCHEDULE_GROUP[name]
        _sch_str = ", ".join([f"{k}={v}" for k, v in _schedule.items()])
        _next = None
        if last:
            last = get_datetime(last)
            if repeat:
                _next = repeat - (time.time() - _last_tm)
        else:
            start_in = _AIOCTL_SCHEDULE_GROUP[name].get("start_in")
            if start_in:
                if isinstance(start_in, tuple):
                    _next = time.mktime(start_in) - time.time()
                else:
                    _next = _AIOCTL_SCHEDULE_T0 + start_in - time.time()

        print(f"{name}: last @ {last} --> scheduled in {tmdelta_fmt(_next)}")
        if debug:

            print(f"    ┗━► schedule opts: {_sch_str}")
    else:
        if debug:
            print(f"Task {name} not found in schedule group")


def status_sc_all():
    global _AIOCTL_SCHEDULE_GROUP
    for name in _AIOCTL_SCHEDULE_GROUP.keys():
        status_sc(name)


def set_group(taskgroup):
    global _AIOCTL_SCHEDULE_GROUP
    _AIOCTL_SCHEDULE_GROUP = taskgroup


def set_log(log):
    global _AIOCTL_LOG
    _AIOCTL_LOG = log


def group():
    global _AIOCTL_SCHEDULE_GROUP
    return _AIOCTL_SCHEDULE_GROUP


def reset(group=True, log=False):
    global _AIOCTL_SCHEDULE_GROUP

    if group:
        _AIOCTL_SCHEDULE_GROUP = {}
