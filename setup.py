#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-07-11T23:29:40+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-15T00:05:55+00:00

from setuptools import setup


def readme():
    with open('README.md', 'r', encoding="utf-8") as f:
        return f.read()


setup(name='upydev',
      version='0.1.7',
      description='Command line tool for wireless Micropython devices',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='http://github.com/Carglglz/upydev',
      author='Carlos Gil Gonzalez',
      author_email='carlosgilglez@gmail.com',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Terminals'
      ],
      license='MIT',
      packages=['upydev'],
      zip_safe=False,
      scripts=['upydev_dir/bin/upydev', 'upy_tool_dir/bin/upytool',
               'sync_server_dir/bin/sync_server', 'upycmd_dir/bin/upycmd',
               'upycmd_r_dir/bin/upycmd_r',
               'web_repl_cmd_dir/bin/web_repl_cmd',
               'web_repl_cmd_r_dir/bin/web_repl_cmd_r',
               'web_repl_dir/bin/web_repl',
               'dbg_wrepl_cmd_dir/bin/dbg_wrepl',
               'cryp_web_repl_dir/bin/crypweb_repl'],
      include_package_data=True,
      install_requires=['argcomplete', 'mpy-cross', 'esptool', 'prompt_toolkit',
                        'python-nmap', 'netifaces', 'requests', 'cryptography',
                        'upydevice'])
