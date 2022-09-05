### Example Tests to run with pytest command

- **test_esp32/test_espx.py**: Basic test to run with esp device
- **test_sh.py**: Tests collection of shell-repl commands
- **test_custom_cmd.py**: Example of custom tests using dictionaries
- **test_dev.py**: Test to run parametric test using yaml files.

To run do e.g.

```console
$ upydev pytest test_sh.py
```

or 

```console
$ upydev pytest test_basic/test_objs.yaml
```

#### Note:

Some tasks assume `led` is already defined in device i.e.

```python
from machine import Pin

led = Pin(13, Pin.OUT) # change the number to match your device
```

#### Note 2:

In `dev_tests/` dir there are scripts that are dynamically loaded in the device or need to be already there (depending on the test).

In `dev_tests/perf_bench` dir there are micropython performance benchmarks from `micropython/tests/perf_bench` and these can be run with:

```console
$ upydev pytest test_benchmark/test_perf*.yaml
```
