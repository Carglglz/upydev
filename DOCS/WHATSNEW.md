- #### **New in version 0.1.9 --> Mode 'ssl_wrepl': a REPL/SHELL with TLS v1.2** (*experimental)

The idea behind this mode is to try to mimic a SSH protocol. (But right now although SSL works this does not mean it is secure)

(This mode needs upysh in the device, so if it is not already installed or it's not included in the frozen modules do: `$ upydev install -f upysh`)

How to use it:

* TLDR: To test the functionality of this mode **without encryption** do (or test it with Esp8266):

  `$ upydev ssl_wrepl -nem`

* With **Encryption mode**: This needs some configuration before (which is basically generate an ECDSA private key and pass it to the device). Follow [this instructions](https://github.com/Carglglz/upydev/blob/master/DOCS/SSLWebREPL_docs.md) to do this.

  **Encryption mode works only with esp32. Esp8266 seems to be to slow for SSL repl*

  After the configuration is done, to use this mode do:

  `$ upydev ssl_wrepl` 

  Or if there is already a global "UPY_G" named group, any device can be accessed with this mode using:

  e.g.:

  `$ upydev ssl@esp_room1`  or `$ upydev ssl@192.168.1.42` 

  ![](https://raw.githubusercontent.com/Carglglz/upydev/master/DOCS/SSLWebREPL_demo.gif)

  

* #### **New in version 0.2.0: Mode 'sh_srepl', a Serial shell/repl** ** (*experimental)

  See [SERIAL SHELL-REPL instructions](https://github.com/Carglglz/upydev/blob/master/DOCS/SERIAL_SHELL_REPL_docs.md) for detailed info or

  See **uPydev Mode/Tools** : **sh_srepl** and **shr** modes.

  

* #### **New in version 0.2.6: 'git' integration in SHELLS (SSL/Web/SERIAL)**: (This needs 'git' available in path, see [Git](https://git-scm.com))

  ![](https://github.com/Carglglz/upydev/blob/master/DOCS/ssl_git.gif?raw=true)

* #### **New in version 0.2.7: Mode 'wssrepl' and 'wssl': (This needs WebSecureREPL enabled):**

  - For **WebSecureREPL:** `$ upydev wssrepl`
  - For **WebSecureREPL + SSL REPL-SHELL:** 
    - `$ upydev wssl@esp_room1` or `$ upydev wssl@192.168.1.42`

  See [changelog](https://github.com/Carglglz/upydev/blob/master/changelog.md) for new commands in both SSLWeb SHELL-REPL and SERIAL SHELL-REPL.

