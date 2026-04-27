import config
from machine import Pin, ADC, Timer
import utime

class PanTiltLaser:

    class LaserModule:
        def __init__(self, adc_pin):
            self.laser_sensor = Pin(adc_pin)

        def __on__(self):
            laser.value(1)

        def __off__(self):
            laser.value(0)

    class PanTiltSystem:
        """SG90 pulse range: 500µs (-90°) to 2400µs (+90°)"""
        min_us = 500    # -90°
        max_us = 2400   # +90°
        mid_us = 1450   # ~center (slightly under 1500 is typical for SG90)

        
        def __init__(self, pan_adc_pin, tilt_adc_pin):
            self.pan = PWM(Pin(pan_adc_pin), freq=config.DEFAULT_FREQUENCY)
            self.tilt = PWM(Pin(tilt_adc_pin), freq=config.DEFAULT_FREQUENCY)

        def angle_to_duty(self, angle):
            pulse_us = mid_us + (angle / 90) * ((max_us - min_us) / 2)
            duty = int(pulse_us / 20000 * 65535)
            return duty

        def set_angle(self, angle, servo):
            angle = max(-90, min(90, angle))
            servo.duty_u16(angle_to_duty(angle))

        def pan(self, angle):
            set_angle(self.set_angle(angle, self.pan))

        def tilt(self, angle):
            set_angle(self.set_angle(angle, self.tilt))

    def __init__(self, pan_adc_pin, tilt_adc_pin, laser_adc_pin):
        self.pan_tilt = pan
        self.laser = LaserModule(laser_adc_pin)
        
        self.auto_enabled = False

        self.target_pan = 0
        self.target_tilt = 0

        self.last_move_time = utime.ticks_ms()
        self.last_target_time = utime.ticks_ms()

    def start_auto(self):
        self.auto_enabled = True
        self.laser.on()
        self.pick_new_target()

    def stop_auto(self):
        self.auto_enabled = False
        self.laser.off()
        self.pan_tilt.set_position(0, 10)

    def pick_new_target(self):
        self.target_pan = random.randint(self.PAN_MIN, self.PAN_MAX)
        self.target_tilt = random.randint(self.TILT_MIN, self.TILT_MAX)

    def update(self):
        if not self.auto_enabled:
            return

        now = utime.ticks_ms()

        if utime.ticks_diff(now, self.last_target_time) > self.TARGET_INTERVAL_MS:
            self.pick_new_target()
            self.last_target_time = now

        if utime.ticks_diff(now, self.last_move_time) > self.MOVE_INTERVAL_MS:
            self.pan_tilt.move_toward(
                self.target_pan,
                self.target_tilt,
                step=2
            )
            self.last_move_time = now

    def state(self):
        return null