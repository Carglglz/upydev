UID = "from machine import unique_id;\
from ubinascii import hexlify;hexlify(unique_id());gc.collect()"

UPYSH = "from upysh import *;gc.collect()"

HELP = "help();gc.collect()"

MODULES = "help('modules');gc.collect()"

MEM = "from micropython import mem_info;mem_info();gc.collect()"

OS_STAT = "import os;os.stat('{}');gc.collect()"

FILE_STAT = "import os;[(filename,os.stat('{0}'+str(filename))[6]) for filename in os.listdir('{0}')]"

CHECK_DIR = "import os;'{}' in os.listdir('/');gc.collect()"

STAT_FS = "import os;os.statvfs('{}');gc.collect()"

IFCONFIG = "network.WLAN(network.STA_IF).ifconfig()"

SSID = "network.WLAN(network.STA_IF).config('essid')"

BSSID = "network.WLAN(network.STA_IF).config('mac')"

RSSI = "network.WLAN(network.STA_IF).status('rssi')"

NET_INFO = "import network;[{},{},{},{}];gc.collect()".format(IFCONFIG,
                                                              SSID,
                                                              BSSID,
                                                              RSSI)

NET_SCAN = "import network;network.WLAN(network.STA_IF).scan();gc.collect()"

NET_STAT_ON = "import network;network.WLAN(network.STA_IF).active(True);gc.collect()"

NET_STAT_OFF = "import network;network.WLAN(network.STA_IF).active(False);gc.collect()"

NET_STAT_CONN = "import network;network.WLAN(network.STA_IF).connect('{}', '{}');gc.collect()"

NET_STAT = "import network;network.WLAN(network.STA_IF).active();gc.collect()"

AP_ON = "import network;network.WLAN(network.AP_IF).active(True);gc.collect()"

AP_OFF = "import network;network.WLAN(network.AP_IF).active(False);gc.collect()"

AP_STATE = "network.WLAN(network.AP_IF).active()"

AP_SSID = "network.WLAN(network.AP_IF).config('essid')"

AP_CHANNEL = "network.WLAN(network.AP_IF).config('channel')"

AP_AUTHMODE = "network.WLAN(network.AP_IF).config('authmode')"

AP_IFCONFIG = "network.WLAN(network.AP_IF).ifconfig()"

APSTAT = "import network;[{},{},{},{},{}];gc.collect()".format(
    AP_STATE, AP_SSID, AP_CHANNEL, AP_AUTHMODE, AP_IFCONFIG)

AP_CONFIG = "network.WLAN(network.AP_IF).config(essid='{}',authmode=network.AUTH_WPA_WPA2_PSK, password='{}')"

AP_SCAN = "import network;network.WLAN(network.AP_IF).status('stations');gc.collect()"

I2C_CONFIG = "from machine import I2C,Pin;i2c = I2C(scl=Pin({}),sda=Pin({}));gc.collect()"

I2C_CONFIG_PYB = "from machine import I2C;i2c = I2C(scl='{}', sda='{}');gc.collect()"

I2C_SCAN = "i2c.scan();gc.collect()"

SPI_CONFIG = "from machine import SPI,Pin;spi = SPI(1, baudrate=10000000, sck=Pin({}), mosi=Pin({}), miso=Pin({})); cs = Pin({}, Pin.OUT)"

SET_RTC_LT = "from machine import RTC;rtc = RTC();rtc.datetime(({}, {}, {}, {}, {}, {}, {}+1, {}));gc.collect()"

RTC = "from machine import RTC;rtc = RTC();"

NTPTIME = "from ntptime import settime;settime();"

RTC_CONFIG = "(year, month, mday, week_of_year, hour, minute, second, milisecond) = rtc.datetime();"

UTC_ZONE = "rtc.datetime((year, month, mday, week_of_year,hour+{}, minute, second, milisecond));gc.collect()"

SET_RTC_NT = RTC + NTPTIME + RTC_CONFIG + UTC_ZONE

DATETIME = "import time; tnow = time.localtime();tnow[:6];gc.collect()"

WLAN_INIT = "from wifiutils import WIFI_UTIL; u_wlan = WIFI_UTIL(silent=False);gc.collect()"

WLAN_CONFIG = "u_wlan.sta_config('{}', '{}');gc.collect()"

WLAN_AP_CONFIG = "u_wlan.ap_config('{}', '{}');gc.collect()"

WLAN_CONN = "u_wlan.STA_conn();gc.collect()"

WLAN_AP_CONN = "u_wlan.AP_conn();gc.collect()"

SD_ENABLE_CONF = "from machine import Pin;sd_enable=Pin({}, Pin.OUT);"
SD_ENABLE_TOGGLE = "sd_enable.value(not sd_enable.value());sd_enable.value();gc.collect()"
SD_ENABLE = SD_ENABLE_CONF + SD_ENABLE_TOGGLE

SD_SDINIT = "import sdcard,os;sd = sdcard.SDCard(spi, cs);time.sleep_ms(1000);"
SD_MOUNT = "os.mount(sd, '/sd');'sd' in os.listdir('/');gc.collect()"
SD_INIT = SD_SDINIT + SD_MOUNT

SD_DEINIT = "import os;os.umount('/sd');sd_enable.off();sd_enable.value();gc.collect()"
SD_AUTO = "import SD_AM;gc.collect()"

CHECK_UPYSH2 = "import os;'upysh2.py' in os.listdir('lib');gc.collect()"

SET_HOSTNAME = "f=open('hostname.py','wb');f.write(b'{}');f.close();"

SET_LOCALNAME = "f=open('localname.py','wb');f.write(b'{}');f.close();"

SHASUM_CHECK = "from shasum import shasum_check;shasum_check('{}');gc.collect()"
SHASUM = "from shasum import shasum;shasum({});gc.collect()"
LS = "ls({}, gts={}, hidden={});gc.collect()"
CAT = "cat({});gc.collect()"
TOUCH = "from upysh2 import touch;touch({});gc.collect()"
HEAD = "cat({},n={},prog='head');gc.collect()"
VIM = "cat({},prog='vim');gc.collect()"

CMDDICT_ = {'UID': UID, 'UPYSH': UPYSH, 'HELP': HELP, 'MOD': MODULES,
            'MEM': MEM, 'OS_STAT': OS_STAT, 'FILE_STAT': FILE_STAT,
            'CHECK_DIR': CHECK_DIR, 'STAT_FS': STAT_FS,
            'NET_INFO': NET_INFO, 'NET_SCAN': NET_SCAN,
            'NET_STAT_ON': NET_STAT_ON, 'NET_STAT_OFF': NET_STAT_OFF,
            'NET_STAT_CONN': NET_STAT_CONN, 'NET_STAT': NET_STAT,
            'AP_ON': AP_ON, 'AP_OFF': AP_OFF, 'APSTAT': APSTAT,
            'AP_CONFIG': AP_CONFIG, 'AP_SCAN': AP_SCAN,
            'I2C_CONFIG': I2C_CONFIG, 'I2C_SCAN': I2C_SCAN,
            'SPI_CONFIG': SPI_CONFIG, 'SET_RTC_LT': SET_RTC_LT,
            'SET_RTC_NT': SET_RTC_NT, 'DATETIME': DATETIME,
            'I2C_CONFIG_PYB': I2C_CONFIG_PYB, 'WLAN_INIT': WLAN_INIT,
            'WLAN_CONFIG': WLAN_CONFIG, 'WLAN_AP_CONFIG': WLAN_AP_CONFIG,
            'WLAN_CONN': WLAN_CONN, 'WLAN_AP_CONN': WLAN_AP_CONN,
            'SD_ENABLE': SD_ENABLE, 'SD_INIT': SD_INIT,
            'SD_DEINIT': SD_DEINIT, 'SD_AUTO': SD_AUTO, 'CHECK_UPYSH2': CHECK_UPYSH2,
            'SET_HOSTNAME': SET_HOSTNAME, 'SET_LOCALNAME': SET_LOCALNAME,
            'SHASUM_CHECK': SHASUM_CHECK,
            'SHASUM': SHASUM, 'LS': LS, 'CAT': CAT, 'TOUCH': TOUCH, 'HEAD': HEAD,
            'VIM': VIM}

_CMDDICT_ = {k: 'import gc;' + v for k, v in CMDDICT_.items()}
