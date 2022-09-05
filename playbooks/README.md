### Example playbooks

These playbooks showcase some combinations of directives.
To run modify the hosts to match your own devices and then e.g.
```console
$ upydev play mytask.yaml
```

#### Note:
Some tasks assume `led` is already defined in device i.e.

```python

from machine import Pin

led = Pin(13, Pin.OUT) # change the number to match your device

```
