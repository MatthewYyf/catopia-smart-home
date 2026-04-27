import config
from machine import Pin, ADC, Timer
import utime

class PanTiltLaser:

    class LaserModule:
        def __init__(self, adc_pin):
            self.laser_sensor = ADC(Pin(adc_pin))

        def __on__(self):
            # tbi

        def __off__(self):
            # tbi

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

    def on(slef):
        while True:
            


    def state(self):
        return null