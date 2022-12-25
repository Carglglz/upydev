# sysctl for async tasks

import uasyncio as asyncio


_AIOCTL_GROUP = None


def create_task(coro, *args, **kwargs):
    if "name" not in kwargs:
        task = asyncio.create_task(coro(*args, **kwargs))
        name = coro.__name__
    else:
        name = kwargs.pop("name")
        task = asyncio.create_task(coro(*args, **kwargs))
    return Taskctl(coro, task, name, args, kwargs)


class Taskctl:
    def __init__(self, coro, task, name, args, kwargs):
        self.coro = coro
        self.task = task
        self.name = name
        self.args = args
        self.kwargs = kwargs


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


def status(name):
    global _AIOCTL_GROUP
    if _AIOCTL_GROUP.tasks[name].task.done():
        _AIOCTL_GROUP.results[name] = _AIOCTL_GROUP.tasks[name].task.data
        return f"done --> result: { _AIOCTL_GROUP.tasks[name].task.data}"
    else:
        return "running"


def result(name):
    global _AIOCTL_GROUP
    if _AIOCTL_GROUP.tasks[name].task.done():
        return _AIOCTL_GROUP.tasks[name].task.data.value
    else:
        return


def status_all():
    global _AIOCTL_GROUP
    for name in _AIOCTL_GROUP.tasks.keys():
        print(f"{name}: {status(name)}")


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


def stop(name):
    global _AIOCTL_GROUP
    try:
        if not _AIOCTL_GROUP.tasks[name].task.done():
            _AIOCTL_GROUP.tasks[name].task.cancel()

        _AIOCTL_GROUP.results[name] = _AIOCTL_GROUP.tasks[name].task.data

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
