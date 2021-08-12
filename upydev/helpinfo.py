import upydev
import json
import os
import textwrap
import webbrowser

UPYDEV_PATH = upydev.__path__[0]


HELP_INFO_ARG = '''Mode/Tools:
> DEVICE MANAGEMENT: '$ upydev dm' to see help on device management.
    ACTIONS : config, check, set, make_group, mg_group, see, gg

> FILEIO: '$ upydev fio' to see help on file input/ouput operations.
    ACTIONS: put, get, fget, dsync, rsync, backup, install, update_upyutils

> FIRMWARE: '$ upydev fw' to see help on firmware operations.
    ACTIONS: fwr, flash, mpyx

> KEYGEN: '$ upydev kg' to see help on keygen operations.
    ACTIONS: gen_rsakey, rf_wrkey, sslgen_key

> REPLS: '$ upydev rp' to see help on repls modes.
    ACTIONS: repl, rpl, wrepl, wssrepl, srepl

> SHELL-REPLS: '$ upydev sh' to see help on shell-repls modes.
    ACTIONS: shell, shl, ssl_wrepl, ssl, sh_srepl, shr, wssl, set_wss, ble, jupyterc

> DEBUGGING: '$ upydev db' to see help on debugging operations.
    ACTIONS: ping, probe, scan, run, timeit, diagnose, errlog, stream_test,
             sysctl, log, debug, pytest-setup, pytest

> GROUP COMMAND MODE: '$ upydev gp' to see help on group mode options.
    OPTIONS: -G, -GP

> HELP: '$ upydev h' or '$ upydev help' to see help (without optional args)
        '$ upydev -h' or '$ upydev --help' to see full help info.

        - To see help about a any ACTION/COMMAND
          put %% before that ACTION/COMMAND as : $ upydev %%ACTION

    ACTIONS: help, h, dm, fio, fw, kg, rp, sh, db, gp, gc, wu, sd, pro, docs,
             udocs, mdocs.

upy Commands:
> GENERAL: do '$ upydev gc' to see General commmands help.

> WIFI UTILS: do '$ upydev wu' to see Wifi utils commands help.

> SD: do '$ upydev sd' to see SD utils commands help.

> PROTOTYPE: do '$ upydev pro' to see Prototype utils commands help.
'''


def see_help(cmd):
    help_file = os.path.join(UPYDEV_PATH, 'help.config')
    with open(help_file, 'r') as helpref:
        help_dict = json.loads(helpref.read())
    columns, rows = os.get_terminal_size(0)
    if cmd is not None:
        if cmd in help_dict:
            print('\n'.join(textwrap.wrap(help_dict[cmd], columns-3)))
        else:
            print('Help info not available for "{}" command'.format(cmd))
    else:
        pass


def see_docs(args):
    if args.m == 'mdocs':
        docs_url = "docs.micropython.org"
    elif args.m == 'docs':
        docs_url = "upydev.readthedocs.io"
    elif args.m == 'udocs':
        docs_url = "upydevice.readthedocs.io"
    if args.f:
        key_word = args.f
        search = f'https://{docs_url}/en/latest/search.html?q={key_word}&check_keywords=yes&area=default'
        webbrowser.open(search)
    else:
        webbrowser.open(f'https://{docs_url}/en/latest/')
