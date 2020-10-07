

GROUP_MODE_HELP = """
> GROUP COMMAND MODE:
    To send a command to multiple devices in a group (made with make_group command)

    To target specific devices within a group add -devs option as -devs [DEV NAME] [DEV NAME] ...

    *(upydev will use local working directory configuration unless it does
    not find any or manually indicated with -g option)

    COMMAND MODE OPTION:
        -G : Usage '$ upydev ACTION -G GROUPNAME [opts]' or
                   '$ upydev ACTION -gg [opts]' for global group.
            This sends the command to one device at a time;

        -GP: Usage '$ upydev ACTION -GP GROUPNAME [opts]' or
                   '$ upydev ACTION -ggp [opts]' for global group.
            For parallel/non-blocking command execution using multiprocessing"""
