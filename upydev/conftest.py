import pytest
import yaml
from braceexpand import braceexpand
import ast


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


def pytest_addoption(parser):
    parser.addoption("--dev", action="store", default="default",
                     help="indicate the device with which to run the test")
    parser.addoption("--wss", action="store_true", default=False,
                     help="to indicate use of ssl if WebSecureREPL enabled in WebSocketDevice")
    parser.addoption("--devp", action="store", default="default",
                     help="indicate the device with which to run the test")
    parser.addoption("--yf", help="indicate a test yaml file to use", nargs='*')


@pytest.fixture
def devname(request):
    return request.config.getoption("--dev")


@pytest.fixture
def use_ssl(request):
    return request.config.getoption("--wss")


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
        # parametrize
        metafunc.parametrize("cmd", test_struct, ids=test_names)
