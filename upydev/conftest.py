import pytest


def pytest_addoption(parser):
    parser.addoption("--dev", action="store", default="default",
                     help="indicate the device with which to run the test")


@pytest.fixture
def devname(request):
    return request.config.getoption("--dev")
