### Task files for testing directives

These task files check and demonstrate the usage of available directives.
To run use `task_xx_nh.yaml` files or modify the hosts to match your own devices, then e.g.
```console
$ upydev play task_command_nh.yaml
```

#### Note:
Some tasks assume `led` is already defined in device i.e.

```python

from machine import Pin

led = Pin(13, Pin.OUT) # change the number to match your device

```

