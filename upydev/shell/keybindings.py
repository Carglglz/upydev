from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal
from upydev.shell.constants import (kb_info, shell_commands_info, d_prompt,
                                    shell_commands, custom_sh_cmd_kw,
                                    CGREEN, CEND, ABLUE_bold, MAGENTA_bold)
from upydev.shell.common import print_table
import os
import signal
import subprocess
import shlex

_BB = ABLUE_bold
_CG = CGREEN
_MB = MAGENTA_bold
_CE = CEND

# KEYBINDINGS


def ShellKeyBindings(_flags, _dev, _shell):
    kb = KeyBindings()
    flags = _flags
    dev = _dev

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

    def _autocomplete_shell():
        pass

    def _autocomplete_repl():
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
            if flags.shell_mode['S']:
                print(shell_commands_info)
        run_in_terminal(cmd_info)

    @kb.add('c-r')
    def flush_line(event):
        event.app.current_buffer.reset()

    @kb.add('c-o')
    def cmd_ls(event):
        def ls_out():
            print('>>> ls')
            dev.wr_cmd('ls();gc.collect()', follow=True)

        run_in_terminal(ls_out)

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
        def run_tmpcode():
            print('Running Buffer')
            with open('_tmp_script.py', 'r') as fbuff:
                filebuffer = fbuff.read()
            event.app.current_buffer.reset()
            dev.paste_buff(filebuffer)
            event.app.current_buffer.reset()
            dev.wr_cmd('\x04', follow=True)
        run_in_terminal(run_tmpcode)
#
#
# @kb.add('c-w')
# def reloadpress(event):
#     "Reload test_code command"
#     def reload_code():
#         espdev.output = None
#         reload_cmd = "import sys;del(sys.modules['test_code']);gc.collect()"
#         print('>>> {}'.format(reload_cmd))
#
#         shr_cp.sh_repl(reload_cmd)
#         if espdev.output is not None:
#             print(espdev.output)
#     if not edit_mode['E']:
#         run_in_terminal(reload_code)
#     else:
#         edit_mode['E'] = False
#
#

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
            else:

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
                with open('_tmp_script.py', 'r') as fbuff:
                    filebuffer = fbuff.read()
                dev.paste_buff(filebuffer)
                print('Temp Buffer loaded do CTRL-D to execute or CTRL-C to cancel')
                # dev.wr_cmd('\x04', follow=True)

            run_in_terminal(cmd_paste_vim)
        else:
            pass
            # if edit_mode['E']:
            #     def cmd_paste():
            #         print('Edit Mode; Ctrl-C to cancel, Ctrl-D to finish, then ESC, ENTER')
            #         print("#<---- File: {} --->".format(edit_mode['File']))
            #         prompt['p'] = ""
            #     run_in_terminal(cmd_paste)
            #     event.app.current_buffer.reset()
            #     espdev.long_output = []
            #     espdev.output = None
            #     espdev.response = ''
            #     shr_cp.sh_repl("cat('{}')".format(edit_mode['File']))
            #     file_content = espdev.output
            #     try:
            #         process_content = file_content
            #     except Exception as e:
            #         process_content = ' '
            #     if isinstance(file_content, str):
            #         event.app.current_buffer.insert_text(process_content)
            # else:
            #     # "Move cursor to final position"
            #     buff_text = event.app.current_buffer.document.text
            #     event.app.current_buffer.reset()
            #     event.app.current_buffer.insert_text(buff_text, move_cursor=True)
#
#

    @kb.add('c-d')
    def paste_mode_exit(event):
        "PASTE MODE VIM EXEC, SOFT RESET IN REPL"
        # event.app.current_buffer.insert_text('import')

        def cmd_paste_exit():
            print('Running Buffer...')
            event.app.current_buffer.reset()
            dev.wr_cmd('\x04', follow=True)
            flags.paste['p'] = False

        if flags.paste['p']:
            run_in_terminal(cmd_paste_exit)
#
#     def cmd_edit_exit(file_to_edit=edit_mode['File']):
#            buff_text = ''.join([event.app.current_buffer.document.text])
#             if buff_text is not None and buff_text != '':
#                 send_custom_sh_cmd(
#                     "_file_to_edit = open('{}','w')".format(file_to_edit))
#                 send_custom_sh_cmd("nl = '\\n'")
#                 print('Writing to file...')
#                 lines_to_write = buff_text.split('\n')
#                 for line in lines_to_write:
#                     if line != ' ' and line != "" and line != '':
#                         send_custom_sh_cmd(
#                             '_file_to_edit.write("{}")'.format(line))
#
#                         send_custom_sh_cmd('_file_to_edit.write(nl)')
#
#                 send_custom_sh_cmd("_file_to_edit.close()")
#                 send_custom_sh_cmd("gc.collect()")
#                 time.sleep(0.5)
#                 shr_cp.flush_conn()
#                 shr_cp.flush_conn()
#             event.app.current_buffer.reset()
#
#             print("File {} edited successfully!".format(file_to_edit))
#             print('PRESS ESC, THEN ENTER TO EXIT EDIT MODE')
#     if not shell_mode['S']:
#         if paste_flag['p']:
#             # print(paste_buffer['B'])
#             run_in_terminal(cmd_paste_exit)
#             paste_buffer['B'] = ['']
#         else:
#             shr_cp.sh_repl('\x04', follow=True)
#             time.sleep(0.2)
#             shr_cp.dev.serial.close()
#             time.sleep(1)
#             shr_cp.dev.serial.open()
#             shr_cp.sh_repl('import os;import gc;from upysh import *', silent=True)
#             shr_cp.flush_conn()
#         paste_flag['p'] = False
#     else:
#         if edit_mode['E']:
#             run_in_terminal(cmd_edit_exit)
#             prompt['p'] = shell_prompt['s']
#         edit_mode['E'] = False
#     # paste_buffer['B'] = ['']  # RESET PASTE BUFFER
#
#
# @kb.add('tab')
# def tab_press(event):
#     "Tab autocompletion info"
#     # event.app.current_buffer.insert_text('import')
#     if paste_flag['p'] or edit_mode['E']:
#         event.app.current_buffer.insert_text('    ')
#     else:
#         glb = False
#         import_cmd = False
#         try:
#             buff_text_frst_cmd = event.app.current_buffer.document.text.split(' ')[
#                                                                               0]
#             if buff_text_frst_cmd == 'import' or buff_text_frst_cmd == 'from':
#                 import_cmd = True
#             if ').' not in event.app.current_buffer.document.text:
#                 buff_text = event.app.current_buffer.document.text.replace(
#                     '=', ' ').replace('(', ' ').split(' ')[-1]
#             else:
#                 buff_text = event.app.current_buffer.document.text.replace(
#                     '=', ' ').split(' ')[-1]
#             if isinstance(buff_text, str):
#                 if '.' in buff_text and not shell_mode['S']:
#
#                     root_text = '.'.join(buff_text.split('.')[:-1])
#                     rest = buff_text.split('.')[-1]
#                     if rest != '':
#                         shr_cp.sh_repl(
#                             "[val for val in dir({}) if val.startswith('{}')]".format(root_text, rest))
#                         shr_cp.flush_conn()
#
#                     else:
#                         try:
#                             shr_cp.sh_repl('dir({});gc.collect()'.format(root_text),
#                                            debug=False, prevent_hang=True)
#                         except KeyboardInterrupt:
#                             time.sleep(0.2)
#                             shr_cp.sh_repl('\x03', silent=True,
#                                            traceback=True)
#
#                         shr_cp.flush_conn()
#
#                 else:
#                     rest = ''
#                     glb = True
#                     cmd_ls_glb = 'dir()'
#                     if buff_text != '':
#                         cmd_ls_glb = "[val for val in dir() if val.startswith('{}')]".format(
#                             buff_text)
#                     if import_cmd:
#                         fbuff_text = event.app.current_buffer.document.text.split()
#                         if 'import' in fbuff_text and 'from' in fbuff_text and len(fbuff_text) >= 3:
#                             if fbuff_text[1] not in frozen_modules['FM']:
#                                 if len(fbuff_text) == 3:
#                                     cmd_ls_glb = "import {0};dir({0});del(sys.modules['{0}'])".format(
#                                         fbuff_text[1])
#                                 if len(fbuff_text) == 4:
#                                     cmd_ls_glb = "import {0};[val for val in dir({0}) if val.startswith('{1}')];del(sys.modules['{0}'])".format(
#                                         fbuff_text[1], fbuff_text[3])
#                             else:
#                                 if len(fbuff_text) == 3:
#                                     cmd_ls_glb = "import {0};dir({0})".format(
#                                         fbuff_text[1])
#                                 if len(fbuff_text) == 4:
#                                     cmd_ls_glb = "import {0};[val for val in dir({0}) if val.startswith('{1}')]".format(
#                                         fbuff_text[1], fbuff_text[3])
#                         else:
#                             cmd_ls_glb = "[scp.split('.')[0] for scp in os.listdir()+os.listdir('./lib') if '.py' in scp]"
#                             if dev_platform == 'pyboard':
#                                 cmd_ls_glb = "[scp.split('.')[0] for scp in os.listdir()+os.listdir('/flash/lib') if '.py' in scp]"
#                             frozen_modules['SUB'] = frozen_modules['FM']
#                             if buff_text != '':
#                                 cmd_ls_glb = "[scp.split('.')[0] for scp in os.listdir()+os.listdir('./lib') if '.py' in scp and scp.startswith('{}')]".format(
#                                     buff_text)
#                                 if dev_platform == 'pyboard':
#                                     cmd_ls_glb = "[scp.split('.')[0] for scp in os.listdir()+os.listdir('/flash/lib') if '.py' in scp and scp.startswith('{}')]".format(
#                                         buff_text)
#
#                                 frozen_modules['SUB'] = [
#                                     mod for mod in frozen_modules['FM'] if mod.startswith(buff_text)]
#
#                     if shell_mode['S']:
#
#                         if '/' in buff_text:
#                             glb = False
#                             dir_to_list = '/'.join(buff_text.split('/')[:-1])
#                             cmd_ls_glb = "os.listdir('{}')".format(dir_to_list)
#                             if buff_text.split('/')[-1] != '':
#                                 cmd_ls_glb = "[val for val in os.listdir('{}') if val.startswith('{}')]".format(
#                                     dir_to_list, buff_text.split('/')[-1])
#
#                         else:
#                             cmd_ls_glb = 'os.listdir()'
#                             if buff_text != '':
#                                 cmd_ls_glb = "[val for val in os.listdir() if val.startswith('{}')]".format(
#                                     buff_text)
#
#                     try:
#                         shr_cp.sh_repl(cmd_ls_glb+';gc.collect()',
#                                        debug=False, prevent_hang=True)
#                     except KeyboardInterrupt:
#                         time.sleep(0.2)
#                         shr_cp.sh_repl('\x03', silent=True,
#                                        traceback=True)
#                     shr_cp.flush_conn()
#
#             else:
#                 root_text = buff_text.split('.')[0]
#                 rest = buff_text.split('.')[1]
#                 try:
#                     shr_cp.sh_repl('dir({});gc.collect()'.format(root_text))
#                 except KeyboardInterrupt:
#                     time.sleep(0.2)
#                     shr_cp.sh_repl('\x03', silent=True, traceback=True)
#                 shr_cp.flush_conn()
#         except Exception as e:
#             pass
#
#         def tab_cmd_info(rest_part=rest, flag=glb, buff=buff_text):
#             try:
#                 if espdev.output is not None:
#                     espdev.get_output()
#                     if glb:
#                         kw_line_buff = event.app.current_buffer.document.text.split()
#                         if len(kw_line_buff) > 0 and len(kw_line_buff) <= 2:
#                             if 'import' == kw_line_buff[0] or 'from' == kw_line_buff[0]:
#                                 espdev.output = espdev.output + frozen_modules['SUB']
#                     if isinstance(espdev.output, str):
#                         # print(espdev.output)
#                         pass
#                     else:
#                         if rest != '':  # print attributes
#                             result = [
#                                 val for val in espdev.output if val.startswith(rest)]
#                             if len(result) > 1:
#                                 comm_part = os.path.commonprefix(result)
#                                 if comm_part == rest:
#                                     print('>>> {}'.format(buff_text))
#                                     print_table(result, autowide=True, sort=False)
#                                 else:
#                                     event.app.current_buffer.insert_text(
#                                         comm_part[len(rest):])
#                             else:
#                                 event.app.current_buffer.insert_text(
#                                     result[0][len(rest):])
#                         else:
#                             if not glb:
#                                 if shell_mode['S']:  # print dirs/files
#                                     result = [val for val in espdev.output if val.startswith(
#                                         buff_text.split('/')[-1])]
#                                     if len(result) > 1:
#                                         comm_part = os.path.commonprefix(result)
#                                         if comm_part == buff_text.split('/')[-1]:
#                                             if shell_mode['S']:
#                                                 last_cmd = event.app.current_buffer.document.text
#                                                 if local_path['p'] == '':
#                                                     g_p = [val[1]
#                                                            for val in prompt['p'][1:5]]
#                                                     b_p = [val[1]
#                                                            for val in prompt['p'][5:]]
#                                                     color_p = "\33[32;1m{}\033[0m:\u001b[34;1m{}\033[0m{}".format(
#                                                         "".join(g_p[:-1]), "".join(b_p), last_cmd)
#                                                     print(color_p)
#                                                 else:
#                                                     m_p = [prompt['p'][0][1]]
#                                                     g_p = [val[1]
#                                                            for val in prompt['p'][1:5]]
#                                                     b_p = [val[1]
#                                                            for val in prompt['p'][5:]]
#                                                     color_p = "\u001b[35;1m{}\033[0m\33[32;1m{}\033[0m:\u001b[34;1m{}\033[0m{}".format(
#                                                         "".join(m_p), "".join(g_p[:-1]), "".join(b_p), last_cmd)
#                                                     print(color_p)
#                                                 # format ouput
#                                                 print_table(
#                                                     result, wide=28, format_SH=True)
#                                         else:
#                                             event.app.current_buffer.insert_text(
#                                                 comm_part[len(buff_text.split('/')[-1]):])
#                                     else:
#                                         event.app.current_buffer.insert_text(
#                                             result[0][len(buff_text.split('/')[-1]):])
#                                 else:
#                                     print('>>> {}'.format(buff_text))   # dir var
#                                     print_table(espdev.output, wide=16,
#                                                 autocol_tab=True, sort=False)
#                             else:
#                                 result = [
#                                     val for val in espdev.output if val.startswith(buff_text)]
#                                 if len(result) > 1:
#                                     comm_part = os.path.commonprefix(result)
#                                     if comm_part == buff_text:
#                                         if shell_mode['S']:
#                                             last_cmd = event.app.current_buffer.document.text
#                                             if local_path['p'] == '':
#                                                 g_p = [val[1]
#                                                        for val in prompt['p'][1:5]]
#                                                 b_p = [val[1]
#                                                        for val in prompt['p'][5:]]
#                                                 color_p = "\33[32;1m{}\033[0m:\u001b[34;1m{}\033[0m{}".format(
#                                                     "".join(g_p[:-1]), "".join(b_p), last_cmd)
#                                                 print(color_p)
#                                             else:
#                                                 m_p = [prompt['p'][0][1]]
#                                                 g_p = [val[1]
#                                                        for val in prompt['p'][1:5]]
#                                                 b_p = [val[1]
#                                                        for val in prompt['p'][5:]]
#                                                 color_p = "\u001b[35;1m{}\033[0m\33[32;1m{}\033[0m:\u001b[34;1m{}\033[0m{}".format(
#                                                     "".join(m_p), "".join(g_p[:-1]), "".join(b_p), last_cmd)
#                                                 print(color_p)
#                                             # format ouput
#                                             print_table(
#                                                 result, wide=28, format_SH=True)
#                                         else:
#                                             print('>>> {}'.format(buff_text))  # globals
#                                             print_table(result, wide=16,
#                                                         autowide=True)
#                                     else:
#                                         event.app.current_buffer.insert_text(
#                                             comm_part[len(buff_text):])
#                                 else:
#                                     event.app.current_buffer.insert_text(
#                                         result[0][len(buff_text):])
#
#             except Exception as e:
#                 # print(e)
#                 pass
#         run_in_terminal(tab_cmd_info)
#
#

    @kb.add('s-tab')
    def shif_tab(event):
        "Autocomplete shell commands"
        def autocomplete_sh_cmd():
            if flags.shell_mode['S']:
                buff_text = event.app.current_buffer.document.text
                result = [sh_cmd for sh_cmd in shell_commands
                          + custom_sh_cmd_kw if sh_cmd.startswith(buff_text)]
                if 'fw' in buff_text.split():
                    # print('Here: {}'.format(buff_text.split()))
                    if len(buff_text.split()) > 1:
                        result = [sh_cmd
                                  for sh_cmd in
                                  ['list', 'get', 'latest', 'update']
                                  if sh_cmd.startswith(buff_text.split()[-1])]
                        # print(result)
                        buff_text = buff_text.split()[-1]
                    else:
                        result = ['list', 'get', 'latest', 'update']
                        buff_text = ''
                if len(result) > 1:
                    comm_part = os.path.commonprefix(result)
                    if comm_part == buff_text:
                        last_cmd = buff_text
                        _printpath_cmd(last_cmd)

                        print_table(result)
                    else:
                        event.app.current_buffer.insert_text(
                            comm_part[len(buff_text):])
                else:
                    if len(result) > 0:
                        event.app.current_buffer.insert_text(
                            result[0][len(buff_text):])

        run_in_terminal(autocomplete_sh_cmd)
#
#

    @kb.add('s-right')
    def autocomplete_locals(event):
        glb = False
        if flags.shell_mode['S']:
            try:
                buff_text_frst_cmd = event.app.current_buffer.document.text.split(' ')[
                                                                                  0]
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

            def s_r_cmd_info(rest_part=rest, flag=glb, buff=buff_text,
                             output=cmd_ls_glb):
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
                                                last_cmd = event.app.current_buffer.document.text
                                                _printpath_cmd(last_cmd)
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
                                            last_cmd = event.app.current_buffer.document.text
                                            _printpath_cmd(last_cmd)

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
            run_in_terminal(s_r_cmd_info)
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
# @kb.add('c-p')
# def toggle_status_ram_msg(event):
#     "Toggle Right RAM status"
#     if status_encryp_msg['Toggle']:
#         if status_encryp_msg['S']:
#             status_encryp_msg['S'] = False
#         else:
#             status_encryp_msg['S'] = True
#
#     if not mem_show_rp['show']:
#         mem_show_rp['show'] = True
#         mem_show_rp['call'] = True
#     else:
#         mem_show_rp['show'] = False
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
