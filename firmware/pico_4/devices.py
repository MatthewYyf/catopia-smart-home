from machine import Pin, ADC, Timer
import utime

class PumpDevice:
    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.IN)
        self.off()

    def on(self):
        self.pin = Pin(pin_id, Pin.OUT)

    def off(self):
        self.pin = Pin(pin_id, Pin.IN)

    def toggle(self):
        if self.state() == 1:
            self.pin = Pin(pin_id, Pin.OUT)
        else:
            self.pin = Pin(pin_id, Pin.IN)

    def state(self):
        return self.pin.value()

class LoadSensor:
    def __init__(self, adc_pin):
        self.load_sensor = ADC(Pin(adc_pin))

    def read(self):
        # map force sensor outputs to actual weight
        return self.load_sensor.read_u16()