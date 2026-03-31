import network
import socket
import json
import time
from machine import Pin, PWM

# ─── Configuration ────────────────────────────────────────────────────────────
WIFI_SSID     = "yuxuan_hotspot"      # <-- your Wi-Fi network name
WIFI_PASSWORD = "!"  # <-- your Wi-Fi password
LISTEN_PORT   = 5005

# GPIO pins for the two servos
PAN_PIN  = 20   # Left/Right servo  → GP0
TILT_PIN = 18   # Up/Down servo     → GP1
# ──────────────────────────────────────────────────────────────────────────────


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Connecting to Wi-Fi", end="")
    timeout = 20  # seconds
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("\nConnected! IP:", wlan.ifconfig()[0])
        return wlan.ifconfig()[0]
    else:
        raise RuntimeError("Wi-Fi connection failed — check SSID and password")


def angle_to_duty(angle):
    """
    Convert a servo angle (0–180°) to a 16-bit PWM duty cycle.

    Standard hobby servo pulse widths:
      0°   →  ~1 ms pulse  →  duty ~1000  (out of 65535 at 50 Hz)
      90°  →  ~1.5 ms pulse → duty ~5000
      180° →  ~2 ms pulse  →  duty ~9000

    Tune MIN_DUTY / MAX_DUTY slightly if your servos don't reach
    full travel or buzz at the ends.
    """
    MIN_DUTY = 1000
    MAX_DUTY = 9000
    angle = max(0, min(180, angle))  # clamp just in case
    return int(MIN_DUTY + (angle / 180.0) * (MAX_DUTY - MIN_DUTY))


def main():
    ip = connect_wifi()

    # Set up servos at 50 Hz (standard for hobby servos)
    pan_servo  = PWM(Pin(PAN_PIN),  freq=50)
    tilt_servo = PWM(Pin(TILT_PIN), freq=50)

    # Centre both servos on startup
    pan_servo.duty_u16(angle_to_duty(90))
    tilt_servo.duty_u16(angle_to_duty(90))
    print("Servos centred at 90°")

    # Open UDP socket
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("0.0.0.0", LISTEN_PORT))
    print(f"Listening for UDP commands on {ip}:{LISTEN_PORT}")

    while True:
        try:
            data, addr = udp.recvfrom(128)
            cmd = json.loads(data)

            axis  = cmd.get("axis")
            angle = float(cmd.get("angle", 90))
            duty  = angle_to_duty(angle)

            if axis == "pan":
                pan_servo.duty_u16(duty)
            elif axis == "tilt":
                tilt_servo.duty_u16(duty)

            # Optional: print to Thonny console for debugging
            # print(f"{axis} → {angle:.1f}° (duty {duty})")

        except Exception as e:
            print("Error:", e)
            # Keep running even if one packet is malformed


main()
