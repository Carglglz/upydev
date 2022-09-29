WebSocket (ws) / WebSocket Secure (wss) TLS
===========================================

To enable WebREPL see
`WebREPL: a prompt over-wifi <http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi>`_
and `WebREPL: web-browser interactive prompt <http://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt>`_

See :ref:`WebSocketDevice development setup <examples:WebSocketDevice>`  

Steps to enable WebSecureREPL mode
----------------------------------

1. **Put** ``wss_repl.py`` and ``wss_helper.py`` **in the device**: to do this use ``update_upyutils`` command as:

  .. code-block:: console

      $ upydev update_upyutils

 This will upload :

 * ``sync_tool.py``
 * ``nanoglob.py``
 * ``shasum.py`` (to enable dsync)
 * ``upylog.py``
 * ``upynotify.py``
 * ``uping.py``
 * ``upysh.py`` (to enable dsync)
 * ``upysecrets.py`` (to enable random WebREPL passwords generation)
 * ``upysh2.py`` (to enable 'tree'  and 'du' command)
 * ``wss_repl.py`` (to enable WebSecureREPL)
 * ``wss_helper.py`` (to enable WebSecureREPL)

2. **Generate ROOT CA ECDSA private key and self-signed ROOT CA certificate** then **upload the ROOT CA certificate to the device**:

   To generate the key do:

   .. code-block:: console

      $ upydev kg ssl CA -tfkey

   ``-tfkey`` option is to send the ROOT CA certificate to the device.

   This will ask to set a passphrase, **Do not forget it because it will be needed to generate HOST and device keys/certificates**

3. **Generate HOST ECDSA private key and ROOT CA signed HOST certificate** :

  To generate the key do:

  .. code-block:: console

     $ upydev kg ssl host


  This will ask for the ROOT CA key passphrase to sign HOST certificate and then set another passphrase for HOST key, **Do not forget it because it will be needed to log into WebSecureREPL**

4. **Generate device ECDSA private key and ROOT CA signed device certificate**  then **upload them to the device**:

   To generate the key do:

   .. code-block:: console

      $ upydev kg ssl -tfkey

   ``-tfkey`` option is to send the key/cert to the device (so use this if connected directly to the AP of the device or a "secure" wifi e.g. local/home) If not connected to a "secure" wifi upload the key (it is stored in upydev.\__path__) by USB/Serial connection.

   This will ask for the ROOT CA key passphrase to be able to sign device certificate.

At this point there should be in the host verify locations path ``upydev.\__path__``:
  - ROOT CA key/cert pair
  - HOST key/cert pair
  - device cert.
And in the device:
  - ROOT CA cert
  - device key/cert pair.

.. note::

  This setup of ROOT CA-->HOST/device certificate chain enables TLS mutual authentication, and if the ROOT CA key/cert pair is exported to another
  host, it can generate its own HOST key/cert pair so it can perform a TLS mutual authentication too.
  This enables multihost support.

5. **Enable WebSecREPL/WebSecureREPL in device**

  Replace ``import webrepl`` for ``import wss_repl`` and ``webrepl.start()`` by
  ``wss_repl.start(ssl=True)``, in ``boot.py`` or ``main.py``.



After these steps WebSecureREPL or WebREPL over wss is now available:

.. code-block:: console

    $ upydev shl

Or if the global group ``UPY_G`` is configured already, any device in the global group
can be accessed with this mode using:


.. code-block:: console

    $ upydev shl@[DEVICE]


e.g.

.. code-block:: console

    mbp@cgg:~$ upydev shl@esp_room1
    Enter passphrase for key 'HOST_key@6361726c6f.pem':
    WebSecREPL with TLSv1.2 connected
    TLSv1.2 @ ECDHE-ECDSA-AES128-CCM8 - 128 bits Encryption

    MicroPython v1.18-165-g795370ca2-dirty on 2022-03-01; ESP32 module with ESP32
    Type "help()" for more information.

    - CTRL-k to see keybindings or -h to see help
    - CTRL-s to toggle shell/repl mode
    - CTRL-x or "exit" to exit
    esp32@esp_room1:~ $

.. note::

  Once WebSecREPL is enabled, device configuration can be updated with host passphrase
  as ``-p [password]:[passphrase]`` so it's not needed for logging anymore.

  .. code-block::

      $upydev config -t esp_room1.local -p mypasswd:mypassphr -@ esp_room1 -gg


WebSecureREPL protocol
----------------------

* **TLSv1.2 @ ECDHE-ECDSA-AES128-CCM8 - 128 bits Encryption**

* **Cipher suite ECDHE-ECDSA-AES128-CCM8** (recommended for embedded devices):

  - `Check Security State <https://ciphersuite.info/cs/TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8/>`_

  - `RFC-7925: TLS/DTLS IoT Profiles <https://www.rfc-editor.org/rfc/rfc7925>`_

* **ECDSA private keys**: Generated with *SECP256R1* (a.k.a *prime256v1* or *P-256*) see `RFC-5480 <https://www.ietf.org/rfc/rfc5480.txt>`_
