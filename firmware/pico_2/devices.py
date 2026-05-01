from machine import Pin
import utime
from hx711 import HX711


class KibbleDispenser:
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
            return {
                "weight": self.read()
            }

    def __init__(
        self,
        dir_pin,
        step_pin,
        load_sensor_out_pin,
        load_sensor_sck_pin,
        steps_per_rev=200,
        direction=1
    ):
        self.load_sensor = KibbleDispenser.LoadSensor(
            load_sensor_out_pin,
            load_sensor_sck_pin
        )

        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)

        self.steps_per_rev = steps_per_rev
        self.direction = direction

        self.dir_pin.value(direction)
        self.step_pin.value(0)

    def set_direction(self, direction):
        self.direction = direction
        self.dir_pin.value(direction)

    def step_once(self, delay_us=1000):
        self.step_pin.value(1)
        utime.sleep_us(delay_us)
        self.step_pin.value(0)
        utime.sleep_us(delay_us)

    def step_n(self, num_steps, delay_us=1000):
        for _ in range(num_steps):
            self.step_once(delay_us)

    def stop(self):
        self.step_pin.value(0)

    def read_weight(self):
        return self.load_sensor.read()

    def state(self):
        return {
            "weight": self.read_weight(),
            "direction": self.direction
        }

    def dispense(self, target_weight, timeout_ms=30000):
        """
        Dispense kibble until the load sensor reaches target_weight.

        Far from target: faster, larger steps.
        Near target: slower, smaller steps.
        """

        start_time = utime.ticks_ms()

        while True:
            weight = self.load_sensor.read()
            remaining = target_weight - weight

            print("Weight:", weight, "Remaining:", remaining)

            if remaining <= 0:
                break

            if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout_ms:
                print("Dispense timeout")
                break

            if remaining > 30:
                # Fast dispense
                self.step_n(80, 600)

            elif remaining > 15:
                # Medium-fast dispense
                self.step_n(40, 800)

            elif remaining > 5:
                # Slow dispense
                self.step_n(15, 1200)

            elif remaining > 2:
                # Very slow near target
                self.step_n(5, 1600)

            else:
                # Tiny final pulses
                self.step_n(2, 2200)

            utime.sleep_ms(150)

        self.stop()
        print("Dispense complete. Final weight:", self.load_sensor.read())