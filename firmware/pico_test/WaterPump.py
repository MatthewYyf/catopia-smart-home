from machine import Pin
import utime
pump_on_time = 2
pump_off_time = 5

# turn on pump
def turn_pump_on():
    relay_pin = Pin(22, Pin.OUT)

# turn off the pump
def turn_pump_off():
    relay_pin = Pin(22, Pin.IN)

# Run the pump
while True:
    turn_pump_on()
    utime.sleep(pump_on_time)  
    turn_pump_off()
    utime.sleep(pump_off_time)   
