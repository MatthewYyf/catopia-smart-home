import random
import config
from machine import Pin, PWM
import utime


class PanTiltLaser:

    class LaserModule:
        def __init__(self, pin_id):
            self.laser = Pin(pin_id, Pin.OUT)
            self.off()

        def on(self):
            self.laser.value(1)

        def off(self):
            self.laser.value(0)

        def state(self):
            return self.laser.value()

    class PanTiltSystem:
        """SG90 pulse range: 500µs (-90°) to 2400µs (+90°)"""

        MIN_US = 500
        MAX_US = 2400
        MID_US = 1450

        PAN_MIN = -90
        PAN_MAX = 90
        TILT_MIN = -90
        TILT_MAX = -10

        def __init__(self, pan_pin, tilt_pin):
            self.pan_servo = PWM(Pin(pan_pin))
            self.tilt_servo = PWM(Pin(tilt_pin))

            self.pan_servo.freq(config.DEFAULT_FREQUENCY)
            self.tilt_servo.freq(config.DEFAULT_FREQUENCY)

            self.pan_angle = 0
            self.tilt_angle = -45

            self.set_position(self.pan_angle, self.tilt_angle)

        def angle_to_duty(self, angle):
            pulse_us = self.MID_US + (angle / 90) * ((self.MAX_US - self.MIN_US) / 2)
            duty = int(pulse_us / 20000 * 65535)
            return duty

        def set_angle(self, servo, angle):
            servo.duty_u16(self.angle_to_duty(angle))

        def set_pan(self, angle):
            self.pan_angle = max(self.PAN_MIN, min(self.PAN_MAX, angle))
            self.set_angle(self.pan_servo, self.pan_angle)

        def set_tilt(self, angle):
            self.tilt_angle = max(self.TILT_MIN, min(self.TILT_MAX, angle))
            self.set_angle(self.tilt_servo, self.tilt_angle)

        def set_position(self, pan_angle, tilt_angle):
            self.set_pan(pan_angle)
            self.set_tilt(tilt_angle)

        def move_toward(self, target_pan, target_tilt, step=2):
            if abs(self.pan_angle - target_pan) <= step:
                new_pan = target_pan
            elif self.pan_angle < target_pan:
                new_pan = self.pan_angle + step
            else:
                new_pan = self.pan_angle - step

            if abs(self.tilt_angle - target_tilt) <= step:
                new_tilt = target_tilt
            elif self.tilt_angle < target_tilt:
                new_tilt = self.tilt_angle + step
            else:
                new_tilt = self.tilt_angle - step

            self.set_position(new_pan, new_tilt)

    def __init__(self, pan_pin, tilt_pin, laser_pin):
        self.pan_tilt = self.PanTiltSystem(pan_pin, tilt_pin)
        self.laser = self.LaserModule(laser_pin)

        self.auto_enabled = False

        self.target_pan = 0
        self.target_tilt = -45

        self.last_move_time = utime.ticks_ms()
        self.last_target_time = utime.ticks_ms()

        self.PAN_MIN = -90
        self.PAN_MAX = 90
        self.TILT_MIN = -90
        self.TILT_MAX = -10

        self.target_interval_ms = random.randint(500, 1200)
        self.MOVE_INTERVAL_MS = 40

    def start_auto(self):
        self.auto_enabled = True
        self.laser.on()
        self.pick_new_target()

    def stop_auto(self):
        self.auto_enabled = False
        self.laser.off()
        self.pan_tilt.set_position(0, -45)

    def pick_new_target(self):
        self.target_pan = random.randint(self.PAN_MIN, self.PAN_MAX)
        self.target_tilt = random.randint(self.TILT_MIN, self.TILT_MAX)
        self.target_interval_ms = random.randint(500, 1200)

    def update(self):
        if not self.auto_enabled:
            return

        now = utime.ticks_ms()

        if utime.ticks_diff(now, self.last_target_time) > self.target_interval_ms:
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
        return {
            "auto_enabled": self.auto_enabled,
            "laser": self.laser.state(),
            "pan_angle": self.pan_tilt.pan_angle,
            "tilt_angle": self.pan_tilt.tilt_angle,
            "target_pan": self.target_pan,
            "target_tilt": self.target_tilt,
        }