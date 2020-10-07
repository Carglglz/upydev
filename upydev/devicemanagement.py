

DEVICE_MANAGEMENT_HELP = """
> DEVICE MANAGMENT: Usage '$ upydev ACTION [opts]'
    ACTION:
    - config : to save upy device settings (see -t, -p, -g, -@, -gg),
                so the target and password arguments wont be required any more
                * -gg flag will add the device to the global group (UPY_G)
            (-t target -p password -g global directory -@ device name -gg global group)

    - check: to check current device information or with -@ entry point if stored in the global group.

    - set: to set current device configuration from a device saved in the global group with -@ entry point

    - make_group: to make a group of boards to send commands to. Use -f for the name
                  of the group and -devs option to indicate a name, ip and the
                  password of each board. (To store the group settings globally use -g option)

    - mg_group: to manage a group of boards to send commands to. Use -G for the name
                  of the group and -add option to add devices (indicate a name, ip and the
                  password of each board) or -rm to remove devices (indicated by name)

    - see: To get specific info about a devices group use -G option as "see -G [GROUP NAME]"

    - gg: To see global group
"""
