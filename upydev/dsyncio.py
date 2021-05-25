#!/usr/bin/env python3

import os
import time
import json
import hashlib
from binascii import hexlify


# AVOID FILES

_CONFG_FILES = ['.upydev_wdlog.json', 'upydev_.config']


# from @Roberthh #https://forum.micropython.org/viewtopic.php?f=2&t=7512
def rmrf(d):  # Remove file or tree
    try:
        if os.path.isdir(d):  # Dir
            for f in os.listdir(d):
                if f not in ('.', '..'):
                    rmrf(os.path.join(d, f))  # File or Dir
            os.rmdir(d)
        else:  # File
            os.remove(d)
    except Exception as e:
        print(e)
        print("rm of '%s' failed" % d)


# WATCHDOG LOG FILE

def get_hash(file):
    with open(file, 'rb') as file_to_hash:
        raw_file = file_to_hash.read()
    file_hash = hashlib.sha256()
    file_hash.update(raw_file)
    hashed_file = file_hash.digest()
    return hexlify(hashed_file).decode()


def get_hash_cwd_dict(path='.'):
    hash_cwd_dict = {name: get_hash(os.path.join(path, name)) for name in
                     [file for file in os.listdir(path) if
                      os.path.isfile(os.path.join(path, file))
                      and file not in _CONFG_FILES]}
    return hash_cwd_dict


def check_wdlog(path='.', save_wdlog=True):
    # WD_LOG EXISTS, CHECK AND COMPARE
    deleted_files = []
    if '.upydev_wdlog.json' in os.listdir(path):
        print('Checking upydev cwd watchdog logfile...')
        with open('{}/'.format(path) + '.upydev_wdlog.json', 'r') as wd_logfile:
            hash_wdlog_dict = json.loads(wd_logfile.read())
            files_wdlog_list = list(hash_wdlog_dict.keys())
            files_cwd = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and file not in _CONFG_FILES]
            # New files in cwd:
            new_files_to_upload = [file for file in files_cwd if file not in files_wdlog_list]
            if len(new_files_to_upload) > 0:
                print('New files to upload:')
                for nf in new_files_to_upload:
                    print('- {}'.format(nf))
            # Files deleted in cwd:
            deleted_files = [file for file in files_wdlog_list if file not in files_cwd]
            # Files modified in cwd:
            files_wdlog_list = [file for file in files_wdlog_list if file not in deleted_files]
            modified_files = [file for file in files_wdlog_list if get_hash(os.path.join(path, file)) != hash_wdlog_dict[file]]
            if len(modified_files) > 0:
                print('Modified files to upload:')
                for mf in modified_files:
                    print('- {}'.format(mf))
            if len(deleted_files) > 0:
                print('Deleted files to remove:')
                for df in deleted_files:
                    print('- {}'.format(df))
            # MAKE NEW WD_LOG
            if save_wdlog:
                with open('{}/'.format(path) + '.upydev_wdlog.json', 'w') as wd_logfile:
                    hash_cwd_dict = get_hash_cwd_dict(path=path)
                    wd_logfile.write(json.dumps(hash_cwd_dict))
            global_files_to_upload = new_files_to_upload + modified_files
            if len(global_files_to_upload) == 0:
                print('No new or modified files found')
            return global_files_to_upload, deleted_files
    # WD_LOG does NOT exist, CREATE NEW ONE
    else:
        if save_wdlog:
            print('.upydev_wdlog.json not found, creating new one...')
            with open('{}/'.format(path) + '.upydev_wdlog.json', 'w') as wd_logfile:
                hash_cwd_dict = get_hash_cwd_dict(path=path)
                wd_logfile.write(json.dumps(hash_cwd_dict))
            print('Done!')
        global_files_to_upload = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and file not in _CONFG_FILES]
        for file in global_files_to_upload:
            print('- {}'.format(file))
        return global_files_to_upload, deleted_files


class LTREE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", level=0, is_last=False, is_root=True,
                 carrier="│   ", hidden=False):
        if is_root:
            print('\u001b[34;1m{}\033[0m'.format(path))
        os.chdir(path)
        r_path = path
        path = "."
        if hidden:
            l = os.listdir(path)
        else:
            l = [f for f in os.listdir(path) if not f.startswith('.')]
        nf = len([file for file in l if not os.stat("%s/%s" % (path, file))[0] & 0x4000])
        nd = len(l) - nf
        ns_f, ns_d = 0, 0
        l.sort()
        if len(l) > 0:
            last_file = l[-1]
        else:
            last_file = ''
        for f in l:
            st = os.stat("%s/%s" % (path, f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + "  \u001b[34;1m%s\033[0m" % f)
                if f == last_file and level == 0:
                    carrier = "    "
                os.chdir(f)
                level += 1
                lf = last_file == f
                if level > 1:
                    if lf:
                        carrier += "     "
                    else:
                        carrier += "    │"
                ns_f, ns_d = self.__call__(level=level, is_last=lf,
                                           is_root=False, carrier=carrier,
                                           hidden=hidden)
                if level > 1:
                    carrier = carrier[:-5]
                os.chdir('..')
                level += (-1)
                nf += ns_f
                nd += ns_d
            else:
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + " %s" % (f))
        if is_root:
            nd_str = 'directories'
            nf_str = 'files'
            if nd == 1:
                nd_str = 'directory'
            if nf == 1:
                nf_str = 'file'
            print('\n{} {}, {} {}'.format(nd, nd_str, nf, nf_str))
            if r_path != ".":
                os.chdir('..')
        else:
            return (nf, nd)

    def _treeindent(self, lev, f, lastfile, is_last=False, carrier=None):
        if lev == 0:
            if f != lastfile:
                return "├──"
            else:
                return "└──"
        else:
            if f != lastfile:
                return carrier + "    ├────"
            else:
                return carrier + "    └────"


tree = LTREE()


class DISK_USAGE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", dlev=0, max_dlev=0, hidden=False, absp=True):
        if path != ".":
                if not os.stat(path)[0] & 0x4000:
                    print('{:9} {}'.format(self.print_filesys_info(os.stat(path)[6]), path))
                else:
                    if hidden:
                        resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path)}
                    else:
                        resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
                    for dir in resp.keys():

                        if not os.stat(dir)[0] & 0x4000:
                            if absp:
                                print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir))
                            else:
                                print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir.split('/')[-1]))

                        else:
                            if dlev < max_dlev:
                                dlev += 1
                                self.__call__(path=dir, dlev=dlev, max_dlev=max_dlev, hidden=hidden)
                                dlev += (-1)
                            else:
                                if absp:
                                    print('{:9} \u001b[34;1m{}\033[0m'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir))
                                else:
                                    print('{:9} \u001b[34;1m{}\033[0m'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir.split('/')[-1]))

        else:
            if hidden:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path)}
            else:
                resp = {path+'/'+dir: os.stat(path+'/'+dir)[6] for dir in os.listdir(path) if not dir.startswith('.')}
            for dir in resp.keys():

                if not os.stat(dir)[0] & 0x4000:
                    print('{:9} {}'.format(self.print_filesys_info(resp[dir]), dir))

                else:
                    if dlev < max_dlev:
                        dlev += 1
                        self.__call__(path=dir, dlev=dlev, max_dlev=max_dlev, hidden=hidden)
                        dlev += (-1)
                    else:
                        print('{:9} \u001b[34;1m{}\033[0m'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir))

    def print_filesys_info(self, filesize):
        _kB = 1024
        if filesize < _kB:
            sizestr = str(filesize) + " by"
        elif filesize < _kB**2:
            sizestr = "%0.1f KB" % (filesize / _kB)
        elif filesize < _kB**3:
            sizestr = "%0.1f MB" % (filesize / _kB**2)
        else:
            sizestr = "%0.1f GB" % (filesize / _kB**3)
        return sizestr

    def get_dir_size_recursive(self, dir):
        return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0] & 0x4000 else self.get_dir_size_recursive(dir+'/'+f) for f in os.listdir(dir)])


du = DISK_USAGE()


def print_filesys_info(filesize):
    _kB = 1024
    if filesize < _kB:
        sizestr = str(filesize) + " by"
    elif filesize < _kB**2:
        sizestr = "%0.1f KB" % (filesize / _kB)
    elif filesize < _kB**3:
        sizestr = "%0.1f MB" % (filesize / _kB**2)
    else:
        sizestr = "%0.1f GB" % (filesize / _kB**3)
    return sizestr


def get_dir_size_recursive(dir):
    return sum([os.stat(dir+'/'+f)[6] if not os.stat(dir+'/'+f)[0] &
                0x4000 else get_dir_size_recursive(dir+'/'+f) for f in
                os.listdir(dir)])


def d_sync_recursive(folder, devIO=None, rootdir='./', root_sync_folder=None,
                     show_tree=False, args=None, dev_name=None):
    t0 = time.time()
    # type_file_dict = {True: '<f>', False: '<d>'}
    if folder == root_sync_folder:
        print('DIRECTORY TO SYNC: {}'.format(folder))
        print('DIRECTORY SIZE: {}'.format(
                                          print_filesys_info(
                                              get_dir_size_recursive(folder))))
    if show_tree:
        print('DIRECTORY TREE STRUCTURE:\n')
        tree(path=folder)
    time.sleep(1)
    print('\n')
    print('***** {} *****'.format(folder))
    print('\n')
    directory = folder
    file_list = None
    file_list_abs_path = []
    dir_list_abs_path = []
    current_dir = directory
    # get directory structure:
    print('ROOT DIRECTORY: {}'.format(rootdir))
    print('DIRECTORY TO SYNC: {}'.format(directory))
    print('\n')
    if directory != '.':
        print('CHECKING IF DIRECTORY {} IN: {}'.format(
            directory.split('/')[-1], rootdir))
    if directory.split('/')[-1] in os.listdir(rootdir) or directory == '.':
        print('DIRECTORY {} FOUND'.format(directory))
        print('\n')
        print('FILES/DIRS IN DIRECTORY {}:'.format(directory))
        if directory == '.':
            directory = ''
        du(path='./{}'.format(directory), absp=False, hidden=True)
        # for file in os.listdir(directory):
        #     print('- {} {} [{}]'.format(type_file_dict[os.path.isfile(os.path.join(current_dir, file))],
        #                            file, print_filesys_info(os.stat(os.path.join(current_dir, file))[6])))
        if directory == '':
            directory = '.'
        file_list = os.listdir(directory)
        print('\n')
        if args.wdl:
            modified_files, deleted_files = check_wdlog(path=directory)
        for file in file_list:
            if os.path.isfile(os.path.join(current_dir, file)):
                if args.wdl:
                    wdl_file = file.split('/')[-1]
                    if wdl_file not in _CONFG_FILES and wdl_file in modified_files:
                        file_list_abs_path.append(os.path.join(current_dir, file))
                else:
                    if file not in _CONFG_FILES:
                        file_list_abs_path.append(os.path.join(current_dir, file))
            elif os.path.isdir(os.path.join(current_dir, file)):
                dir_list_abs_path.append(os.path.join(current_dir, file))

    if file_list_abs_path:
        print('LIST OF FILES TO UPLOAD:')
        for file in file_list_abs_path:
            print('- {}'.format(file.split('/')[-1]))
        print('\n')
    else:
        pass
        # print('NO FILES TO UPLOAD')

    if dir_list_abs_path:
        print('LIST OF SUBDIRS TO CREATE:')
        for subdir in dir_list_abs_path:
            print('- {}'.format(subdir.split('/')[-1]))
        print('\n')
    else:
        # print('NO SUBDIRS TO CREATE')
        pass
    # Now create the root sync dir:
    if './' == rootdir:
        rootdir = ''
    if not devIO.dev.connected:
        devIO.dev.connect()
    dev_root_list = devIO.dev.wr_cmd("import os;'{}' in os.listdir('{}')".format(current_dir.split('/')[-1],
                                     rootdir), silent=True, rtn_resp=True)
    if not dev_root_list and current_dir != '.':
        print('\n')
        print('MAKING DIR: {}'.format(current_dir))
        print('\n')
        devIO.dev.wr_cmd("os.mkdir('{}')".format(current_dir), silent=True)
        print('\n')

    if file_list_abs_path:
        print('UPLOADING FILES TO {}'.format(current_dir))
        if len(file_list_abs_path) > 1:
            if directory == '.':
                file_list_abs_path = [file.split('/')[-1] for file in file_list_abs_path]
            for file in file_list_abs_path:
                print('- {}'.format(file))
            args.fre = file_list_abs_path
            if directory != '.':
                args.s = os.path.join(*file_list_abs_path[0].split('/')[:-1])
            else:
                args.s = '/'
            print('\n')
            devIO.put_files(args, dev_name)
            args.fre = None
            time.sleep(0.2)
        elif len(file_list_abs_path) == 1:
            args.fre = None
            file_to_put = file_list_abs_path[0]
            if directory == '.':
                file_to_put = file.split('/')[-1]
            print('- {}'.format(file_to_put), end='\n\n')
            file_to_put_in_dev = file_to_put.replace('./', '')
            devIO.put(file_to_put, file_to_put_in_dev, ppath=True, dev_name=dev_name)
            time.sleep(0.2)
    else:
        print('NO FILES TO UPLOAD')
    # Now create subdirs:
    print('\n')
    if dir_list_abs_path:
        print('MAKING DIRS NOW...')
        for dir_ in dir_list_abs_path:
            print('\n')
            current_dir = dir_
            # Now create the root sync dir:
            try:
                dir_to_sync = directory
                dir_to_find = current_dir.split('/')[-1]
                dev_directory = devIO.dev.cmd("'{}' in os.listdir('{}')".format(dir_to_find, dir_to_sync),
                                              silent=True, rtn_resp=True)
            except Exception as e:
                pass
            if not dev_directory:
                print('Creating dir: {}'.format(current_dir))
                devIO.dev.cmd("os.mkdir('{}')".format(current_dir))
            else:
                print('DIRECTORY {} ALREADY EXISTS'.format(dir_to_find))
    else:
        print('NO DIRS TO MAKE')

    if args.rf:
        # remove dirs and files? -rf?
        # Deleted Files
        if args.wdl:
            if deleted_files:
                print('FILES TO REMOVE:')
                for dfile in deleted_files:
                    try:
                        devIO.dev.cmd("os.remove('{}/{}')".format(directory, dfile), silent=True, rtn_resp=True)
                        if directory != '.':
                            print('- {}/{}'.format(directory, dfile))
                        else:
                            print('- {}'.format(dfile))
                    except Exception as e:
                        print(e)
                print('\nFILES DELETED')

        else:
            pass

        # Deleted Directories

        if directory != '.':
            dirs_in_dev = devIO.dev.cmd("['{0}/'+dir for dir in os.listdir('{0}') if os.stat('{0}/'+dir)[0] & 0x4000]".format(directory),
                                        silent=True, rtn_resp=True)

            deleted_dirs = [dir for dir in dirs_in_dev if dir not in dir_list_abs_path]

            if deleted_dirs:
                print('\nDIRS TO REMOVE:')
                for ddir in deleted_dirs:
                    print('- {} '.format(ddir))
                    is_dir_empty = devIO.dev.cmd("from upysh2 import rmrf;not len(os.listdir('{}')) > 0".format(ddir),
                                                 silent=True, rtn_resp=True)
                    if is_dir_empty:
                        devIO.dev.cmd("os.rmdir('{}')".format(ddir), silent=True,
                                      rtn_resp=True)
                    else:
                        devIO.dev.cmd("rmrf('{}')".format(ddir), silent=True,
                                      rtn_resp=True)


    root = directory
    for dir_ in dir_list_abs_path:
        d_sync_recursive(dir_, devIO, root, args=args, dev_name=dev_name)

    if directory == root_sync_folder:
        print('Done in : {:.2f} seconds'.format(time.time()-t0))


def dev2host_sync_recursive(folder, devIO=None, rootdir='./', root_sync_folder=None,
                            show_tree=False, args=None, dev_name=None):
    t0 = time.time()
    # type_file_dict = {True: '<f>', False: '<d>'}
    if not devIO.dev.connected:
        devIO.dev.connect()
    devIO.dev.wr_cmd('from upysh2 import du', silent=True)
    dev_dir_size = devIO.dev.wr_cmd("du.get_dir_size_recursive('{}')".format(folder),
                                    silent=True, rtn_resp=True)
    _folder = folder if folder != '.' else ''
    if folder == root_sync_folder:
        print('DIRECTORY TO SYNC: {}:/{}'.format(dev_name, _folder))
        print('DIRECTORY SIZE: {}'.format(
                                          print_filesys_info(dev_dir_size)))
        platform = devIO.dev.wr_cmd('import os; os.uname().sysname', silent=True,
                                    rtn_resp=True)
        # print(platform)
        if platform == 'pyboard':
            rootdir = '.'
    if show_tree:
        devIO.dev.wr_cmd('from upysh2 import tree', silent=True)
        print('DIRECTORY TREE STRUCTURE:\n')
        devIO.dev.wr_cmd("tree('{}')".format(folder), follow=True)
        # tree(path=folder)
    time.sleep(1)
    print('\n')
    print('***** {}:/{} *****'.format(dev_name, _folder))
    print('\n')
    directory = folder
    file_list = None
    file_list_abs_path = []
    dir_list_abs_path = []
    current_dir = directory
    # get directory structure:
    print('ROOT DIRECTORY: {}:{}'.format(dev_name, rootdir))
    print('DIRECTORY TO SYNC: {}'.format(directory))
    print('\n')
    if directory != '.':
        print('CHECKING IF DIRECTORY {} IN: {}'.format(
            directory.split('/')[-1], rootdir))
    check_dir = devIO.dev.wr_cmd("os.listdir('{}')".format(rootdir), silent=True,
                                 rtn_resp=True)
    # print(check_dir)
    if directory.split('/')[-1] in check_dir or directory == '.':
        print('DIRECTORY {} FOUND'.format(directory))
        print('\n')
        print('FILES/DIRS IN DIRECTORY {}:'.format(directory))
        if directory == '.':
            directory = ''
        _directory = directory if directory else '.'
        devIO.dev.wr_cmd("du(path='{}', hidden=True)".format(_directory), follow=True)
        # for file in os.listdir(directory):
        #     print('- {} {} [{}]'.format(type_file_dict[os.path.isfile(os.path.join(current_dir, file))],
        #                            file, print_filesys_info(os.stat(os.path.join(current_dir, file))[6])))
        if directory == '':
            directory = '.'
        file_list = devIO.dev.wr_cmd("os.listdir('{}')".format(directory), silent=True,
                                     rtn_resp=True)
        print('\n')
        # if args.wdl:
        #     modified_files, deleted_files = check_wdlog(path=directory)
        is_dir_cmd = "import os; os.stat('{}')[0] & 0x4000"
        for file in file_list:
            if not devIO.dev.wr_cmd(is_dir_cmd.format(os.path.join(current_dir, file)),
                                    silent=True, rtn_resp=True):  # os.path.join(current_dir, file)
                # if args.wdl:
                #     wdl_file = file.split('/')[-1]
                #     if wdl_file not in _CONFG_FILES and wdl_file in modified_files:
                #         file_list_abs_path.append(os.path.join(current_dir, file))
                # else:
                file_list_abs_path.append(os.path.join(current_dir, file))
            else:
                dir_list_abs_path.append(os.path.join(current_dir, file))

    if file_list_abs_path:
        print('LIST OF FILES TO DOWNLOAD:')
        for file in file_list_abs_path:
            print('- {}'.format(file.split('/')[-1]))
        print('\n')
    else:
        pass
        # print('NO FILES TO UPLOAD')

    if dir_list_abs_path:
        print('LIST OF SUBDIRS TO CREATE:')
        for subdir in dir_list_abs_path:
            print('- {}'.format(subdir.split('/')[-1]))
        print('\n')
    else:
        # print('NO SUBDIRS TO CREATE')
        pass
    # Now create the root sync dir:
    if './' == rootdir:
        rootdir = '.'
    # if not devIO.dev.connected:
    #     devIO.dev.connect()
    host_root_list = current_dir.split('/')[-1] in os.listdir(rootdir)
    if not host_root_list and current_dir != '.':
        print('\n')
        print('MAKING DIR: {}'.format(current_dir))
        print('\n')
        # devIO.dev.wr_cmd("os.mkdir('{}')".format(current_dir), silent=True)
        os.mkdir(current_dir)
        print('\n')

    _files_to_delete_in_host = []
    if file_list_abs_path:
        print('DOWNLOADING FILES TO {}'.format(current_dir))
        os.chdir(current_dir)
        if len(file_list_abs_path) > 1:
            if directory == '.':
                file_list_abs_path = [file.split('/')[-1] for file in file_list_abs_path]
            for file in file_list_abs_path:
                print('- {}'.format(file))
            args.fre = file_list_abs_path
            if directory != '.':
                args.s = os.path.join(*file_list_abs_path[0].split('/')[:-1])
            else:
                args.s = '/'
            print('\n')
            if args.rf:
                # print(args.fre)
                _files_to_delete_in_host += [os.path.join(current_dir, _file) for _file in os.listdir() if os.path.isfile(_file) and os.path.join(current_dir, _file) not in file_list_abs_path]
                # print(_files_to_delete_in_host)
            devIO.get_files(args, dev_name)
            args.fre = None
            time.sleep(0.2)
        elif len(file_list_abs_path) == 1:
            args.fre = None
            file_to_get = file_list_abs_path[0]
            if directory == '.':
                file_to_get = file.split('/')[-1]
            print('- {}'.format(file_to_get), end='\n\n')
            file_to_get_from_dev = file_to_get.replace('./', '')
            devIO.get(file_to_get, file_to_get_from_dev, ppath=True, dev_name=dev_name)
            time.sleep(0.2)
            if args.rf:
                # print(file_to_get, file_to_get_from_dev)
                _files_to_delete_in_host += [os.path.join(current_dir, _file) for _file in os.listdir() if os.path.isfile(_file) and os.path.join(current_dir, _file) != file_to_get]
                # print(_files_to_delete_in_host)
        if current_dir != '.':
            for level in current_dir.split('/'):
                if level != '.':
                    os.chdir('..')
    else:
        print('NO FILES TO DOWNLOAD')
        # if args.rf check files to delete
        if args.rf:
            _files_to_delete_in_host += [os.path.join(current_dir, _file) for _file in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, _file))]
            # print(_files_to_delete_in_host)
    # Now create subdirs:
    print('\n')
    _dirs_to_delete_in_host = []
    if dir_list_abs_path:
        print('MAKING DIRS NOW...')
        if args.rf:
            # print(current_dir, os.listdir(current_dir))
            if current_dir in os.listdir():
                _dirs_to_delete_in_host += [os.path.join(current_dir, _dir) for _dir in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, _dir)) and os.path.join(current_dir, _dir) not in dir_list_abs_path]
            # print(_dirs_to_delete_in_host)
        for dir_ in dir_list_abs_path:
            print('\n')
            current_dir = dir_
            # Now create the root sync dir:
            try:
                dir_to_sync = directory
                dir_to_find = current_dir.split('/')[-1]
                # print(os.getcwd())
                dev_directory = dir_to_find in os.listdir(dir_to_sync)
            except Exception as e:
                print(e, dir_to_sync)
            if not dev_directory:
                print('Creating dir: {}'.format(current_dir))
                os.mkdir(current_dir)
            else:
                print('DIRECTORY {} ALREADY EXISTS'.format(dir_to_find))
    else:
        print('NO DIRS TO MAKE')
        # if args.rf check dirs to delete
        # print(current_dir, os.listdir(current_dir))
        if args.rf:
            _dirs_to_delete_in_host += [os.path.join(current_dir, _dir) for _dir in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, _dir))]
        # print(_dirs_to_delete_in_host)

    if args.rf:
        # Delete Files

        if _files_to_delete_in_host:
            print('FILES TO REMOVE:')
            for dfile in _files_to_delete_in_host:
                try:
                    os.remove(dfile)
                    if directory != '.':
                        print('- {}'.format(dfile))
                    else:
                        print('- {}'.format(dfile))
                except Exception as e:
                    print(e)
            print('\nFILES DELETED')

        # Deleted Directories

        if _dirs_to_delete_in_host:

            print('\nDIRS TO REMOVE:')
            for ddir in _dirs_to_delete_in_host:
                print('- {} '.format(ddir))
                is_dir_empty = not len(os.listdir(ddir)) > 0
                if is_dir_empty:
                    os.rmdir(ddir)
                else:
                    rmrf(ddir)
            print('\nDIRS DELETED')


    root = directory
    for dir_ in dir_list_abs_path:
        dev2host_sync_recursive(dir_, devIO, root, args=args, dev_name=dev_name)

    if directory == root_sync_folder:
        print('Done in : {:.2f} seconds'.format(time.time()-t0))
