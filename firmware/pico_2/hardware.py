import config
from devices import LedDevice, PumpDevice, KnobSensor

class Hardware:
    def __init__(self):
        self.kibble_dispenser = KibbleDispenser(config.STEPPER_DIR_PIN, config.STEPPER_OUT_PIN, config.LOAD_SENSOR_OUT_PIN, config.LOAD_SENSOR_SCK_PIN)

    def state_dict(self):
        return {
            "load": self.load.read()
        }