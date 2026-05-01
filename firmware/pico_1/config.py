# config.py
# pico for handling pant/tilt servos + 5v laser module

# ----- Device Identifier -----
device_id = "001"

# ----- Hotspot Login -----

SSID = "catopia"
PASSWORD = ""
PI_IP = "10.42.0.1"

# ----- GPIO assignments -----
PAN_PIN = 0
TILT_PIN = 1
LASER_PIN = 2

# ----- Pulse Range -----
DEFAULT_FREQUENCY = 50

# ----- Boundary -----

MAX_PAN = 90
MIN_PAN = -90
MAX_TILT = -10
MIN_TILT = -90