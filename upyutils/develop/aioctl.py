# sysctl for async tasks

import uasyncio as asyncio
import sys
import time

_SCHEDULE = False
try:
    import aioschedule

    _SCHEDULE = True
except Exception:
    pass

_AIOCTL_GROUP = None
_AIOCTL_LOG = None
_DEBUG = False


def aiotask(f):
    # print(f.__name__)

    async def _task(*args, **kwargs):
        on_error = kwargs.get("on_error")
        on_stop = kwargs.get("on_stop")
        _id = kwargs.get("_id")
        if on_error:
            kwargs.pop("on_error")
        if on_stop:
            kwargs.pop("on_stop")
        if _id:
            kwargs.pop("_id")
        else:
            _id = f.__name__
        try:
            result = await f(*args, **kwargs)
            if _id in group().tasks.keys():
                group().tasks[_id].done_at = time.time()
            return result
        except asyncio.CancelledError:
            if _id in group().tasks.keys():
                group().tasks[_id].done_at = time.time()
            if callable(on_stop):
                return on_stop()
            return on_stop

        except Exception as e:
            if _id in group().tasks.keys():
                group().tasks[_id].done_at = time.time()
            log = kwargs.get("log")
            if log:
                log.error(f"[{_id}]" + f" {e.__class__.__name__}: {e.errno}")
            if callable(on_error):
                return on_error(e)
            return e

    return _task, f.__name__


def create_task(coro, *args, **kwargs):
    name = None
    if isinstance(coro, follow.__class__):
        name = kwargs.get("name", coro.__name__)
    if "name" in kwargs:
        name = kwargs.pop("name")
    # print(type(coro), coro)

    # print(dir(coro))
    if isinstance(coro, tuple):
        coro, _name = coro[0], coro[1]
        if not name:
            name = _name
    if callable(coro):
        _coro = coro(*args, **kwargs)
        if isinstance(_coro, tuple):
            _coro, _name = _coro[0], _coro[1]
            if not name:
                name = _name
    # print(type(_coro), _coro)
    task = asyncio.create_task(_coro)
    # print(task, coro, name)
    # print(dir(task))
    # print(dir(task.coro))
    return Taskctl(coro, task, name, args, kwargs)


class Taskctl:
    def __init__(self, coro, task, name, args, kwargs):
        self.coro = coro
        self.task = task
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.since = time.time()
        self.done_at = None


class TaskGroup:
    def __init__(self, tasks=[]):
        self.tasks = {task.name: task for task in tasks}
        self.cnt = 0
        self.results = {}

    def add_task(self, task):
        if task.name not in self.tasks:
            self.tasks[task.name] = task
            self.cnt = 0
        else:
            self.cnt += 1
            new_name = f"{task.name}_{self.cnt}"
            task.name = new_name
            self.tasks[task.name] = task


def set_group(taskgroup):
    global _AIOCTL_GROUP
    _AIOCTL_GROUP = taskgroup


def set_log(log):
    global _AIOCTL_LOG
    _AIOCTL_LOG = log


def group():
    global _AIOCTL_GROUP
    return _AIOCTL_GROUP


def tasks():
    global _AIOCTL_GROUP
    return [task.task for task in _AIOCTL_GROUP.tasks.values()]


def add(coro, *args, **kwargs):
    global _AIOCTL_GROUP
    new_task = create_task(coro, *args, **kwargs)
    if not _AIOCTL_GROUP:
        _AIOCTL_GROUP = TaskGroup([new_task])
    else:
        _AIOCTL_GROUP.add_task(new_task)


def delete(*args):
    global _AIOCTL_GROUP
    for name in args:
        if name in _AIOCTL_GROUP.tasks.keys():
            _AIOCTL_GROUP.tasks.pop(name)


def status(name=None, log=True, debug=False):
    global _AIOCTL_GROUP, _AIOCTL_LOG, _SCHEDULE, _DEBUG
    if _DEBUG:
        debug = _DEBUG
    if not name:
        return status_all(log=log, debug=debug)
    if name in _AIOCTL_GROUP.tasks:
        if _AIOCTL_GROUP.tasks[name].task.done():
            _AIOCTL_GROUP.results[name] = _AIOCTL_GROUP.tasks[name].task.data
            status = "done"
            _done_at = group().tasks[name].done_at
            if _SCHEDULE:
                if _done_at:
                    _done_at = time.localtime(_done_at)
                    _done_at = aioschedule.get_datetime(_done_at)
                    _done_delta = time.time() - group().tasks[name].done_at
                    _done_at += f"; {aioschedule.tmdelta_fmt(_done_delta)} ago"

            data = _AIOCTL_GROUP.results[name]
            if issubclass(data.value.__class__, Exception):
                status = "\u001b[31;1mERROR\u001b[0m"
                data = (
                    f"\u001b[31;1m{data.value.__class__.__name__}\u001b[0m:"
                    + f" {data.value.value}"
                )

            print(f"{name}: status: {status} @ {_done_at} --> result: " + f"{data}")
            if debug:
                c_task = _AIOCTL_GROUP.tasks[name]
                print(f"    ┗━► args: {c_task.args}, kwargs: {c_task.kwargs}")
            if _SCHEDULE:
                aioschedule.status_sc(name, debug=debug)
            if log and _AIOCTL_LOG:
                _AIOCTL_LOG.cat(grep=name)
                print("<" + "-" * 80 + ">")
        else:
            # 2023-01-12 04:42:51 GMT; 2 weeks 0 days ago
            _since_str = time.localtime(group().tasks[name].since)
            _since_delta = time.time() - group().tasks[name].since

            if _SCHEDULE:
                _since_str = aioschedule.get_datetime(_since_str)
                _since_str += f"; {aioschedule.tmdelta_fmt(_since_delta)}"
            print(f"{name}: status: \033[92mrunning\x1b[0m since {_since_str} ago")
            if debug:
                c_task = _AIOCTL_GROUP.tasks[name]
                print(f"    ┗━► args: {c_task.args}, kwargs: {c_task.kwargs}")
            if _SCHEDULE:
                aioschedule.status_sc(name, debug=debug)
            if log and _AIOCTL_LOG:
                _AIOCTL_LOG.cat(grep=name)
                print("<" + "-" * 80 + ">")
    else:
        print(f"Task {name} not found in {list(_AIOCTL_GROUP.tasks.keys())}")


def result(name=None):
    global _AIOCTL_GROUP
    if not name:
        return result_all()

    if name in _AIOCTL_GROUP.tasks:
        if _AIOCTL_GROUP.tasks[name].task.done():
            return _AIOCTL_GROUP.tasks[name].task.data.value
    else:
        return


def debug():
    global _DEBUG
    _DEBUG = not _DEBUG
    print(f"debug mode: {_DEBUG}")


def result_all(as_dict=False):
    global _AIOCTL_GROUP
    if not as_dict:
        for name in _AIOCTL_GROUP.tasks.keys():
            print(f"{name} --> {result(name)}")
    else:
        return {name: result(name) for name in _AIOCTL_GROUP.tasks.keys()}


def status_all(log=True, debug=False):
    global _AIOCTL_GROUP
    for name in _AIOCTL_GROUP.tasks.keys():
        if name:
            status(name, log=log, debug=debug)


def start(name):
    global _AIOCTL_GROUP
    if name in _AIOCTL_GROUP.tasks:
        coro = _AIOCTL_GROUP.tasks[name].coro
        args = _AIOCTL_GROUP.tasks[name].args
        kwargs = _AIOCTL_GROUP.tasks[name].kwargs
        kwargs["name"] = name
        _AIOCTL_GROUP.tasks.pop(name)
        try:
            add(coro, *args, **kwargs)
        except Exception as e:
            print(e)
        return True
    else:
        return False


def stop(name=None):
    global _AIOCTL_GROUP
    if not name:
        return stop_all()
    try:
        if name in _AIOCTL_GROUP.tasks:
            if not _AIOCTL_GROUP.tasks[name].task.done():
                _AIOCTL_GROUP.tasks[name].task.cancel()

            _AIOCTL_GROUP.results[name] = _AIOCTL_GROUP.tasks[name].task.data
        else:
            print(f"Task {name} not found in {list(_AIOCTL_GROUP.tasks.keys())}")

    except asyncio.CancelledError:
        pass
    except RuntimeError as e:
        print(f"{e}, {name}")
        pass
    return True


def stop_all():
    global _AIOCTL_GROUP
    for name in _AIOCTL_GROUP.tasks.keys():
        stop(name)
    return True


async def follow(grep="", wait=0.05):
    global _AIOCTL_LOG

    if _AIOCTL_LOG:
        return await _AIOCTL_LOG.follow(grep=grep, wait=wait)


def traceback(name=None):
    if not name:
        return traceback_all()
    _tb = result(name)
    if issubclass(_tb.__class__, Exception):
        print(f"{name}: Traceback")
        sys.print_exception(_tb)


def traceback_all():
    global _AIOCTL_GROUP
    for name in _AIOCTL_GROUP.tasks.keys():
        traceback(name)


def run():
    global _AIOCTL_GROUP

    async def _main():
        for name in _AIOCTL_GROUP.tasks.keys():
            start(name)
        await asyncio.gather(*tasks())

    asyncio.run(_main())


def reset(group=True, log=False):
    global _AIOCTL_GROUP, _AIOCTL_LOG

    if group:
        _AIOCTL_GROUP = None
    if log:
        _AIOCTL_LOG = None
