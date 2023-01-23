import aioctl


@aioctl.aiotask
async def ret_int():
    return 1


@aioctl.aiotask
async def ret_float():
    return 1.0


@aioctl.aiotask
async def ret_string():
    return "hello"


@aioctl.aiotask
async def ret_list():
    return [1, 2, 3]


@aioctl.aiotask
async def ret_tuple():
    return (1, 2, 3)


@aioctl.aiotask
async def ret_dict():
    return {"a": 1, "b": 2, "c": 3}


@aioctl.aiotask
async def ret_bytes():
    return 'b"hello"'


@aioctl.aiotask
async def ret_bytesx():
    return 'b"\x00\x00\x00"'


aioctl.add(ret_int, name="ret_int")
aioctl.add(ret_float, name="ret_float")
aioctl.add(ret_string, name="ret_string")
aioctl.add(ret_list, name="ret_list")
aioctl.add(ret_tuple, name="ret_tuple")
aioctl.add(ret_dict, name="ret_dict")
aioctl.add(ret_bytes, name="ret_bytes")
aioctl.add(ret_bytesx, name="ret_bytesx")

aioctl.run()
