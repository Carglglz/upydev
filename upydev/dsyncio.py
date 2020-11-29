#!/usr/bin/env python3

import os
import time
import json
import hashlib
from binascii import hexlify


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
                      and '.upydev_wdlog.json' not in file]}
    return hash_cwd_dict


def check_wdlog(path='.', save_wdlog=True):
    # WD_LOG EXISTS, CHECK AND COMPARE
    if '.upydev_wdlog.json' in os.listdir(path):
        print('Checking upydev cwd watchdog logfile...')
        with open('{}/'.format(path) + '.upydev_wdlog.json', 'r') as wd_logfile:
            hash_wdlog_dict = json.loads(wd_logfile.read())
            files_wdlog_list = list(hash_wdlog_dict.keys())
            files_cwd = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and '.upydev_wdlog.json' not in file]
            # New files in cwd:
            new_files_to_upload = [file for file in files_cwd if file not in files_wdlog_list]
            if len(new_files_to_upload) > 0:
                print('New files to upload:')
                for nf in new_files_to_upload:
                    print('- {}'.format(nf))
            # Files modified in cwd:
            modified_files = [file for file in files_wdlog_list if get_hash(os.path.join(path, file)) != hash_wdlog_dict[file]]
            if len(modified_files) > 0:
                print('Modified files to upload:')
                for mf in modified_files:
                    print('- {}'.format(mf))
            # MAKE NEW WD_LOG
            if save_wdlog:
                with open('{}/'.format(path) + '.upydev_wdlog.json', 'w') as wd_logfile:
                    hash_cwd_dict = get_hash_cwd_dict(path=path)
                    wd_logfile.write(json.dumps(hash_cwd_dict))
            global_files_to_upload = new_files_to_upload + modified_files
            if len(global_files_to_upload) == 0:
                print('No new or modified files found')
            return global_files_to_upload
    # WD_LOG DO NOT EXISTS, CREATE NEW ONE
    else:
        if save_wdlog:
            print('.upydev_wdlog.json not found, creating new one...')
            with open('{}/'.format(path) + '.upydev_wdlog.json', 'w') as wd_logfile:
                hash_cwd_dict = get_hash_cwd_dict(path=path)
                wd_logfile.write(json.dumps(hash_cwd_dict))
            print('Done!')
        global_files_to_upload = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and '.upydev_wdlog.json' not in file]
        for file in global_files_to_upload:
            print('- {}'.format(file))
        return global_files_to_upload


class LTREE:

    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path=".", level=0, is_last=False, is_root=True,
                 carrier="    ", hidden=False):
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
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + "  %s <dir>" % f)
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
                print(self._treeindent(level, f, last_file, is_last=is_last, carrier=carrier) + "  %s" % (f))
        if is_root:
            print('{} directories, {} files'.format(nd, nf))
            if r_path != ".":
                os.chdir('..')
        else:
            return (nf, nd)

    def _treeindent(self, lev, f, lastfile, is_last=False, carrier=None):
        if lev == 0:
            return ""
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
                                    print('{:9} {} {}'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir, '<dir>'))
                                else:
                                    print('{:9} {} {}'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir.split('/')[-1], '<dir>'))

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
                        print('{:9} {} {}'.format(self.print_filesys_info(self.get_dir_size_recursive(dir)), dir, '<dir>'))

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
    print('CHECKING IF DIRECTORY {} IN: {}'.format(
        directory.split('/')[-1], rootdir))
    if directory.split('/')[-1] in os.listdir(rootdir):
        print('DIRECTORY {} FOUND'.format(directory))
        print('\n')
        print('FILES/DIRS IN DIRECTORY {}:'.format(directory))
        du(path='./{}'.format(directory), absp=False, hidden=True)
        # for file in os.listdir(directory):
        #     print('- {} {} [{}]'.format(type_file_dict[os.path.isfile(os.path.join(current_dir, file))],
        #                            file, print_filesys_info(os.stat(os.path.join(current_dir, file))[6])))
        file_list = os.listdir(directory)
        print('\n')
        if args.wdl:
            modified_files = check_wdlog(path=directory)
        for file in file_list:
            if os.path.isfile(os.path.join(current_dir, file)):
                if args.wdl:
                    wdl_file = file.split('/')[-1]
                    if wdl_file != '.upydev_wdlog.json' and wdl_file in modified_files:
                        file_list_abs_path.append(os.path.join(current_dir, file))
                else:
                    file_list_abs_path.append(os.path.join(current_dir, file))
            elif os.path.isdir(os.path.join(current_dir, file)):
                dir_list_abs_path.append(os.path.join(current_dir, file))
    print('LIST OF FILES TO UPLOAD:')
    for file in file_list_abs_path:
        print('- {}'.format(file.split('/')[-1]))
    print('\n')
    print('LIST OF SUBDIRS TO CREATE:')
    for subdir in dir_list_abs_path:
        print('- {}'.format(subdir.split('/')[-1]))
    print('\n')
    # Now create the root sync dir:
    if './' == rootdir:
        rootdir = ''
    if not devIO.dev.connected:
        devIO.dev.connect()
    dev_root_list = devIO.dev.wr_cmd("os.listdir('{}')".format(rootdir), silent=True,
                                     rtn_resp=True)
    if current_dir.split('/')[-1] not in dev_root_list:
        print('\n')
        print('MAKING DIR: {}'.format(current_dir))
        print('\n')
        devIO.dev.wr_cmd("os.mkdir('{}')".format(current_dir), silent=True)
        print('\n')
    print('UPLOADING FILES TO {}'.format(current_dir))
    if len(file_list_abs_path) > 1:
        for file in file_list_abs_path:
            print('- {}'.format(file))
        args.fre = file_list_abs_path
        args.s = os.path.join(*file_list_abs_path[0].split('/')[:-1])
        devIO.put_files(args, dev_name)
        args.fre = None
        time.sleep(0.2)
        # shr_cp.sh_repl("print('Done!')")
        time.sleep(0.2)
    elif len(file_list_abs_path) == 1:
        file_to_put = file_list_abs_path[0]
        print('- {}'.format(file_to_put))
        devIO.put(file_to_put, file_to_put)
        # shr_cp.sh_repl("print('Done!')")
        time.sleep(0.2)
    else:
        print('NO FILES IN DIR TO UPLOAD')
    # Now create subdirs:
    print('\n')
    print('MAKING SUBDIRS NOW...')
    for dir_ in dir_list_abs_path:
        print('\n')
        current_dir = dir_
        # Now create the root sync dir:
        try:
            dir_to_sync = directory
            dev_directory = devIO.dev.cmd("os.listdir('{}')".format(dir_to_sync),
                                          silent=True, rtn_resp=True)
        except Exception as e:
            pass
        if not current_dir.split('/')[-1] in dev_directory:
            print('Creating dir: {}'.format(current_dir))
            devIO.dev.cmd("os.mkdir('{}')".format(current_dir))
        else:
            print('DIRECTORY {} ALREADY EXISTS'.format(current_dir.split('/')[-1]))
    if len(dir_list_abs_path) == 0:
        print('NO MORE SUBDIRS')
    root = directory
    for dir_ in dir_list_abs_path:
        d_sync_recursive(dir_, devIO, root, args=args, dev_name=dev_name)

    if directory == root_sync_folder:
        print('Done in : {:.2f} seconds'.format(time.time()-t0))
