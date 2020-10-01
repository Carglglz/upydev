#### GLOBAL GROUP OF DEVICES

**Make a global group of uPy devices named "UPY_G" to enable redirection to a specific device:** 

Make a global group named "UPY_G" of devices, so next time any command can be redirected to any device within the group:

Example:

`$ upydev make_group -g -f UPY_G -devs esp_room1 192.168.1.42 mypass esp_room2 192.168.1.54 mypass2`

To see the devices saved in this global group do:

```
$ upydev see -G UPY_G -g
GROUP NAME: UPY_G
# DEVICES: 2
DEVICE NAME: esp_room1, IP: 192.168.1.42
DEVICE NAME: esp_room2, IP: 192.168.1.54
```

*To add or remove devices from this group use "mg_group" command (see uPydev Mode/Tools)*

Now any command can be redirected to one of these devices with the "-@" option:

```
$ upydev info -@ esp_room1
SYSTEM NAME: esp32
NODE NAME: esp32
RELEASE: 1.12.0
VERSION: v1.12 on 2019-12-20
MACHINE: ESP32 module with ESP32
```

*Option `-@` has autocompletion on tab so hit tab and see what devices are available*

------



### Atom / Visual Studio Code INTEGRATION with PLATFORMIO TERMINAL 

- ##### ATOM:

  To do this go to `Atom Settings --> Packages -->` Then search for `platformio-ide-terminal` and click on `Settings`. Here go to `Custom Texts` section: (There are up to 8 "custom texts" or commands that can be customised) These custom text will be pasted an executed in the Terminal when called. And this can be done with keybindings or key-shortcuts. For example:

  - **To automate upload the current file:**

    In `Custom text 1`  write:  `upydev put -f $F` 

  - **To automate run the current file:**

    In `Custom text 2`  write:  `upydev run -f $F` 

  - **To automate open the wrepl:**

    In `Custom text 3`  write:  `upydev wrepl`

  - **To automate diagnose:**

    In `Custom text 4`  write:  `upydev diagnose` 

    

  Now configure the Keybindings, to do this go to `Settings --> Keybindings --> your keymap file` 

  Then in `keymap.cson` add: (This is an example, the key combination can be changed)

  ```
  'atom-workspace atom-text-editor:not([mini])':
    'ctrl-shift-d': 'platformio-ide-terminal:insert-custom-text-4'
    'ctrl-cmd-u': 'platformio-ide-terminal:insert-custom-text-1'
    'ctrl-cmd-x': 'platformio-ide-terminal:insert-custom-text-2'
    'ctrl-cmd-w': 'platformio-ide-terminal:insert-custom-text-3'
  ```

   Save the file and now when pressing these key combinations should paste the command and run it in the Terminal.

- ##### Visual Studio Code:

  Using tasks and adding the shortcut in keybinds.json file for example:

  Task:

  ```json
  "version": "2.0.0",
      "tasks": [
          {
              "label": "upydev_upload",
              "type": "shell",
              "command": "upydev",
              "args": ["put", "-f", "${file}"],
              "options": {
                  "cwd": "${workspaceFolder}"
              },
              "presentation": {
                  "echo": true,
                  "reveal": "always",
                  "focus": true,
                  "panel": "shared",
                  "showReuseMessage": true,
                  "clear": false
              },
              "problemMatcher": []
          }, ]
  ```

  Keybinding.json

  ```json
  {
          "key": "ctrl+cmd+u",
          "command": "workbench.action.tasks.runTask",
          "args": "upydev_upload"
      }
  ```
