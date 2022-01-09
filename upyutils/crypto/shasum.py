import hashlib
from binascii import hexlify


def shasum(file, debug=True, save=False, rtn=False, filetosave=False):
    _hash = hashlib.sha256()
    with open(file, 'rb') as bfile:
        buff = bfile.read(1)
        _hash.update(buff)
        while buff != b'':
            try:
                buff = bfile.read(256)
                if buff != b'':
                    _hash.update(buff)
            except Exception as e:
                print(e)

    _result = _hash.digest()
    result = hexlify(_result).decode()
    if debug:
        print(f"{result}  {file}")
    if save:
        if not filetosave:
            with open(f"{file}.sha256", 'w') as shafile:
                shafile.write(f"{result}  {file}")
        else:
            with open(filetosave, 'a') as shafile:
                shafile.write(f"{result}  {file}")
    if rtn:
        return result


def shasum_check(shafile):
    with open(shafile, 'r') as shafile_check:
        shasum_lines = shafile_check.readlines()
        for shaline in shasum_lines:
            _sha256, filename = shaline.split()
            _shacheck = shasum(filename, debug=False, rtn=True)
            if _sha256 == _shacheck:
                print(f"{filename}: OK")
            else:
                print(f"{filename}: Failed")
