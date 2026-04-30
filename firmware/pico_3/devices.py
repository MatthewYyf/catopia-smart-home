from machine import Pin, ADC, Timer
import utime
from hx711 import HX711

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

class KibbleDispenser:
    def __init__(self, dir_pin, step_pin, load_sensor_out_pin, load_sensor_sck_pin, steps_per_rev=200):
        self.load_sensor = LoadSensor(load_sensor_out_pin, load_sensor_sck_pin)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.steps_per_rev = steps_per_rev
        self.dir_pin.value(1)

    def step_once(self, delay_us=1000):
        self.step_pin.value(1)
        utime.sleep_us(delay_us)
        self.step_pin.value(0)
        utime.sleep_us(delay_us)

    def step_n(self, n, delay_us=1000):
        for _ in range(n):
            self.step_once(delay_us)

    def dispense(self, max_weight):
        while True:
            weight = self.load_sensor.read()
            remaining = max_weight - weight

            if remaining <= 0:
                break
            elif remaining > 20:
                self.step_n(40, 800)
            elif remaining > 5:
                self.step_n(15, 1000)
            else:
                self.step_n(3, 1200)

            utime.sleep_ms(100)

    def state(self):
        return None
