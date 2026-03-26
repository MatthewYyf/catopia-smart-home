# config.py

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = "12345678"
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
LED_PIN = "LED"          # onboard LED
WATER_PUMP_PIN = 15
FEEDER_STEP_PIN = 16
FEEDER_DIR_PIN = 17
KNOB_ADC_PIN = 26

# ----- Logic levels -----
ACTIVE_HIGH = 1
ACTIVE_LOW = 0

# ----- Safety / calibration -----
MAX_PUMP_SECONDS = 10
MAX_DISPENSE_GRAMS = 80

# Example calibration
STEPS_PER_GRAM = 25