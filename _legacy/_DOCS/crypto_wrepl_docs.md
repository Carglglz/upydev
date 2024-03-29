# CryptoWebREPL

### Steps to enable encryption mode:

1. **Put 'upysecrets.py' in the device**: to do this use '**update_upyutils**' command as:

   `$ upydev update_upyutils`

   This will upload : 

   * sync_tool.py
   * upylog.py
   * upynotify.py
   * upysecrets.py (to enable encryption)
   * upysh2.py (to enable 'tree' command)

2. **Generate RSA-2048 bits private key** and **upload it to the device**:

   To generate the key do:

   `$ upydev gen_rsakey -tfkey` 

   *-tfkey* option is to send the key to the device (so use this if connected directly to the AP of the device or a "secure" wifi e.g. local/home) If not connected to a "secure" wifi upload the key (it is stored in upydev.\__path__) by USB/Serial connection.

After these two steps encryption mode is now available:

`$ upydev crypto_wrepl` 

Or if there is already a global "UPY_G" named group, any device can be accessed with this mode using:

e.g.:

`$ upydev upy@esp_room1`  or `$ upydev upy@192.168.1.42` 

```bash
$ upydev upy@esp_room1
Welcome to CryptoWebREPL 0.0.1!
Initiating SECURE HANDSHAKE...
esp32@30aea4233564
Done!, INITIATING CRYPTOGRAPHERS..
CryptoWebREPL connected
>>>
MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
Type "help()" for more information.
Use CTRL-x to exit, Use CTRL-s,ENTER to toggle shell/repl mode, Use CTRL-k to see more info
esp32@esp_room1:~ $
```



### CryptoWebREPL protocol: AES - Cipher Block Chaining (CBC):

####  In every session two new keys are generated (one by the host, and one by the device) so encryption and decryption use different keys, as well as initialization vectors

* **Ciphers (aes256-cbc):** AES in CBC mode with a 256-bit key 

* **RSA-2048 bits private key:** The key is generated by the host and then uploaded to the device

* **The HANDSHAKE** (and key exchange method):

  * The host loads the RSA private key, generates 32 random bytes ( integers 0-255), then these bytes are used to select 32 values from the first 256 values of the RSA key. These values are added to the end of the RSA key, and using **sha256** the hash of key is computed. Then the session key is randomly generated selecting 32 values from the hash. The session IV is randomly generated selecting 16 values from the hash. The first 32 random bytes + 32 random index values of the hash + 16 random index values of hash makes the host token.
  * The host sends its token to the device so it can replicate the steps to generate the host session key and IV.
  * Then the devices generates its session key and session IV using the same method above, and sends its token to the host, so the host can replicate the steps to generate the device session key and IV.

  So in the token there is no explicit info about any key, the bytes in the token are just indexes.

* **E2EE communication (almost)**:

  Example:

  With encryption enabled, this command in the CryptoWebREPL:

  `>>> led.on()`

  Will look like this in the Websockets packages and Serial REPL:

  `>>> cp.crepl(b'886ab3a45537cbb40c951359e27265d3')`

  Or 

  ```
  >>> print('Hello')
  Hello
  
  >>>
  ```

  Will look like this:

  ```
  cp.crepl(b'32b73f35adc1e4332d4020bcc0268335')
  Hello # This is printed in the serial REPL but not forwarded to WebREPL
  b'1d9c213456f377e674643446defa0262' # This is what is forwarded to WebREPL
  ```

* **After exiting CryptoWebREPL**:

  The device will be soft-reset so session keys are erased from RAM.

### CryptoWebREPL : shell/repl

The CryptoWebREPL allows to toggle between shell and repl modes (Use 'CTRL-s' and then press 'ENTER' to do this)

The repl mode has some limitations:

- In encrypted mode the output of a command won't be received until its end (so no 'live output')

- In both encrypted and unencrypted modes CTRL-C cannot be use to break an infinite loop.

- To define a function/class or make a loop use the paste mode. (CTRL-E)

  *However the original WebREPL Terminal can be accessed from shell with 'wrepl' command*

  e.g.

  ```
  esp32@esp_room1:~ $ wrepl
  WARNING: ENCRYPTION DISABLED IN THIS MODE
  <-- Device esp32 MicroPython -->
  Use CTRL-x to exit, Use CTRL-k to see custom wrepl Keybdings
  Password:
  WebREPL connected
  >>>
  MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
  Type "help()" for more information.
  >>>
  >>>
  ```

  

**To see keybindings / shell commands info do 'CTRL-k': This will print**:

Custom keybindings:
- CTRL-x : to exit CryptoWebREPL Terminal

- CTRL-u : toggle encryption mode (on/off), this prints a right aligned status message

- CTRL-p : toggle encryption right aligned status message

- CTRL-e : paste mode in repl, (edit mode after 'edit' shell command)

- CTRL-d : ends paste mode in repl, (ends edit mode after 'edit' shell command)

- CTRL-c : KeyboardInterrupt, in normal mode, cancel in paste mode

- CTRL-r : to flush line buffer

- CTRL-o : to list files in cwd (ls shorcut command)

- CTRL-n : shows mem_info()

- CTRL-y : gc.collect() shortcut command

- CTRL-space : repeats last command

- CTRL-t : runs test_code.py if present

- CTRL-w : flush test_code from sys modules, so it can be run again

- CTRL-a : set cursor position at the beggining

- CTRL-f : toggle autosuggest mode (Fish shell like)

- CRTL-s , ENTER : toggle shell mode to navigate filesystem (see shell commands)

- CTRL-k : prints the custom keybindings (this list) (+ shell commands if in shell mode)

  
* Autocompletion commands:
     - tab to autocomplete device file / dirs names / raw micropython (repl commands)
     - shift-tab to autocomplete shell commands
     - shift-right to autocomplete local file / dirs names
     - shift-left,ENTER to toggle local path in prompt

* Device shell commands:
    * upysh commands:
        - sz   : list files and size in bytes
        - head : print the head of a file
        - cat  : prints the content of a file
        - mkdir: make directory
        - cd   : change directory (cd .. to go back one level)
        - pwd  : print working directory
        - rm   : to remove a file
        - rmdir: to remove a directory

    * custom shell commands:
        - ls  : list device files in colored format (same as pressing tab on empty line)
        - tree : to print a tree version of filesystem (if the ouput is to big won't work with encryption)
        - run  : to run a 'script.py' (To access again to the shell do CTRL-C)
        - df   : to see filesystem flash usage (or SD if already mounted as 'sd')
        - meminfo: to see RAM info
        - whoami : to see user, system and machine info
        - datetime: to see device datetime (if not set, will display uptime)
        - set_localtime : to set the device datetime from the local machine time
        - ifconfig: to see STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
        - ifconfig_t: to see STATION interface configuration in table format
                      (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
        - netscan: to scan WLANs available, (ESSID, MAC ADDRESS, CHANNEL, RSSI, AUTH MODE, HIDDEN)
        - apconfig: to see access POINT (AP) interface configuration (IP, SUBNET, GATEAWAY, DNS)
        - apconfig_t: to see access POINT (AP) interface configuration in table format
                     (SSID, BSSID, CHANNEL, AUTH, IP, SUBNET, GATEAWAY, DNS)
        - install: to install a library into the device with upip.
        - touch  : to create a new file (e.g. touch test.txt)
        - edit   : to edit a file (e.g. edit my_script.py)
        - get    : to get a file from the device
        - put    : to upload a file to the device
        - sync   : to get file (faster) from the device (use with > 10 KB files)
        - d_sync: to recursively sync a local directory with the device filesystem
        - wrepl  : to enter the original WebREPL terminal (no encryption mode)
        - reload : to delete a module from sys.path so it can be imported again.
        - exit   : to exit CryptoWebREPL Terminal
        - crypto_buffsize: to see buffer size of the device 'cryptographer'
                          or set it in case it is too small
                          (default 2048 bytes, e.g. increase to 4096) (crypto_buffsize 4096)

* Local shell commands:
    - pwdl   : to see local path
    - cdl    : to change local directory
    - lsl    : to list local directory
    - catl   : to print the contents of a local file
    - l_micropython: if "micropython" local machine version available in $PATH, runs it.
    - python : switch to local python3 repl
    - vim    : to edit a local file with vim  (e.g. vim script.py)
    - l_ifconfig: to see local machine STATION interface configuration (IP, SUBNET, GATEAWAY, DNS)
    - l_ifconfig_t: to see local machine STATION interface configuration in table format
                  (IP, SUBNET, GATEAWAY, DNS, ESSID, RSSI)
    - lsof : to scan TCP ports of the device (TCP ports 1-10000)
    - docs : to open MicroPython docs site in the default web browser, if a second term
            is passed e.g. 'docs machine' it will open the docs site and search for 'machine'

Some examples of these commands:

```
esp32@esp_room1:~ $ df
Filesystem      Size        Used       Avail        Use%     Mounted on
Flash          2.0 MB     512.0 KB     1.5 MB      25.3 %        /
esp32@esp_room1:~ $ ls
lib                          boot.py                      main.py
wifi_.config                 ap_.config                   webrepl_cfg.py
upy_pv_rsa30aea4233564.key  test_sync_dir
esp32@esp_room1:~ $ meminfo
Memory         Size        Used       Avail        Use%
RAM          116.188 KB  36.531 KB   79.656 KB     31.4 %
esp32@esp_room1:~ $ tree
lib <dir>
        ├────  sync_tool.py
        ├────  upylog.py
        ├────  upynotify.py
        ├────  upysecrets.py
        └────  upysh2.py
boot.py
main.py
webrepl_cfg.py
wifi_.config
ap_.config
test_sync_dir <dir>
        ├────  ATEXTFILE.txt
        ├────  THETESTCODE.py
        ├────  my_other_dir_sync <dir>
        │   └────  another_file.txt
        └────  test_subdir_sync <dir>
            ├────  SUBTEXT.txt
            └────  sub_sub_dir_test_sync <dir>
                ├────  level_2_subtext.txt
                └────  level_3_subtext.txt
```

