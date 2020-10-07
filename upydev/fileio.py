

FILEIO_HELP = """
> FILEIO: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - put : to upload a file to upy device (see -f, -s, -fre, -dir, -rst)

        - get : to download a file from upy device (see -f, -s, -fre, -dir)

        - sync : for a faster transfer of large files
            (this needs sync_tool.py in upy device) (see -f, -s and -lh)

        - d_sync: to recursively sync a folder in upydevice filesystem use -dir
                    to indicate the folder (must be in cwd), use -tree to see dir
                    structure, to sync to an Sd card mounted as 'sd' use -s sd

        - install : install libs to '/lib' path with upip; indicate lib with -f option

        - update_upyutils: to update the latest versions of sync_tool.py, upylog.py,
                        upynotify.py, upysecrets.py, upysh2.py, ssl_repl.py, uping.py, time_it.py,
                        wss_repl.py and wss_helper.py.

"""
