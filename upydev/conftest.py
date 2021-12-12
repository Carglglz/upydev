import pytest


def pytest_addoption(parser):
    parser.addoption("--dev", action="store", default="default",
                     help="indicate the device with which to run the test")
    parser.addoption("--wss", action="store_true", default=False,
                     help="to indicate use of ssl if WebSecureREPL enabled in WebSocketDevice")
    parser.addoption("--devp", action="store", default="default",
                     help="indicate the device with which to run the test")


@pytest.fixture
def devname(request):
    return request.config.getoption("--dev")


@pytest.fixture
def use_ssl(request):
    return request.config.getoption("--wss")
