# Define configuration functions
# patterns
# config files --> [param]_config.py
# config param --> named tuples in params.py
# function --> set_config(param, *kargs)
# with open param_config.py
# from params import [PARAM]_CONF --> namedtuple
# write [PARAM] = [PARAM]_CONF({*["=".join([k,v]) for k,v in **kargs]})


def set_val(val):
    if isinstance(val, str):
        return f"'{val}'"
    else:
        return str(val)


def set_config(param, **kargs):
    _conftuple = f"{param.upper()}_CONF"
    _paramconf = f"{param.upper()}"
    _conf = (f"{_paramconf} = {_conftuple}("
             + f"{', '.join(['='.join([k,set_val(v)]) for k,v in kargs.items()])})")
    # print(_conf)
    # print(_paramconf)
    name_conf = f"{param}_config.py"
    with open(name_conf, "w") as configfile:
        configfile.write('from collections import namedtuple\n\n')
        configfile.write(f'{_conftuple} = namedtuple'
                         + f'("{_paramconf}CONFIG", '
                         + f'({", ".join([set_val(k) for k in kargs.keys()])}))\n')
        configfile.write(_conf)
    print(_conf)


def add_param(param):
    _config_param = (f"def set_{param}(**kargs):\n"
                     + f"    try:\n"
                     + f"        from {param}_config import {param.upper()}\n"
                     + f"        for k in dir({param.upper()}):\n"
                     + f"            if k != '__class__':\n"
                     + f"                if k not in kargs.keys():\n"
                     + f"                    kargs[k] = eval(get_val({param.upper()}, k))\n"
                     + f"    except Exception:\n"
                     + f"        pass\n"
                     + f"    set_config('{param}', **kargs)\n")
    with open("/lib/config/params.py", 'a') as paramfile:
        paramfile.write('\n\n')
        paramfile.write(_config_param)
