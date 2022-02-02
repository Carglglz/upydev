from upydev.shell.commands import ShellCmds, _SHELL_FLAGS


class ShellWsCmds(ShellCmds):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def custom_sh_cmd(self, cmd, rest_args=None, args=None, topargs=None):
        # To be implemented for each shell to manage special commands, e.g. fwr
        if cmd == 'exit':
            if args.r:
                print('Rebooting device...')
                self.dev.reset(silent=True, reconnect=False)
                print('Done!')
            elif args.hr:
                print('Device Hard Reset...')
                self.dev.reset(silent=True, reconnect=False, hr=True)
                print('Done!')
            self.flags.exit['exit'] = True
