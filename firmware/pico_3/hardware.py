import config
from devices import LedDevice, PumpDevice, LoadSensor

class Hardware:
    def __init__(self):
        self.led = LedDevice(config.LED_PIN)
        self.pump = PumpDevice(config.WATER_PUMP_PIN)
        self.load = LoadSensor(config.LOAD_SENSOR_PIN)

    def state_dict(self):
        return {
            "led": self.led.state(),
            "pump": self.pump.state(),
            "load": self.load.read()
        }