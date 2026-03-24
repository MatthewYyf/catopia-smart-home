"""
This Raspberry Pi Pico MicroPython code was developed by newbiely.com
This Raspberry Pi Pico code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pico/raspberry-pi-pico-force-sensor
"""

from machine import ADC, Pin
import time

# Define the pin connected to the FSR force sensor
FORCE_SENSOR_PIN = 28  # The Raspberry Pi Pico pin GP28 (ADC2) connected to the force sensor

# Initialize ADC on the specified pin
force_sensor = ADC(Pin(FORCE_SENSOR_PIN))

# Main loop
while True:
    analog_reading = force_sensor.read_u16()  # Read the raw analog value (0-65535)
    analog_reading = analog_reading // 64  # Scale it down to 0-1023 range to match Arduino

    print("Force sensor reading = ", analog_reading)  # Print the raw analog reading

    if analog_reading < 6553:       # from 0 to 6552
        print(" -> no pressure")
    elif analog_reading < 13107:    # from 6553 to 13106
        print(" -> light touch")
    elif analog_reading < 32767:    # from 13107 to 32766
        print(" -> light squeeze")
    elif analog_reading < 52428:    # from 32767 to 52427
        print(" -> medium squeeze")
    else:                           # from 52428 to 65535
        print(" -> big squeeze")

    time.sleep(1)  # Delay for 1000 milliseconds


# MUST CALIBRATE WITH KNOWN WEIGHT!!!!!!!!
