import pytest
import yaml


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

        metafunc.parametrize("cmd", test_struct, ids=test_names)
