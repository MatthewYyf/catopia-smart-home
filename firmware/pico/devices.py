from machine import Pin, ADC

class LedDevice:
    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.OUT)
        self.pin.off()

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

    def toggle(self):
        self.pin.value(0 if self.pin.value() else 1)

    def state(self):
        return self.pin.value()


class PumpDevice:
    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.OUT)
        self.pin.off()

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

    def state(self):
        return self.pin.value()


class KnobSensor:
    def __init__(self, adc_pin):
        self.adc = ADC(adc_pin)

    def read(self):
        return self.adc.read_u16()