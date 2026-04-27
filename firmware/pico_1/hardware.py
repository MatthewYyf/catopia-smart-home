import config
from devices import PanTiltSystem

class Hardware:
    def __init__(self):
        self.pan_tilt_system = PanTiltSystem(config.PAN_PIN, config.TILT_PIN)
        

    


    # def state_dict(self):
    #     return {
    #         "led": self.led.state(),
    #         "pump": self.pump.state(),
    #         "load": self.load.read()
    #     }