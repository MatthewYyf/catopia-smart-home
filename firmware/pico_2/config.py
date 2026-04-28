# config.py
# pico for water handling loadcell and water pump

# ----- Device Identifier -----
device_id = "002"

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = "12345678"
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
WATER_PUMP_PIN = 22
LOAD_SENSOR_PIN = 28

# ----- Logic levels -----
ACTIVE_HIGH = 1
ACTIVE_LOW = 0

# ----- Safety / calibration -----
MAX_PUMP_SECONDS = 10
MAX_DISPENSE_GRAMS = 80

# Example calibration
STEPS_PER_GRAM = 25