.. upydev documentation master file, created by
   sphinx-quickstart on Thu Oct  1 02:33:14 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

upydev
=============

.. image:: https://raw.githubusercontent.com/Carglglz/upydev/master/uPydevlogo.png
   :target: https://github.com/Carglglz/upydev
   :alt: Upydev Logo
   :align: center
   :width: 25%


Command line tool
------------------
**uPydev** is an acronym of '**MicroPy**\ thon **dev**\ ice', and it is intended to be a
command line tool to make easier the development, prototyping and testing process of
devices based on boards running MicroPython. It is intended to be cross-platform and
connection agnostic (Serial, WiFi and Bluetooth Low Energy).

* Lincense: MIT
* Documentation: https://upydev.readthedocs.io.

Features
--------

* Tools to allow configuration, management, communication and control of MicroPython devices.
* Command line Autocompletion
* File IO operations (upload, download one or multiple files, recursively sync directories...)
* SHELL-REPL: Serial, WiFi (WebREPL/WebSecureREPL) and Bluetooth Low Energy
* OTA\* Firmware updates WiFi (TCP/SSL), BLE (\*esp32 only)
* Custom commands for debugging, testing and prototyping.
* Group mode to operate with multiple devices


Installing
----------

Install ``upydev`` by running:

.. code-block:: console

    $ pip install upydev

To update to the latest version available:

.. code-block:: console

    $ pip install --upgrade upydev

To get development version:

.. code-block:: console

    $ pip install https://github.com/Carglglz/upydev/tree/develop.zip

To get help, use ``h`` or ``help`` command :

.. code-block:: console

    $ upydev help

Or see help about a specific command ``$ upydev [COMMAND] -h``:

.. code-block:: console

    $ upydev put -h
    usage:  put [-h] [-dir DIR] [-rst] file/pattern/dir [file/pattern/dir ...]

    upload files to device

    positional arguments:
      file/pattern/dir  indicate a file/pattern/dir to upload

    optional arguments:
      -h, --help        show this help message and exit
      -dir DIR          path to upload to
      -rst              to soft reset after upload
