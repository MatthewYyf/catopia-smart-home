# config.py
# pico for water handling loadcell and water pump

# ----- Device Identifier -----
device_id = "003"

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = ""
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
WATER_PUMP_PIN = 22

LOAD_SENSOR_PIN_OUT = 15
LOAD_SENSOR_PIN_SCK = 14
LOAD_SENSOR_SCALE = 460
LOAD_SENSOR_ZERO_THRESHOLD_GRAMS = 2
