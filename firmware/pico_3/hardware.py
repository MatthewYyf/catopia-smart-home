import config
from devices import LedDevice, PumpDevice, LoadSensor

class Hardware:
    def __init__(self):
        self.pump = PumpDevice(config.WATER_PUMP_PIN)
        self.load = LoadSensor(
            config.LOAD_SENSOR_PIN_OUT,
            config.LOAD_SENSOR_PIN_SCK,
            config.LOAD_SENSOR_SCALE,
            config.LOAD_SENSOR_ZERO_THRESHOLD_GRAMS,
        )

    def state_dict(self):
        return {
            "pump": self.pump.state(),
            "load": self.load.read()
        }
