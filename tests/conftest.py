import ast
import pytest
import yaml
from braceexpand import braceexpand
from pytest_benchmark import utils
from pytest_benchmark import session
from pytest_benchmark import cli
from upydev.tableresults import TableResults

# Monkey patch to allow custom measure units other than time/seconds
# This allows to benchmark sensor measurements too
session.TableResults = TableResults
cli.TableResults = TableResults


# PARSE YAML TEST FILE
def parse_task_file(task_file):
    with open(task_file, "r") as tf:
        task_doc = tf.read()
    task = yaml.safe_load(task_doc)
    # print(task)
    return task

# PARSE YAML TEST FILE


def parse_yaml(get_yamlfile):
    test_struct = parse_task_file(get_yamlfile)
    return test_struct


# CUSTOM UNITS

def str_replace(a, b, offset=0, post=0):
    len_diff = len(a) - len(b)
    len_a = len(a)
    backspaces = '\x08' * len_a
    if len_diff > 0:
        b += ' ' * len_diff
    return f"{backspaces}{b}"


def pytest_addoption(parser):
    parser.addoption("--dev", action="store", default="default",
                     help="indicate the device with which to run the test")
    parser.addoption("--wss", action="store_true", default=False,
                     help="to indicate use of ssl if WebSecureREPL enabled in WebSocketDevice")
    parser.addoption("--devp", action="store", default="default",
                     help="indicate the device with which to run the test")
    parser.addoption("--yf", help="indicate a test yaml file to use", nargs='*')
    parser.addoption("--unit", help="indicate a unit to use if other than time",
                     default="time:s")


@pytest.fixture
def devname(request):
    return request.config.getoption("--dev")


@pytest.fixture
def use_ssl(request):
    return request.config.getoption("--wss")


@pytest.fixture
def get_unit(request):
    return request.config.getoption("--unit")


def pytest_generate_tests(metafunc):
    if "cmd" in metafunc.fixturenames:
        test_struct = []
        for tst in metafunc.config.getoption("--yf"):
            test_struct += parse_yaml(tst)
        test_names = [tst["name"] for tst in test_struct]
        # expands params as different args test cases
        for k, tst in enumerate(test_struct):
            if "params" in tst:
                # parse params and assert if python expression:
                if isinstance(tst["params"], str):
                    try:
                        tst["params"] = [ast.literal_eval(tc) for tc in list(
                            braceexpand(tst["params"]))]
                    except Exception as e:
                        print(e)
                if isinstance(tst["assert"], str):
                    try:
                        tst["assert"] = [ast.literal_eval(tc) for tc in list(
                            braceexpand(tst["assert"]))]
                    except Exception as e:
                        print(e)
                for i, p_case in enumerate(tst["params"]):
                    p_test = dict(tst)
                    p_test["args"] = p_case
                    p_test["assert"] = tst["assert"][i]
                    p_test.pop('params')
                    test_struct.insert(k, p_test)
                    test_names.insert(k, f"{p_test['name']}{i}")
                test_struct.remove(tst)
                test_names.remove(tst["name"])
        # custom unit
        _units = test_struct[0].get("unit")
        if _units:
            if hasattr(metafunc.config, "unit"):
                metafunc.config.unit = _units
        # parametrize
        metafunc.parametrize("cmd", test_struct, ids=test_names)


def pytest_benchmark_scale_unit(config, unit, benchmarks, best, worst, sort):

    # Monkey patch to allow custom measure units other than time/seconds
    # This allows to benchmark sensor measurements too

    custom_unit = benchmarks[0]["extra_info"].get("unit")
    if custom_unit is not None and unit == "seconds":
        custom_unit = custom_unit.split(":")
        if len(custom_unit) > 1:
            measure, _c_unit = custom_unit[0], custom_unit[1]
        else:
            measure = "measure"
            _c_unit = custom_unit[0]
        time_unit_key = sort
        if sort in ("name", "fullname"):
            time_unit_key = "min"
        _prefix, _scale = utils.time_unit(best.get(sort, benchmarks[0][time_unit_key]))
        if hasattr(config, "getoption"):
            return measure, f"{_prefix}{_c_unit}", _scale
        else:
            return measure, f"{_prefix}{_c_unit}", _scale

    if hasattr(config, "getoption"):
        custom_unit = config.getoption("--unit")
    if custom_unit is not None and unit == "seconds":
        custom_unit = custom_unit.split(":")
        if len(custom_unit) > 1:
            measure, _c_unit = custom_unit[0], custom_unit[1]
        else:
            measure = "measure"
            _c_unit = custom_unit[0]
        time_unit_key = sort
        if sort in ("name", "fullname"):
            time_unit_key = "min"
        _prefix, _scale = utils.time_unit(best.get(sort, benchmarks[0][time_unit_key]))
        return measure, f"{_prefix}{_c_unit}", _scale

    if unit == 'seconds':
        time_unit_key = sort
        if sort in ("name", "fullname"):
            time_unit_key = "min"
        _prefix, _scale = utils.time_unit(best.get(sort, benchmarks[0][time_unit_key]))
        if hasattr(config, "getoption"):
            return "time", f"{_prefix}s", _scale
        else:
            return "time", f"{_prefix}s", _scale
    elif unit == 'operations':
        return utils.operations_unit(worst.get('ops', benchmarks[0]['ops']))
    else:
        raise RuntimeError("Unexpected measurement unit %r" % unit)
