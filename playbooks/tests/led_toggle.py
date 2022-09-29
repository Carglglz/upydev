import time

for i in range(5):
    print(f"This is a loaded script: {i}")
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)
