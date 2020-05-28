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
      version='0.3.3',
      description='Command line tool for wireless MicroPython devices',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
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
               'cryp_web_repl_dir/bin/crypweb_repl',
               'ssl_web_repl_dir/bin/sslweb_repl',
               'sh_srepl_dir/bin/sh_srepl',
               'pydfu_dir/bin/pydfu'],
      include_package_data=True,
      install_requires=['websocket-client', 'argcomplete', 'mpy-cross',
                        'esptool', 'prompt_toolkit', 'python-nmap',
                        'netifaces', 'requests', 'cryptography', 'Pygments',
                        'pyusb', 'upydevice>=0.2.3',
                        'jupyter_micropython_upydevice>=0.0.4'])
