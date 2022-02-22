
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyProcessor
from prompt_toolkit.application import get_app
from prompt_toolkit.application import run_in_terminal, in_terminal
from upydev.shell.constants import (kb_info, d_prompt,
                                    shell_commands, custom_sh_cmd_kw,
                                    CGREEN, CEND, ABLUE_bold, MAGENTA_bold,
                                    SHELL_CMD_DICT_PARSER)
from upydev.shell.common import print_table
import os
import signal
import subprocess
import shlex
import asyncio

_BB = ABLUE_bold
_CG = CGREEN
_MB = MAGENTA_bold
_CE = CEND

# KEYBINDINGS


def ShellKeyBindings(_flags, _dev, _shell, spc_cmds=[], kwdict=None):
    kb = KeyBindings()
    flags = _flags
    dev = _dev
    if kwdict:
        SHELL_CMD_DICT_PARSER.update(kwdict)
        # SHELL_CMD_DICT_PARSER

    def _printpath():
        if flags.local_path['p'] == '':
            g_p = [val[1] for val in flags.prompt['p'][1:5]]
            b_p = [val[1] for val in flags.prompt['p'][5:]]
            color_p = (f"{_CG}{''.join(g_p[:-1])}{_CE}:{_BB}"
                       f"{''.join(b_p)}{_CE}")
            print(color_p)
        else:
            m_p = [flags.prompt['p'][0][1]]
            g_p = [val[1] for val in flags.prompt['p'][1:5]]
            b_p = [val[1] for val in flags.prompt['p'][5:]]
            color_p = (f"{_MB}{''.join(m_p)}{_CE}{_CG}"
                       f"{''.join(g_p[:-1])}{_CE}:{_BB}{''.join(b_p)}"
                       f"{_CE}")
            print(color_p)

    def _printpath_cmd(last_cmd):
        if flags.local_path['p'] == '':
            g_p = [val[1] for val in
                   flags.prompt['p'][1:5]]
            b_p = [val[1]
                   for val in flags.prompt['p'][5:]]
            color_p = (f"{_CG}{''.join(g_p[:-1])}"
                       f"{_CE}:{_BB}"
                       f"{''.join(b_p)}{_CE}"
                       f"{last_cmd}")
            print(color_p)
        else:
            m_p = [flags.prompt['p'][0][1]]
            g_p = [val[1]
                   for val in flags.prompt['p'][1:5]]
            b_p = [val[1]
                   for val in flags.prompt['p'][5:]]
            color_p = (f"{_MB}{''.join(m_p)}{_CE}"
                       f"{_CG}{''.join(g_p[:-1])}"
                       f"{_CE}:{_BB}"
                       f"{''.join(b_p)}{_CE}"
                       f"{last_cmd}")
            print(color_p)

    def _autocomplete_config(buff_text):
        is_config = buff_text.split()[0] == 'config'
        param_patt = ''
        show_param_opts = False
        if is_config:
            if len(buff_text.split()) > 1:
                param_patt = buff_text.split()[-1]
                param_conf = buff_text.split()[1]
                if param_conf.endswith(':'):
                    show_param_opts = True
                    param_patt = param_conf.replace(':', '')
                    _sub_param_patt = ''
                    if buff_text.split()[-1] != buff_text.split()[1]:
                        _sub_param_patt = buff_text.split()[-1]
            if not show_param_opts:
                params_config_l = dev.wr_cmd("[conf for conf in os.listdir() "
                                             "if conf.endswith('_config.py')]",
                                             silent=True, rtn_resp=True)

                _params_config = [param.split('_')[0]
                                  for param in params_config_l]
                _params_config += ['add']
                if param_patt:
                    _params_config = [param for param in _params_config
                                      if param.startswith(param_patt)]
            if show_param_opts:
                conf = param_patt
                _param_dir = dev.wr_cmd(f"from {conf}_config"
                                        f" import {conf.upper()};"
                                        f"dir({conf.upper()})",
                                        silent=True, rtn_resp=True)
                if isinstance(_param_dir, list):
                    param_dir = [param for param in _param_dir if param != '__class__']
                    _params_config = param_dir
                else:
                    _params_config = []
                if _sub_param_patt:
                    _params_config = [param for param in _params_config
                                      if param.startswith(_sub_param_patt)]
            return _params_config
        else:
            return []

    def _autocomplete_shell_local(event):
        glb = False
        cmd_ls_glb = []
        if flags.shell_mode['S']:
            try:
                buff_text = event.app.current_buffer.document.text.split(' ')[-1]
                if isinstance(buff_text, str):
                    if '/' in buff_text:
                        root_text = '/'.join(buff_text.split('/')[:-1])
                        rest = buff_text.split('/')[-1]
                        if flags.shell_mode['S']:
                            cmd_ls_glb = os.listdir(root_text)
                    else:
                        rest = ''
                        glb = True
                        if flags.shell_mode['S']:
                            cmd_ls_glb = os.listdir()
                else:
                    pass
            except Exception:
                pass
            output = cmd_ls_glb
            try:
                if isinstance(cmd_ls_glb, str):
                    # print(espdev.output)
                    pass
                else:
                    if rest != '':
                        result = [val for val in output if val.startswith(rest)]
                        if len(result) > 1:
                            comm_part = os.path.commonprefix(result)
                            if comm_part == rest:
                                if flags.shell_mode['S']:
                                    last_cmd = event.app.current_buffer.document.text
                                    _printpath_cmd(last_cmd)
                                print_table(result, wide=28, format_SH=True)
                            else:
                                event.app.current_buffer.insert_text(
                                    comm_part[len(rest):])
                        else:
                            event.app.current_buffer.insert_text(
                                result[0][len(rest):])
                    else:
                        if not glb:
                            if flags.shell_mode['S']:
                                result = [val for val in output if val.startswith(
                                    buff_text.split('/')[-1])]
                                if len(result) > 1:
                                    comm_part = os.path.commonprefix(result)
                                    if comm_part == buff_text.split('/')[-1]:
                                        if flags.shell_mode['S']:
                                            lc = event.app.current_buffer.document.text
                                            _printpath_cmd(lc)
                                            # format ouput
                                            print_table(
                                                result, wide=28, format_SH=True)
                                    else:
                                        event.app.current_buffer.insert_text(
                                            comm_part[len(buff_text.split('/')[-1]):])
                                else:
                                    event.app.current_buffer.insert_text(
                                        result[0][len(buff_text.split('/')[-1]):])
                            else:
                                print_table(output, wide=28, format_SH=True)
                        else:
                            result = [
                                val for val in output if val.startswith(buff_text)]
                            if len(result) > 1:
                                comm_part = os.path.commonprefix(result)
                                if comm_part == buff_text:
                                    if flags.shell_mode['S']:
                                        lc = event.app.current_buffer.document.text
                                        _printpath_cmd(lc)
                                        # format ouput
                                        print_table(
                                            result, wide=28, format_SH=True)
                                    else:
                                        print('>>> {}'.format(buff_text))
                                        print_table(
                                            result, wide=28, format_SH=True)
                                else:
                                    event.app.current_buffer.insert_text(
                                        comm_part[len(buff_text):])
                            else:
                                event.app.current_buffer.insert_text(
                                    result[0][len(buff_text):])

            except Exception:
                pass

    def _autocomplete_shell(event):
        if ').' not in event.app.current_buffer.document.text:
            buff_text = event.app.current_buffer.document.text.replace(
                '=', ' ').replace('(', ' ').split(' ')[-1]
        else:
            buff_text = event.app.current_buffer.document.text.replace(
                '=', ' ').split(' ')[-1]
        rest = ''
        if '/' in buff_text:
            glb = False
            dir_to_list = '/'.join(buff_text.split('/')[:-1])
            cmd_ls_glb = f"os.listdir('{dir_to_list}')"
            if buff_text.split('/')[-1] != '':
                rest = buff_text.split('/')[-1]
                cmd_ls_glb = (f"[val for val in os.listdir('{dir_to_list}') "
                              f"if val.startswith('{rest}')]")
            else:
                if dev.dev_class == 'WebSocketDevice':

                    def pprint_result():
                        sz, wd = os.get_terminal_size(0)
                        last_cmd = event.app.current_buffer.document.text
                        _printpath_cmd(last_cmd)
                        dev.wr_cmd(f"print_table({cmd_ls_glb}, wide=28, format_SH=True,"
                                   f" gts={(sz, wd)});gc.collect()",
                                   follow=True,
                                   long_string=True)

                    run_in_terminal(pprint_result)
                    return

        else:
            rest = ''
            glb = True
            cmd_ls_glb = 'os.listdir()'
            if buff_text != '':
                cmd_ls_glb = (f"[val for val in os.listdir() if "
                              f"val.startswith('{buff_text}')]")
            else:
                if dev.dev_class == 'WebSocketDevice':
                    def pprint_result():
                        sz, wd = os.get_terminal_size(0)
                        last_cmd = event.app.current_buffer.document.text
                        _printpath_cmd(last_cmd)
                        dev.wr_cmd(f"print_table({cmd_ls_glb}, wide=28, format_SH=True,"
                                   f" gts={(sz, wd)});gc.collect()", follow=True,
                                   long_string=True)

                    run_in_terminal(pprint_result)
                    return

        output = dev.wr_cmd(cmd_ls_glb+';gc.collect()', silent=True, rtn_resp=True)
        try:
            if isinstance(output, str):
                # print(espdev.output)
                pass
            else:
                if rest != '':
                    result = [val for val in output if val.startswith(rest)]
                    if len(result) > 1:
                        comm_part = os.path.commonprefix(result)
                        if comm_part == rest:
                            def pprint_result():
                                if flags.shell_mode['S']:
                                    last_cmd = event.app.current_buffer.document.text
                                    _printpath_cmd(last_cmd)
                                print_table(result, wide=28, format_SH=True)
                            run_in_terminal(pprint_result)
                        else:
                            event.app.current_buffer.insert_text(
                                comm_part[len(rest):])
                    else:
                        event.app.current_buffer.insert_text(
                            result[0][len(rest):])
                else:
                    if not glb:
                        if flags.shell_mode['S']:
                            result = [val for val in output if val.startswith(
                                buff_text.split('/')[-1])]
                            if len(result) > 1:
                                comm_part = os.path.commonprefix(result)
                                if comm_part == buff_text.split('/')[-1]:
                                    if flags.shell_mode['S']:
                                        lc = event.app.current_buffer.document.text

                                        def pprint_result():
                                            _printpath_cmd(lc)
                                            # format ouput
                                            print_table(
                                                result, wide=28, format_SH=True)
                                        run_in_terminal(pprint_result)
                                else:
                                    event.app.current_buffer.insert_text(
                                        comm_part[len(buff_text.split('/')[-1]):])
                            else:
                                event.app.current_buffer.insert_text(
                                    result[0][len(buff_text.split('/')[-1]):])
                        else:
                            def pprint_result():
                                print_table(output, wide=28, format_SH=True)
                            run_in_terminal(pprint_result)
                    else:
                        result = [
                            val for val in output if val.startswith(buff_text)]
                        if len(result) > 1:
                            comm_part = os.path.commonprefix(result)
                            if comm_part == buff_text:
                                if flags.shell_mode['S']:
                                    lc = event.app.current_buffer.document.text

                                    def pprint_result():
                                        _printpath_cmd(lc)
                                        # format ouput
                                        print_table(
                                            result, wide=28, format_SH=True)
                                    run_in_terminal(pprint_result)

                            else:
                                event.app.current_buffer.insert_text(
                                    comm_part[len(buff_text):])
                        else:
                            event.app.current_buffer.insert_text(
                                result[0][len(buff_text):])

        except Exception:
            pass

    def _autocomplete_repl(event):
        glb = False
        import_cmd = False
        try:
            buff_text_frst_cmd = event.app.current_buffer.document.text.split(' ')[
                                                                              0]
            if buff_text_frst_cmd == 'import' or buff_text_frst_cmd == 'from':
                import_cmd = True
            if ').' not in event.app.current_buffer.document.text:
                buff_text = event.app.current_buffer.document.text.replace(
                    '=', ' ').replace('(', ' ').split(' ')[-1]
            else:
                buff_text = event.app.current_buffer.document.text.replace(
                    '=', ' ').split(' ')[-1]
            if isinstance(buff_text, str):
                if '.' in buff_text and not flags.shell_mode['S']:

                    root_text = '.'.join(buff_text.split('.')[:-1])
                    rest = buff_text.split('.')[-1]
                    if rest != '':
                        output = dev.wr_cmd(f"[val for val in dir({root_text}) if "
                                            f"val.startswith('{rest}')]", silent=True,
                                            rtn_resp=True)

                    else:
                        try:
                            output = dev.wr_cmd(f'dir({root_text});gc.collect()',
                                                silent=True, rtn_resp=True)
                        except KeyboardInterrupt:
                            pass

                else:
                    rest = ''
                    glb = True
                    cmd_ls_glb = 'dir()'
                    if buff_text != '':
                        cmd_ls_glb = (f"[val for val in dir() if "
                                      f"val.startswith('{buff_text}')]")
                    if import_cmd:
                        fbuff_text = event.app.current_buffer.document.text.split()
                        _imp = 'import' in fbuff_text
                        _from = 'from' in fbuff_text
                        if _imp and _from and len(fbuff_text) >= 3:
                            if fbuff_text[1] not in flags.frozen_modules['FM']:
                                if len(fbuff_text) == 3:
                                    _fbt1 = fbuff_text[1]
                                    cmd_ls_glb = (f"import {_fbt1};dir({_fbt1});"
                                                  f"del(sys.modules['{_fbt1}'])")
                                if len(fbuff_text) == 4:
                                    _fbt1 = fbuff_text[1]
                                    _fbt3 = fbuff_text[3]
                                    cmd_ls_glb = (f"import {_fbt1};[val for val in "
                                                  f"dir({_fbt1}) if "
                                                  f"val.startswith('{_fbt3}')];"
                                                  f"del(sys.modules['{_fbt1}'])")
                            else:
                                if len(fbuff_text) == 3:
                                    _fbt1 = fbuff_text[1]
                                    cmd_ls_glb = f"import {_fbt1};dir({_fbt1})"
                                if len(fbuff_text) == 4:
                                    _fbt1 = fbuff_text[1]
                                    _fbt3 = fbuff_text[3]
                                    cmd_ls_glb = (f"import {_fbt1};[val for val in "
                                                  f"dir({_fbt1}) if "
                                                  f"val.startswith('{_fbt3}')];")
                        else:
                            cmd_ls_glb = ("[scp.split('.')[0] for scp "
                                          "in os.listdir()+os.listdir('./lib')"
                                          " if '.py' in scp]")
                            if dev.dev_platform == 'pyboard':
                                cmd_ls_glb = ("[scp.split('.')[0] for scp in "
                                              "os.listdir()+os.listdir('/flash/lib') "
                                              "if '.py' in scp]")
                            flags.frozen_modules['SUB'] = flags.frozen_modules['FM']
                            if buff_text != '':
                                cmd_ls_glb = ("[scp.split('.')[0] for scp in "
                                              "os.listdir()+os.listdir('./lib') "
                                              "if '.py' in scp and "
                                              f"scp.startswith('{buff_text}')]")
                                if dev.dev_platform == 'pyboard':
                                    cmd_ls_glb = ("[scp.split('.')[0] for scp in "
                                                  "os.listdir()+os.listdir('/flash/lib'"
                                                  ") if '.py' in scp and "
                                                  f"scp.startswith('{buff_text}')]")
                                flags.frozen_modules['SUB'] = [mod for mod in
                                                               flags.frozen_modules['FM']
                                                               if mod.startswith(buff_text)]
                    try:
                        output = dev.wr_cmd(cmd_ls_glb+';gc.collect()',
                                            silent=True, rtn_resp=True)
                    except KeyboardInterrupt:
                        pass
            else:
                root_text = buff_text.split('.')[0]
                rest = buff_text.split('.')[1]
                try:
                    output = dev.wr_cmd(f'dir({root_text});gc.collect()',
                                        silent=True, rtn_resp=True)
                except KeyboardInterrupt:
                    pass
        except Exception:
            pass
        try:
            if glb:
                kw_line_buff = event.app.current_buffer.document.text.split()
                if len(kw_line_buff) > 0 and len(kw_line_buff) <= 2:
                    if 'import' == kw_line_buff[0] or 'from' == kw_line_buff[0]:
                        output = output + flags.frozen_modules['SUB']
            if isinstance(output, str):
                pass
            else:
                if rest != '':
                    result = [val for val in output if val.startswith(rest)]
                    if len(result) > 1:
                        comm_part = os.path.commonprefix(result)
                        if comm_part == rest:
                            # print('>>> {}'.format(buff_text))
                            def pprint_result():
                                print('>>> {}'.format(buff_text))
                                print_table(
                                    result, autowide=True, sort=False)
                            run_in_terminal(pprint_result)

                        else:
                            event.app.current_buffer.insert_text(
                                comm_part[len(rest):])
                    else:
                        event.app.current_buffer.insert_text(
                            result[0][len(rest):])
                else:
                    if not glb:
                        # print('>>> {}'.format(buff_text))   # dir var
                        def pprint_result():
                            print('>>> {}'.format(buff_text))   # dir var
                            print_table(output, wide=16, autocol_tab=True, sort=False)
                        run_in_terminal(pprint_result)

                    else:
                        result = [
                            val for val in output if val.startswith(buff_text)]
                        if len(result) > 1:
                            comm_part = os.path.commonprefix(result)
                            if comm_part == buff_text:

                                # print('>>> {}'.format(buff_text))  # globals
                                def pprint_result():
                                    print('>>> {}'.format(buff_text))  # globals
                                    print_table(result, wide=16,
                                                autowide=True)
                                run_in_terminal(pprint_result)

                            else:
                                event.app.current_buffer.insert_text(
                                    comm_part[len(buff_text):])
                        else:
                            event.app.current_buffer.insert_text(
                                result[0][len(buff_text):])

        except Exception:
            pass

    @kb.add('c-x')
    def exitpress(event):
        " Exit SHELL-REPL terminal "
        if flags.shell_mode['S']:
            print('\nclosing...')
        else:
            print('\n>>> closing...')
        if flags.reset['R']:
            # TODO: include hard reset
            dev.reset(reconnect=False)
            dev.disconnect()
        else:
            pass

        flags.exit['exit'] = True
        event.app.exit()

    @kb.add('c-b')
    def bannerpress(event):
        "Prints MicroPython sys version info"
        def upy_sysversion():
            dev.banner()

        run_in_terminal(upy_sysversion)

    @kb.add('c-k')
    def see_cmd_info_press(event):
        "CTRL-Commands info"
        def cmd_info():
            print(kb_info)
        run_in_terminal(cmd_info)

    @kb.add('c-r')
    def flush_line(event):
        event.app.current_buffer.reset()

    @kb.add('c-o')  # upy-config
    def upy_config_dialog(event):
        event.app.current_buffer.reset()
        event.app.current_buffer.insert_text('upy-config', move_cursor=True)

    @kb.add('c-n')
    def cmd_mem_info(event):

        def mem_info_out():
            print('>>> mem_info()')
            dev.wr_cmd('from micropython import mem_info; mem_info()', follow=True)

        run_in_terminal(mem_info_out)

    @kb.add('c-y')
    def cmd_gc_collect(event):

        def gc_collect_out():
            print('>>> gc.collect()')
            dev.wr_cmd('import gc;gc.collect()', follow=True)

        run_in_terminal(gc_collect_out)

    @kb.add('c-f')
    def toggle_autosgst(event):
        if flags.autosuggest['A']:
            flags.autosuggest['A'] = False
        else:
            flags.autosuggest['A'] = True

    @kb.add('c-space')
    def autocomppress(event):
        "Send last command"

        def print_last():
            last_cmd = event.app.current_buffer.history.get_strings()[-1]
            if flags.shell_mode['S']:
                _printpath_cmd(last_cmd)
                _shell.cmd(last_cmd)
            else:
                print('>>> {}'.format(last_cmd))
                try:
                    dev.wr_cmd(last_cmd, follow=True)
                    # if espdev.output is not None:
                    #     print(espdev.output)
                except KeyboardInterrupt:
                    pass

        run_in_terminal(print_last)
#
#

    @kb.add('c-t')
    def runtempbuff(event):
        "Run contents of _tmp_script.py"

        app = get_app()
        p = app.key_processor
        inp = app.input

        def i_pipe(data, kp=p, ap=app, input=inp, **kargs):
            print(data, end='')
            kp.feed_multiple(input.read_keys())
            kp.process_keys()

        async def run_tmpcode():
            if '_tmp_script.py' in os.listdir():
                print('Running Buffer...')
                with open('_tmp_script.py', 'r') as fbuff:
                    filebuffer = fbuff.read()
                event.app.current_buffer.reset()
                dev.paste_buff(filebuffer)
                dev.flush_conn()
                event.app.current_buffer.reset()
                flags.script_is_running['R'] = True
                try:
                    dev.wr_cmd('\x04', follow=True, long_string=True, pipe=i_pipe)
                except KeyboardInterrupt:
                    dev.kbi()

        async def runtmp():
            await run_tmpcode()

        asyncio.create_task(runtmp())

    @kb.add('c-w')
    def whoami(event):
        "Show device info"
        def dev_who():
            print(dev)
        run_in_terminal(dev_who)

    @kb.add('c-a')
    def reset_cursor(event):
        "Move cursor to init position"
        buff_text = event.app.current_buffer.document.text
        event.app.current_buffer.reset()
        event.app.current_buffer.insert_text(buff_text, move_cursor=False)

    @kb.add('c-j')
    def eof_cursor(event):
        "Move cursor to final position"
        buff_text = event.app.current_buffer.document.text
        event.app.current_buffer.reset()
        event.app.current_buffer.insert_text(buff_text, move_cursor=True)
#
#

    @kb.add('c-s')
    def toggle_shell_mode(event):
        def show_p():
            if flags.shell_mode['S']:
                _printpath()
            else:
                print(flags.prompt['p'])

            if flags.shell_mode['S']:
                flags.prompt['p'] = d_prompt
                flags.shell_mode['S'] = False
            else:
                flags.prompt['p'] = flags.shell_prompt['s']
                flags.shell_mode['S'] = True
                dev.wr_cmd('import gc;from upysh import *', silent=True)
                dev.output = None

        run_in_terminal(show_p)
    #
#

    @kb.add('c-c')
    def send_KBI(event):
        # def send_KBI():
        try:
            last_cmd = ''
            if flags.shell_mode['S']:
                print('^C')
                event.app.current_buffer.reset()
                flags.paste['p'] = False
                if flags.script_is_running['R']:
                    dev.kbi(silent=False, long_string=True)
                    flags.script_is_running['R'] = False
            else:
                print('^C')
                dev.kbi(silent=False, long_string=True)  # KBI

                flags.paste['p'] = False
                if not flags.shell_mode['S']:
                    flags.prompt['p'] = d_prompt
                    last_cmd = event.app.current_buffer.document.text
                event.app.current_buffer.reset()
        except Exception:
            pass

        def cmd_kbi(command=last_cmd):
            if flags.prompt['p'] == ">>> ":
                print(flags.prompt['p'] + command)
        run_in_terminal(cmd_kbi)
#
#

    @kb.add('c-e')
    def paste_mode(event):
        "ENTER PASTE VIM MODE"
        if not flags.shell_mode['S']:
            flags.paste['p'] = True
            event.app.current_buffer.reset()
            # event.app.current_buffer.insert_text('import')

            def cmd_paste_vim():
                shell_cmd_str = shlex.split("vim _tmp_script.py")

                old_action = signal.signal(signal.SIGINT, signal.SIG_IGN)

                def preexec_function(action=old_action):
                    signal.signal(signal.SIGINT, action)
                try:
                    subprocess.call(shell_cmd_str, preexec_fn=preexec_function)
                    signal.signal(signal.SIGINT, old_action)
                except Exception as e:
                    print(e)
                # SEND Buffer
                if '_tmp_script.py' in os.listdir():
                    with open('_tmp_script.py', 'r') as fbuff:
                        filebuffer = fbuff.read()
                    dev.paste_buff(filebuffer)
                    print('Temp Buffer loaded do CTRL-D to execute or CTRL-C to cancel')
                # dev.wr_cmd('\x04', follow=True)
                else:
                    flags.paste['p'] = False

            run_in_terminal(cmd_paste_vim)
        else:
            pass
#
#

    @kb.add('c-d')
    def paste_mode_exit(event):
        "PASTE MODE VIM EXEC, SOFT RESET IN REPL"
        if flags.paste['p']:
            app = get_app()
            p = app.key_processor
            inp = app.input

            def i_pipe(data, kp=p, ap=app, input=inp, **kargs):
                print(data, end='')
                kp.feed_multiple(input.read_keys())
                kp.process_keys()

            async def cmd_paste_exit():
                print('Running Buffer...')
                event.app.current_buffer.reset()
                dev.wr_cmd('\x04', follow=True, long_string=True, pipe=i_pipe)
                flags.paste['p'] = False

            async def pastmp():
                await cmd_paste_exit()

            asyncio.create_task(pastmp())
        else:
            if not flags.shell_mode['S']:
                dev.reset()
                dev.wr_cmd('import gc;import os;from upysh import *;'
                           'from nanoglob import glob'
                           ';gc.collect()', silent=True)

#
#

    @kb.add('tab')
    def tab_press(event):
        "Tab autocompletion info"
        def do_complete(event=event):
            if flags.shell_mode['S']:
                _autocomplete_shell(event)
            else:
                _autocomplete_repl(event)
        do_complete()
        # do_complete()
#
#

    @kb.add('s-tab')
    def shif_tab(event):
        "Autocomplete shell commands"
        def autocomplete_sh_cmd():
            if flags.shell_mode['S']:
                buff_text = event.app.current_buffer.document.text
                if ' && ' in buff_text:
                    buff_text = buff_text.split(' && ')[-1]
                result = [sh_cmd for sh_cmd in shell_commands
                          + custom_sh_cmd_kw + spc_cmds if sh_cmd.startswith(buff_text)]
                # parse and autocomplete config
                is_config = False
                if len(buff_text.split()) > 0:
                    if "config" == buff_text.split()[0]:
                        is_config = True
                        result = _autocomplete_config(buff_text)
                        _buff_text = str(buff_text)
                        buff_text = ''
                if any([cmd in buff_text.split()
                        for cmd in SHELL_CMD_DICT_PARSER.keys()]):
                    # print('Here: {}'.format(buff_text.split()))
                    if len(buff_text.split()) > 1:
                        result = []
                        cmd = buff_text.split()[0]
                        if cmd not in SHELL_CMD_DICT_PARSER.keys():
                            result = [sh_cmd for sh_cmd in shell_commands
                                      + custom_sh_cmd_kw + spc_cmds
                                      if sh_cmd.startswith(cmd)]
                        else:
                            if SHELL_CMD_DICT_PARSER[cmd]['subcmd']:
                                ch = SHELL_CMD_DICT_PARSER[cmd]['subcmd'].get('choices')
                                if 'alt_ops' in SHELL_CMD_DICT_PARSER[cmd].keys():
                                    ch = SHELL_CMD_DICT_PARSER[cmd]['alt_ops']
                                if ch:
                                    last_cmd_line = buff_text.split()[-1]
                                    result += [sh_cmd
                                               for sh_cmd in
                                               ch
                                               if sh_cmd.startswith(last_cmd_line)]
                                else:
                                    result = []
                            if SHELL_CMD_DICT_PARSER[cmd]['options']:
                                ch = SHELL_CMD_DICT_PARSER[cmd]['options'].keys()
                                if ch:
                                    last_cmd_line = buff_text.split()[-1]
                                    result += [sh_cmd
                                               for sh_cmd in
                                               ch
                                               if sh_cmd.startswith(last_cmd_line)
                                               and sh_cmd not in buff_text.split()]
                                else:
                                    result = []

                        # print(result)
                        buff_text = buff_text.split()[-1]
                    else:
                        cmd = buff_text.split()[0]
                        ch = []
                        if SHELL_CMD_DICT_PARSER[cmd]['subcmd']:
                            ch = SHELL_CMD_DICT_PARSER[cmd]['subcmd'].get('choices')
                            if 'alt_ops' in SHELL_CMD_DICT_PARSER[cmd].keys():
                                ch = SHELL_CMD_DICT_PARSER[cmd]['alt_ops']
                        if SHELL_CMD_DICT_PARSER[cmd]['options']:
                            if not ch:
                                ch = []
                            ch += SHELL_CMD_DICT_PARSER[cmd]['options'].keys()
                        if ch:
                            result = ch
                        else:
                            result = []
                        buff_text = ''
                if len(result) > 1:
                    if is_config:
                        buff_text = _buff_text.split()[-1]
                        if buff_text == 'config':
                            buff_text = ''
                        if len(_buff_text.split()) > 1:
                            if _buff_text.split()[1].endswith(':'):
                                buff_text = _buff_text.split()[-1]
                                if buff_text.endswith(':'):
                                    buff_text = ''
                    comm_part = os.path.commonprefix(result)
                    if comm_part == buff_text:
                        def pprint_result():
                            last_cmd = event.app.current_buffer.document.text
                            _printpath_cmd(last_cmd)

                            print_table(result)
                        run_in_terminal(pprint_result)
                    else:
                        event.app.current_buffer.insert_text(
                            comm_part[len(buff_text):])
                else:
                    if is_config:
                        buff_text = _buff_text.split()[-1]
                        if buff_text == 'config':
                            buff_text = ''
                            if not event.app.current_buffer.document.text.endswith(' '):
                                event.app.current_buffer.insert_text(' ')
                    if len(result) > 0:
                        event.app.current_buffer.insert_text(
                            result[0][len(buff_text):])

        autocomplete_sh_cmd()
#
#

    @kb.add('s-right')
    def autocomplete_locals(event):
        def do_complete(event=event):
            _autocomplete_shell_local(event)

        run_in_terminal(do_complete)
#
#

    @kb.add('s-left')
    def toggle_local_path(event):
        if flags.shell_mode['S']:
            if flags.show_local_path['s']:
                flags.show_local_path['s'] = False
                flags.local_path['p'] = ''

                # SET ROOT USER PATH:
                flags.shell_prompt['s'][0] = ('class:userpath', flags.local_path['p'])
                flags.prompt['p'] = flags.shell_prompt['s']
            else:
                flags.show_local_path['s'] = True
                flags.local_path['p'] = os.getcwd().split('/')[-1]+':/'
                if os.getcwd() == os.environ['HOME']:
                    flags.local_path['p'] = '~:/'

                # SET ROOT USER PATH:
                flags.shell_prompt['s'][0] = ('class:userpath', flags.local_path['p'])
                flags.prompt['p'] = flags.shell_prompt['s']
#
# # @kb.add('c-u')
# # def unsecure_mode(event):
# #     "Toggle send unencrypted commands"
# #     if not args.nem:
# #         status_encryp_msg['S'] = True
# #         status_encryp_msg['Toggle'] = False
# #         if encrypted_flag['sec']:
# #             encrypted_flag['sec'] = False
# #             espdev.output = None
# #             shr_cp.sw_repl()
# #
# #             def warning_us():
# #                 print(CRED + 'WARNING: ENCRYPTION DISABLED' + CEND)
# #             # run_in_terminal(warning_us)
# #         else:
# #             encrypted_flag['sec'] = True
# #             espdev.output = None
# #             shr_cp.sw_repl()
# #             espdev.output = None
# #
# #             def warning_sec():
# #                 print(CGREEN + 'INFO: ENCRYPTION ENABLED' + CEND)
# #         # run_in_terminal(warning_sec)
#
#

    @kb.add('c-p')
    def toggle_status_ram_msg(event):
        "Toggle Right RAM status"
        if not flags.mem_show_rp['show']:
            flags.mem_show_rp['show'] = True
            flags.mem_show_rp['call'] = True
        else:
            flags.mem_show_rp['show'] = False
#
#
# @kb.add('c-g')
# def listen_SHELL_REPL(event):
#     "Echo SHELL_REPL --> Active listening for timer/hardware interrupts"
#     def echo_ouput():
#         try:
#             buff_text = "import time\nwhile True:\n    time.sleep(1)"
#             shr_cp.paste_buff(buff_text)
#             shr_cp.sh_repl("\x04", follow=True)
#         except KeyboardInterrupt:
#             time.sleep(0.2)
#             shr_cp.sh_repl('\x03', silent=True,
#                            traceback=True)  # KBI
#             time.sleep(0.2)
#             for i in range(1):
#                 shr_cp.sh_repl('\x0d', silent=True)
#                 shr_cp.flush_conn()
#             pass
#         espdev.output = None
#         time.sleep(1)
#         shr_cp.flush_conn()
#         shr_cp.flush_conn()
#         event.app.current_buffer.reset()
#     run_in_terminal(echo_ouput)
#     run_in_terminal(echo_ouput)
    return kb
