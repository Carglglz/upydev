import upydev
import json
import os
import textwrap
import webbrowser

UPYDEV_PATH = upydev.__path__[0]


HELP_INFO_ARG = '''Mode/Tools:
> DEVICE MANAGEMENT: '$ upydev dm' to see help on device management.
    ACTIONS : config, check, set, register, lsdevs, mkg, mgg, gg, mksg, see

> FILEIO: '$ upydev fio' to see help on file input/ouput operations.
    ACTIONS: put, get, dsync, install, update_upyutils

> FIRMWARE: '$ upydev fw' to see help on firmware operations.
    ACTIONS: fwr, flash, ota, mpyx

> KEYGEN: '$ upydev kg' to see help on keygen operations.
    ACTIONS: kg rsa, kg ssl, rsa sign, rsa verify, rsa auth

> REPLS: '$ upydev rp' to see help on repls modes.
    ACTIONS: repl, rpl

> SHELL-REPLS: '$ upydev sh' to see help on shell-repls modes.
    ACTIONS: shell, shl, set_wss, jupyterc

> DEBUGGING: '$ upydev db' to see help on debugging operations.
    ACTIONS: ping, probe, scan, run, timeit, stream_test,
             sysctl, log, pytest, pytest setup

> GENERAL: do '$ upydev gc' to see General commmands help.

> GROUP COMMAND MODE: '$ upydev gp' to see help on group mode options.
    OPTIONS: -G, -GP

> HELP: '$ upydev h' or '$ upydev help' to see help (without optional args)
        '$ upydev -h' or '$ upydev --help' to see full help info.

        - To see help about a any ACTION/COMMAND
          $ upydev COMMAND -h

    ACTIONS: help, h, dm, fio, fw, kg, rp, sh, db, gp, gc, docs,
             udocs, mdocs.
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


def see_docs(args, unkwargs):
    if args.m == 'mdocs':
        docs_url = "docs.micropython.org"
    elif args.m == 'docs':
        docs_url = "upydev.readthedocs.io"
    elif args.m == 'udocs':
        docs_url = "upydevice.readthedocs.io"
    if unkwargs:
        key_word = unkwargs[0]
        search = f'https://{docs_url}/en/latest/search.html?q={key_word}&check_keywords=yes&area=default'
        webbrowser.open(search)
    else:
        webbrowser.open(f'https://{docs_url}/en/latest/')
