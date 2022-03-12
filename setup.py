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
      version='0.3.9',
      description='Command line tool for wired/wireless MicroPython devices',
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
      packages=['upydev', 'upydev.shell'],
      zip_safe=False,
      scripts=['cli/upydev_cli/bin/upydev',
               'cli/shell-repl/web_repl_cli/bin/web_repl',
               'cli/shell-repl/bin/sslweb_repl',
               'cli/shell-repl/bin/sh_srepl',
               'cli/shell-repl/bin/blerepl',
               'cli/pydfu_cli/bin/pydfu'],
      include_package_data=True,
      install_requires=['websocket-client>=1.2.3', 'argcomplete',
                        'esptool', 'prompt_toolkit', 'python-nmap',
                        'netifaces', 'requests', 'cryptography', 'Pygments',
                        'pyusb', 'packaging', 'upydevice>=0.3.4',
                        'jupyter_micropython_upydevice>=0.0.7',
                        'braceexpand'])
