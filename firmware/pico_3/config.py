# config.py
# pico for handling food loadcell and stepper motor

# ----- Device Identifier -----
device_id = "003"

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = "12345678"
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
LED_PIN = "LED"          # onboard LED
WATER_PUMP_PIN = 22
FEEDER_STEP_PIN = 16
FEEDER_DIR_PIN = 17
LOAD_SENSOR_PIN_OUT = 15
LOAD_SENSOR_PIN_SCK = 14
LOAD_SENSOR_SCALE = 460
LOAD_SENSOR_ZERO_THRESHOLD_GRAMS = 2
# STEPPER_DIR_PIN = 
# STEPPER_STEP_PIN =

# ----- Logic levels -----
ACTIVE_HIGH = 1
ACTIVE_LOW = 0

# ----- Safety / calibration -----
MAX_PUMP_SECONDS = 10
MAX_DISPENSE_GRAMS = 80

# Example calibration
STEPS_PER_GRAM = 25
