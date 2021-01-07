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

* Command line for configuration/management/communication/control of MicroPython devices.
* Autocompletion
* File IO operations (put, get, sync...)
* SHELL-REPL modes: Serial, WiFi (SSL/WebREPL), BLE
* Custom commands for debugging/testing/prototyping
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
