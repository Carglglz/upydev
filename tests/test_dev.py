from upydevice import Device
import logging
import sys
import upydev
import json
import os
import ast
import array


_SSL = False
CHECK = "[\033[92m\u2714\x1b[0m]"
XF = "[\u001b[31;1m\u2718\u001b[0m]"
_EXP_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
    "float": float,
    "tuple": tuple,
    "list": list,
    "bytes": bytes,
    "bytearray": bytearray,
    "dict": dict,
    "array": array.array,
}

# Logging Setup


log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels["info"])
logging.basicConfig(
    level=log_levels["debug"],
    format="%(asctime)s [%(name)s] [%(threadName)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler],
)
formatter = logging.Formatter(
    "%(asctime)s [%(name)s] [%(dev)s] [%(devp)s] : %(message)s"
)
handler.setFormatter(formatter)
log = logging.getLogger("pytest")


def parse_assert(in_str):
    try:
        output = ast.literal_eval(in_str)
        return output
    except Exception:
        if "bytearray" in in_str:
            try:
                output = bytearray(
                    ast.literal_eval(in_str.strip().split("bytearray")[1])
                )
                return output
            except Exception:
                return in_str
        else:
            if "array" in in_str:
                try:
                    arr = ast.literal_eval(in_str.strip().split("array")[1])
                    output = array.array(arr[0], arr[1])
                    return output
                except Exception:
                    return in_str
            return in_str


def _assert_op(expected, result, op):
    if op == ">":
        return expected > result

    if op == "<":
        return expected < result

    if op == ">=":
        return expected >= result

    if op == "<=":
        return expected <= result

    if op == "!=":
        return expected != result

    if op == "in":
        return result in expected

    if op == "is":
        return result is expected

    if op == "is not":
        return result is not expected

    if op == "startswith":
        return result.startswith(expected)

    if op == "endswith":
        return result.endswith(expected)


def assert_op(expected, result, op, log, test_name):
    RESULT_MSG = f"expected: {expected} {op} result: {result}"
    FAIL_MSG = f"Test {test_name} FAILED: {RESULT_MSG}"
    log.info(RESULT_MSG)
    ret = _assert_op(expected, result, op)
    if op in ["in", "is", "is not", "startswith", "endswith"]:
        RESULT_MSG = f"result: {result} {op} expected: {expected}"
        FAIL_MSG = f"Test {test_name} FAILED: {RESULT_MSG}"
        assert ret, FAIL_MSG
    else:
        assert ret, FAIL_MSG

    # INIT DEV


def test_devname(devname):
    global dev, log
    group_file = "UPY_G"
    # print(group_file)
    if "{}.config".format(group_file) not in os.listdir():
        group_file = "{}/{}".format(upydev.__path__[0], group_file)
    with open("{}.config".format(group_file), "r", encoding="utf-8") as group:
        devices = json.loads(group.read())
        # print(devices)
    devs = devices.keys()
    # NAME ENTRY POINT
    if devname in devs:
        dev_addr = devices[devname][0]
        dev_pass = devices[devname][1]
    else:
        if devname != "default":
            # load upydev_.config
            file_conf = "upydev_.config"
            if file_conf not in os.listdir():
                file_conf = os.path.join(upydev.__path__[0], "upydev_.config")

            with open(file_conf, "r") as config_file:
                upy_conf = json.loads(config_file.read())
                dev_addr = upy_conf["addr"]
                dev_pass = upy_conf["passwd"]

    dev = Device(dev_addr, dev_pass, init=True, autodetect=True)

    extra = {"dev": devname, "devp": dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)


def do_pass(test_name):
    log.info("{} TEST: {}".format(test_name, CHECK))


def do_fail(test_name):
    log.error("{} TEST: {}".format(test_name, XF))


def test_platform():
    TEST_NAME = "DEV PLATFORM"
    try:
        log.info(f"Running {dev.dev_class} test...")
        log.info("DEV PLATFORM: {}".format(dev.dev_platform))
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e


def test_dev(cmd):
    TEST_NAME = cmd.get("name")
    LOAD = cmd.get("load")
    HINT = cmd.get("hint")
    ARGS = cmd.get("args")
    COMMAND = cmd.get("command")
    DEVICE_RESULT = cmd.get("result")
    EXP_RESULT = cmd.get("exp")
    EXP_TYPE = cmd.get("exp_type")
    ASSERT_OP = cmd.get("assert_op")
    ASSERT_ITR = cmd.get("assert_itr")
    RELOAD = cmd.get("reload")

    # Parse assert result
    if isinstance(EXP_RESULT, str):
        try:
            EXP_RESULT = parse_assert(EXP_RESULT)
        except Exception:
            pass

    try:
        log.info(f"Running [{TEST_NAME}] test...")
        if LOAD:
            # Load can be a file or a snippet in yaml file.
            if os.path.exists(LOAD):
                log.info(f"Loading {LOAD} file...")
                dev.load(LOAD)
            else:
                log.info(f"Loading {LOAD[:10]}... snippet")
                dev.paste_buff(LOAD)
                dev.wr_cmd("\x04", follow=True)
        if HINT:
            log.info(f"Hint: {HINT}")
        if ARGS:
            COMMAND = f"{COMMAND}(*{ARGS})"
        if COMMAND:
            log.info(f"Command [{COMMAND}] ")
            dev.wr_cmd(COMMAND, follow=True)
            # Catch Device Exceptions and raise:
            dev.raise_traceback()
        if DEVICE_RESULT:
            RESULT = dev.wr_cmd(DEVICE_RESULT, silent=True, rtn_resp=True)
            if EXP_TYPE:
                RESULT_MSG = f"expected: {EXP_TYPE} --> result: {type(RESULT)}"
                log.info(RESULT_MSG)
                assert isinstance(
                    RESULT, _EXP_TYPES[EXP_TYPE]
                ), f"Test {TEST_NAME} FAILED: {RESULT_MSG}"
            if EXP_RESULT:
                # ASSERT_OP
                if not ASSERT_OP:
                    RESULT_MSG = f"expected: {EXP_RESULT} == result: {RESULT}"
                    log.info(RESULT_MSG)
                    assert (
                        EXP_RESULT == RESULT
                    ), f"Test {TEST_NAME} FAILED: {RESULT_MSG}"
                else:
                    if not ASSERT_ITR:
                        assert_op(EXP_RESULT, RESULT, ASSERT_OP, log, TEST_NAME)
                    else:
                        RESULT_MSG = (
                            f"expected: {EXP_RESULT} {ASSERT_OP} "
                            f" ({ASSERT_ITR}) result: {RESULT}"
                        )
                        log.info(RESULT_MSG)
                        _result = [
                            _assert_op(EXP_RESULT, res, ASSERT_OP) for res in RESULT
                        ]
                        if ASSERT_ITR == "any":
                            assert any(
                                _result), f"Test {TEST_NAME} FAILED: {RESULT_MSG}"
                        if ASSERT_ITR == "all":
                            assert all(
                                _result), f"Test {TEST_NAME} FAILED: {RESULT_MSG}"

        if RELOAD:
            dev.cmd(f"import sys,gc;del(sys.modules['{RELOAD}']);" f"gc.collect()")
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        if RELOAD:
            dev.cmd(f"import sys,gc;del(sys.modules['{RELOAD}']);" f"gc.collect()")
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e


def test_disconnect():
    TEST_NAME = "DEVICE DISCONNECT"
    log.info("{} TEST".format(TEST_NAME))
    try:
        dev.disconnect()
        assert not dev.connected, "Device Still Connected"
        do_pass(TEST_NAME)
        print("Test Result: ", end="")
    except Exception as e:
        do_fail(TEST_NAME)
        print("Test Result: ", end="")
        raise e
