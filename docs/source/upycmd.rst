
Upy Commands
============


General Commands
----------------
        - **info**: to get device system info
        - **id**: to get device unique id
        - **upysh**: to enable the upy shell in the device (then do ``$ upydev man`` to access upysh manual info)
        - **reset**: to do a device soft reset
        - **kbi**: sends CTRL-C signal to stop an ongoing loop, to be able to access repl again
        - **uhelp**: MicroPython device help
        - **umodules**: MicroPython help('modules')
        - **ls**: ls improved with multiple dirs and pattern matching
        - **cat**: cat improved with multiple files and pattern matching
        - **mem**: to get device RAM memory info
        - **du**: to get the size of file in root dir (default) or sd with ``-s sd`` option. If no file name indicated with ``-f`` option, prints all files
        - **df**: to get memory info of the file system, (total capacity, free, used) (default root dir, ``-s`` option to change)
        - **tree**: to get directory structure in tree format (requires ``upysh2.py``)
        - **ifconfig**: to get device network interface configuration info if station is enabled and connected to an AP
        - **net scan**: to do a WiFi scan and get available AP nearby.
        - **net on**: to enable STA interface
        - **net off**: to disable STA interface
        - **net config**: to configure and connect to an AP, must provide essid and password (see ``-wp``)
        - **net status**: to get STA state. It returns True if enabled, False if disabled
        - **ap on**: to enable AP
        - **ap off**: to disable AP
        - **ap status**: AP state ; returns True if enabled, False if disabled
        - **ap config**: AP configuration of essid and password with authmode WPA/WPA2/PSK, (see ``-ap``), needs first that the AP is enabled (do ``$ upydev ap_on``)
        - **ap scan**: scan devices connected to AP; returns number of devices and mac address
        - **i2c config**: to configure the i2c pins (see ``-i2c``, defaults are SCL=22, SDA=23)
        - **i2c scan**: to scan i2c devices (must config i2c pins first)
        - **set rtc localtime**: to pass host localtime and set upy device rtc
        - **set rtc ntptime**: to set rtc from server, (see ``-utc`` for time zone)
        - **datetime**: to get date and time (must be set first, see above commands)
        - **set hostname**: to set hostname of the device for dhcp service *(needs wpa_supplicant.py)*
        - **set localname**: to set localname of the device for ble gap/advertising name *(needs ble_uart_peripheral.py)*
        - **shasum -c**: to check shasum file
        - **shasum**: to compute hash SHA-256 of a device file
        - **sd**: commands to manage an sd
        - **diff**: use git diff between device's [~file/s] and local file/s
        - **enable_sh**: upload required files so shell is fully operational
        - **uconfig**: set or check config (from *_config.py* files in device)


SD
---


    - **sd enable**: to enable/disable the LDO 3.3V regulator that powers the SD module use ``-po`` option to indicate the Pin.

    - **sd init**: to initialize the sd card; (spi must be configured first) it creates an sd object and mounts it as a filesystem.

    - **sd deinit**: to unmount sd card.

    - **sd auto**: experimental command, needs a sd module with sd detection pin. Enable an Interrupt with the sd detection pin, so it mounts the sd when is detected, and unmount the sd card when it is extracted.

.. note::

  These commands needs ``sdcard.py`` in the device, see upyutils directory in upydev github repo. ``sd_auto`` also needs ``SD_AM.py`` in the device.
