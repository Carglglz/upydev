from config.configfuncs import set_config


def get_val(conf, k):
    conf_str = f"{conf}"
    # print(conf_str, k)
    start = conf_str.find(k) + len(k)
    offset_end = conf_str[start:].find(',')
    if offset_end < 0:
        offset_end = conf_str[start:].find(')')
    end = start + offset_end
    # print(conf_str[start:end].replace('=', ''))
    return conf_str[start:end].replace('=', '')
