from prompt_toolkit.shortcuts import (radiolist_dialog, message_dialog,
                                      input_dialog, yes_no_dialog, button_dialog)
import ast
from upydev.shell.constants import AUTHMODE_DICT
from binascii import hexlify
import time


def config_parser(dev, conf):
    config_params = [param for param in dev.wr_cmd(f"dir({conf.upper()})",
                                                   silent=True, rtn_resp=True)
                     if param != '__class__']
    return config_params


def param_parser(conf_str, k):
    start = conf_str.find(k) + len(k)
    offset_end = conf_str[start:].find(',')
    if offset_end < 0:
        offset_end = conf_str[start:].find(')')
    end = start + offset_end
    return ast.literal_eval(conf_str[start:end].replace('=', ''))


def set_val(val):
    if isinstance(val, str):
        return f"'{val}'"
    else:
        return str(val)


def show_upy_config_dialog(dev, dev_platform):
    _TITLE = f"upydev {dev_platform} Configuration Tool"
    results_array = radiolist_dialog(
            title=_TITLE,
            text="Select an option and press Select (Use tab to change focus)",
            ok_text="Select",
            cancel_text="Finish",
            values=[
                ("network", "{:25}{}".format("1 Network Options",
                                             "Configure network settings")),
                ("interface", "{:25}{}".format("2 Interfacing Options",
                                               "Configure connections to peripherals")),
                ("params", "{:25}{}".format("3 Custom Parameters",
                                            "Configure custom parameters of "
                                            "config files"))
            ]
        ).run()
    if results_array is not None:
        # print('Configure dialog: {}'.format(results_array))
        if results_array == 'network':
            if dev.address == '192.168.4.1' or dev.dev_class != 'WebSocketDevice':
                results_array = radiolist_dialog(
                        title="upydev {} Configuration Tool".format(
                            dev_platform),
                        text="Select an option and press Select (Use tab to change focus)",
                        ok_text="Select",
                        cancel_text="Finish",
                        values=[
                            ("STA", "{:10}{}".format("1 STA:",
                                                     "Configure network SSID and PASSWORD to connect to a WLAN"))
                        ]
                    ).run()
            else:
                results_array = radiolist_dialog(
                        title="upydev {} Configuration Tool".format(
                            dev_platform),
                        text="Select an option and press Select (Use tab to change focus)",
                        ok_text="Select",
                        cancel_text="Finish",
                        values=[
                            ("AP", "{:10}{}".format("1 AP:",
                                                    "Configure SSID and PASSWORD to enable {} access Point".format(dev_platform)))
                        ]
                    ).run()
            if results_array == 'STA':
                print('Scanning WLANs...')
                if dev_platform == 'esp8266':
                    enable_sta = dev.wr_cmd("import network;network.WLAN(network.STA_IF"
                                            ").active()", rtn_resp=True, silent=True)
                else:
                    enable_sta = dev.wr_cmd("import network;network.WLAN(network.STA_IF"
                                            ").active()", rtn_resp=True, silent=True)
                if enable_sta:
                    scan = dev.wr_cmd(
                        "network.WLAN(network.STA_IF).scan()", rtn_resp=True,
                        silent=True)
                    if len(scan) == 0:
                        message_dialog(title=_TITLE,
                                       text="No WLAN available").run()
                    else:
                        scan_list = []
                        for netscan in scan:
                            auth = AUTHMODE_DICT[netscan[4]]
                            vals = hexlify(netscan[1]).decode()
                            bssid = ':'.join([vals[i:i+2]
                                              for i in range(0, len(vals), 2)])
                            scan_list.append((netscan[0].decode(), '{0:20}[{1}] RSSI:{2} AUTH: {3}'.format(
                                netscan[0].decode(), bssid, netscan[3],
                                auth)))

                        results_array = radiolist_dialog(
                                title="upydev {} Configuration Tool".format(
                                    dev_platform),
                                text="Select an option and press Select (Use tab to change focus)",
                                ok_text="Select",
                                cancel_text="Finish",
                                values=scan_list
                            ).run()
                        if results_array is not None:
                            ssid = results_array
                            passwd = input_dialog(
                                    title="upydev {} Configuration Tool".format(
                                        dev_platform),
                                    text='Please type {} Password:'.format(ssid)).run()
                            connect_to = "network.WLAN(network.STA_IF).connect('{}', '{}')".format(
                                ssid, passwd)
                            if passwd is not None:
                                print('Connecting to {}...'.format(ssid))
                                disconn_cmd = "network.WLAN(network.STA_IF).disconnect()"
                                conn_cmd = "{};gc.collect()".format(connect_to)
                                dconn_sta = dev.wr_cmd(disconn_cmd)
                                # dev.wr_cmd('\r\r')
                                time.sleep(1)
                                dev.wr_cmd('\r\r')
                                is_connected = False
                                conn_sta = dev.wr_cmd(conn_cmd)
                                time.sleep(1)
                                dev.wr_cmd('\r\r')
                                while not is_connected:
                                    is_connected = dev.wr_cmd(
                                        "network.WLAN(network.STA_IF).isconnected()",
                                        rtn_resp=True, silent=True)
                                    time.sleep(1)

                                saveconfig = yes_no_dialog(title=_TITLE,
                                                           text="{} connected successfully to {}\n Do you want to save configuration?".format(dev_platform, ssid)).run()

                                if saveconfig:
                                    save_option = button_dialog(
                                                    title=_TITLE,
                                                    text='wifi_.config or '
                                                          'wpa_supplicant.config ?',
                                                    buttons=[
                                                        ('wifi', 'wifi'),
                                                        ('wpa supplicant', 'wpa'),
                                                        ('Cancel', None)
                                                    ],
                                                ).run()
                                    if save_option:
                                        if 'wifi' == save_option:
                                            saveconfig_cmd = (f"import json;"
                                                              f"sta_config=open('wifi_."
                                                              f"config', 'w');sta_confi"
                                                              f"g.write(json.dumps(dict"
                                                              f"(ssid='{ssid}', "
                                                              f"password='{passwd}')));"
                                                              f"sta_config.close()")

                                        elif 'wpa' == save_option:
                                            saveconfig_cmd = (f"import json;"
                                                              f"wpa_config=open('wpa_su"
                                                              f"pplicant.config', 'r');"
                                                              f"wpas=json.loads(wpa_con"
                                                              "fig.read());"
                                                              f"wpas['{ssid}']="
                                                              f"'{passwd}';"
                                                              f"wpa_config.seek(0);"
                                                              f"wpa_config.write("
                                                              f"json.dumps(wpas));"
                                                              f"wpa_config.close()")
                                        dev.wr_cmd(saveconfig_cmd, silent=True)
                                        message_dialog(title=_TITLE,
                                                       text=f"{ssid} configuration "
                                                            "saved successfully").run()

                else:
                    message_dialog(title=_TITLE,
                                   text="Can't enable STA interface").run()

            elif results_array == 'AP':
                ssid = input_dialog(
                        title="upydev {} Configuration Tool".format(
                            dev_platform),
                        text='Please set {} SSID:'.format(dev_platform)).run()
                passwd = input_dialog(
                        title="upydev {} Configuration Tool".format(
                            dev_platform),
                        text='Please set {} Password:'.format(ssid)).run()
                while passwd is not None and len(passwd) < 8:
                    passwd = input_dialog(
                            title="upydev {} Configuration Tool".format(
                                dev_platform),
                            text='Please set {} Password (More than 8 characters):'.format(ssid)).run()

                if ssid is not None and passwd is not None:
                    ap_enbale = dev.wr_cmd(
                        "import network;network.WLAN(network.AP_IF).active(0)",
                        rtn_resp=True)
                    time.sleep(0.5)
                    ap_enbale = dev.wr_cmd(
                        "import network;network.WLAN(network.AP_IF).active(1)",
                        rtn_resp=True)
                    print('Configuring {} AP...'.format(ssid))
                    time.sleep(0.5)
                    ap_config = "import network;network.WLAN(network.AP_IF).config(essid='{}',authmode=network.AUTH_WPA_WPA2_PSK, password='{}')".format(
                        ssid, passwd)
                    resp = dev.wr_cmd(ap_config)
                    time.sleep(1)
                    saveconfig = yes_no_dialog(title=_TITLE,
                                               text="{} AP:{} enabled successfully\n Do you want to save configuration?".format(dev_platform, ssid)).run()

                    if saveconfig:
                        saveconfig_cmd = "import json;sta_config=open('ap_.config', 'w');sta_config.write(json.dumps(dict(ssid='{}', password='{}')));sta_config.close()".format(
                            ssid, passwd)
                        dev.wr_cmd(saveconfig_cmd)
                        message_dialog(title=_TITLE,
                                       text="{} Configuration saved successfully".format(ssid)).run()
        elif results_array == 'interface':
            results_array = radiolist_dialog(
                    title="upydev {} Configuration Tool".format(
                        dev_platform),
                    text="Select an option and press Select (Use tab to change focus)",
                    ok_text="Select",
                    cancel_text="Finish",
                    values=[
                        ("I2C", "{:10}{}".format("1 I2C:",
                                                 "Configure I2C interface"))
                    ]
                ).run()

            if results_array == 'I2C':
                if dev_platform == 'esp32':
                    default = 'I2C: SCL = 22 , SDA = 23, FREQ = 100000'
                    scl = 22
                    sda = 23
                elif dev_platform == 'esp8266':
                    default = 'I2C: SCL = 5 , SDA = 4, FREQ = 100000'
                    scl = 5
                    sda = 4
                elif dev_platform == 'pyboard':
                    default = 'I2C: SCL = X1 , SDA = X2, FREQ = 100000'
                    scl = 'X9'
                    sda = 'X10'
                results_array = radiolist_dialog(
                        title="upydev {} Configuration Tool".format(
                            dev_platform),
                        text="Select an option and press Select (Use tab to change focus)",
                        ok_text="Select",
                        cancel_text="Finish",
                        values=[
                            ("I2C_DEF", "{:10}{}".format("1 I2C DEFAULT:",
                                                         default)),
                            ("I2C_CUSTOM", "{:10}{}".format("2 I2C CUSTOM:",
                                                            "SET SCL, SDA and FREQ"))
                        ]
                    ).run()
                if results_array == 'I2C_DEF':
                    if dev_platform == 'pyboard':

                        dev.wr_cmd(
                            "from machine import I2C;i2c = I2C(scl='{}', sda='{}')".format(scl, sda))

                    else:

                        dev.wr_cmd(
                            "from machine import Pin, I2C;i2c = I2C(scl=Pin({}), sda=Pin({}))".format(scl, sda))

                    message_dialog(title=_TITLE,
                                   text="I2C Default configuration enabled successfully as 'i2c'").run()
                elif results_array == 'I2C_CUSTOM':
                    custom_i2c = input_dialog(
                            title="upydev {} Configuration Tool".format(
                                dev_platform),
                            text='Please set SCL SDA and FREQ separated by space, e.g. : 22 23 100000:').run()
                    if custom_i2c is None or custom_i2c == '':
                        freq = 100000
                        custom_i2c = "{} {} {}".format(scl, sda, freq)
                    else:
                        scl = custom_i2c.split()[0]
                        sda = custom_i2c.split()[1]
                        freq = custom_i2c.split()[2]
                    if dev_platform == 'pyboard':

                        dev.wr_cmd(
                            "from machine import I2C;i2c_custom = I2C(scl='{}', sda='{}', freq={})".format(scl, sda, freq))
                    else:

                        dev.wr_cmd(
                            "from machine import Pin, I2C;i2c_custom = I2C(scl=Pin({}), sda=Pin({}), freq={})".format(scl, sda, freq))

                    message_dialog(title=_TITLE,
                                   text="I2C Custom configuration enabled successfully as 'i2c_custom'").run()

        elif results_array == 'params':
            print('upy-config: loading custom configuration...')
            params_config_l = dev.wr_cmd("[conf for conf in os.listdir() "
                                         "if conf.endswith('_config.py')]",
                                         silent=True, rtn_resp=True)
            _params_config = [(param.split('_')[0], param.replace('.py', ''))
                              for param in params_config_l]
            params_config = {param: dev.wr_cmd(f"from {config} import {param.upper()}"
                                               f"; {param.upper()}", silent=True,
                                               rtn_resp=True)
                             for param, config in _params_config}
            # print(params_config)
            params_vals = [(param[0],
                            f"{str(n) + ' ' + param[0]:10}: Configure {param[0]}")
                           for n, param in enumerate(params_config.items())]
            n = len(params_vals)
            param_option = radiolist_dialog(
                    title=_TITLE,
                    text="Select an option and press Select (Use tab to change focus)",
                    ok_text="Select",
                    cancel_text="Finish",
                    values=params_vals + [('NEW', f"{str(n) + ' New configuration':10}:"
                                           " Create new configuration")]
                ).run()
            if param_option != 'NEW' and param_option:
                param_in_config = config_parser(dev, param_option)
                def_conf = {}
                new_conf = {}
                for param in param_in_config:
                    def_conf[param] = param_parser(params_config[param_option], param)
                for k, v in def_conf.items():
                    new_param_config = input_dialog(title=_TITLE,
                                                    text=f"{k}: ({v})").run()
                    try:
                        new_conf[k] = ast.literal_eval(new_param_config)
                    except ValueError:
                        new_conf[k] = new_param_config
                new_params_str = ','.join([f'{k}={set_val(v)}'
                                           for k, v in new_conf.items()])
                new_conf_str = (f"from config.params import set_{param_option}"
                                f";set_{param_option}({new_params_str})")
                dev.wr_cmd(new_conf_str)
                reload_cmd = (f"import sys;del(sys.modules['{param_option}_config']);"
                              f"gc.collect(); from {param_option}_config import "
                              f"{param_option.upper()}")
                dev.wr_cmd(reload_cmd, silent=True)
            elif param_option == 'NEW':
                # NEW CONFIG
                new_config = input_dialog(title=_TITLE,
                                          text="Name:").run()
                dev.wr_cmd(f"from config import add_param; add_param('{new_config }')")
                new_params = input_dialog(title=f"upydev {dev_platform} "
                                                "Configuration Tool",
                                                text="Parameters: parameter=value,"
                                                     " param...").run()
                reload_cmd = ("import sys;del(sys.modules['config.params']);"
                              "gc.collect()")
                dev.wr_cmd(reload_cmd, silent=True)
                dev.wr_cmd(f"from config.params import set_{new_config}"
                           f";set_{new_config}({new_params})")
