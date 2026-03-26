import config
from devices import LedDevice, PumpDevice, KnobSensor

class Hardware:
    def __init__(self):
        self.led = LedDevice(config.LED_PIN)
        self.pump = PumpDevice(config.WATER_PUMP_PIN)
        self.knob = KnobSensor(config.KNOB_ADC_PIN)

    def state_dict(self):
        return {
            "led": self.led.state(),
            "pump": self.pump.state(),
            "knob": self.knob.read(),
        }