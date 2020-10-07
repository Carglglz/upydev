

REPLS_HELP = """
> REPLS: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - wrepl : to enter the terminal WebREPL; CTRL-x to exit, CTRL-d to do soft reset
                To see more keybindings info do CTRL-k
                (Added custom keybindings and autocompletion on tab to the previous work
                see: https://github.com/Hermann-SW/webrepl for the original work)

        - wssrepl : to enter the terminal WebSecureREPL; CTRL-x to exit, CTRL-d to do soft reset
                To see more keybindings info do CTRL-k. REPL over WebSecureSockets (This needs use of
                'sslgen_key -tfkey', 'update_upyutils' and enable WebSecureREPL in the device
                "import wss_repl;wss_repl.start(ssl=True)")

        - srepl : to enter the terminal serial repl using picocom, indicate port by -port option
                (to exit do CTRL-a, CTRL-x)
"""
