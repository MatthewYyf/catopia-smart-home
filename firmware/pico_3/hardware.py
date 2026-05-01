import config
from devices import PumpDevice, LoadSensor

class Hardware:
    def __init__(self):
        self.pump = PumpDevice(config.WATER_PUMP_PIN)
        self.load = LoadSensor(config.LOAD_SENSOR_PIN_OUT, config.LOAD_SENSOR_PIN_SCK)

    def state_dict(self):
        return {
            "pump": self.pump.state(),
            "load": self.load.read()
        }