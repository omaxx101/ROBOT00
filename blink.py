from machine import Pin
from utime import sleep

# Create a Pin object for the onboard LED
led = Pin(25, Pin.OUT)  # "LED" refers to the built-in LED

print("Built-in LED starts flashing...")
try:
    while True:
        led.toggle()      # Switch LED state (ON/OFF)
        sleep(1)          # Wait 1 second
except KeyboardInterrupt:
    pass

led.off()
print("Finished.")
