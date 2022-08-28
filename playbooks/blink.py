# led must be previously defined e.g.
# uncomment this is that is not the case:

# from machine import Pin
# led = Pin(13, Pin.OUT)

led.on()
time.sleep(1)
led.off()
print("blink")
