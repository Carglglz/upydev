### OTA + SSL build
- This build drops BLE, giving enough space for ssl io buffers (16KB)
+ 10KB free RAM
- Adds shell support freezing modules (`nanoglob.py`, `shasum.py`, `upysh.py`, `upysh2.py`)
- Adds OTA support, and OTA client module (`ota.py`) to allow OTA firmware updates
