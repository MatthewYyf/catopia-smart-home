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
    def __init__(self, pin_out, pin_sck, scale=460, zero_threshold_grams=2):
        self.scale = scale
        self.zero_threshold_grams = zero_threshold_grams
        self.data_pin = Pin(pin_out, Pin.IN)
        self.clock_pin = Pin(pin_sck, Pin.OUT)
        self.load_sensor = HX711(self.clock_pin, self.data_pin)
        self.tare()

    def tare(self):
        self.load_sensor.tare()

    def read(self):
        grams = self.load_sensor.get_value() / self.scale
        if abs(grams) < self.zero_threshold_grams:
            return 0
        return round(grams, 1)

    def state(self):
        return None
