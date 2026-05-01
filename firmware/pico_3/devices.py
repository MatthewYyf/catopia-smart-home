from machine import Pin, ADC, Timer
import utime
from hx711 import HX711

class PumpDevice:
    def __init__(self, pin_id):
        self.pin_id = pin_id
        self.pin = Pin(pin_id, Pin.IN)
        self.off()

    def on(self):
        self.pin = Pin(self.pin_id, Pin.OUT)
        print("Pump ON")

    def off(self):
        self.pin = Pin(self.pin_id, Pin.IN)

    def toggle(self):
        if self.state() == 1:
            self.pin = Pin(self.pin_id, Pin.OUT)
        else:
            self.pin = Pin(self.pin_id, Pin.IN)

    def state(self):
        return self.pin.value()

class LoadSensor:
    def __init__(self, pin_out, pin_sck):
        pin_OUT = Pin(pin_out, Pin.IN, pull=Pin.PULL_DOWN)
        pin_SCK = Pin(pin_sck, Pin.OUT)
        self.load_sensor = HX711(pin_SCK, pin_OUT)
        self.load_sensor.tare()

    def read(self):
        # map force sensor outputs to actual weight
        grams = self.load_sensor.get_value()//430 # Example conversion, needs calibration
        if grams < 2:
                return 0
        return grams


    def state(self):
        return None
