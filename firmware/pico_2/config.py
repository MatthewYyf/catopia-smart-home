# config.py
# pico for water handling loadcell and water pump

# ----- Device Identifier -----
device_id = "002"

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = "12345678"
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
LOAD_SENSOR_OUT_PIN = 15
LOAD_SENSOR_SCK_PIN = 14
LOAD_SENSOR_SCALE = 460
LOAD_SENSOR_ZERO_THRESHOLD_GRAMS = 2

STEPPER_DIR_PIN = 1
STEPPER_STEP_PIN = 0
STEPS_PER_REVOLUTION = 200