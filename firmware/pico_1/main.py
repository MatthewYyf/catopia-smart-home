import network
import time
import urequests
import config
from hardware import Hardware

POST_DATA_URL = "http://{}:8000/api/devices/{}/telemetry".format(
    config.PI_IP, config.device_id
)

GET_COMMAND_URL = "http://{}:8000/api/devices/{}/commands/next".format(
    config.PI_IP, config.device_id
)

hw = Hardware()

COMMAND_INTERVAL_MS = 500
TELEMETRY_INTERVAL_MS = 1000
LOOP_SLEEP_MS = 20

last_command_check = time.ticks_ms()
last_telemetry_send = time.ticks_ms()


def get_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return wlan


def connect_wifi(timeout=10):
    wlan = get_wlan()

    if wlan.isconnected():
        print("Already connected:", wlan.ifconfig())
        return True

    print("Connecting to Wi-Fi...")
    wlan.connect(config.SSID, config.PASSWORD)

    start = time.time()

    while not wlan.isconnected():
        print("Waiting...")
        time.sleep(1)

        if time.time() - start > timeout:
            print("Wi-Fi connection timed out")
            return False

    print("Connected:", wlan.ifconfig())
    return True


def reconnect_wifi():
    wlan = get_wlan()
    print("Reconnecting Wi-Fi...")

    try:
        wlan.disconnect()
    except Exception:
        pass

    time.sleep(1)
    return connect_wifi()


def server_check():
    try:
        res = urequests.get(GET_COMMAND_URL)
        res.close()
        print("Server reachable")
        return True
    except Exception as e:
        print("Server check failed:", e)
        return False


def ensure_connection():
    wlan = get_wlan()

    if not wlan.isconnected():
        if not connect_wifi():
            return False

    return True


def send_data():
    if not ensure_connection():
        print("Skipping send_data: no connection")
        return

    payload = hw.state_dict()

    try:
        res = urequests.post(POST_DATA_URL, json=payload)
        res.close()
    except Exception as e:
        print("POST failed:", e)


def handle_command(cmd):
    if not cmd:
        return

    cmd_type = cmd.get("type")
    params = cmd.get("params", {})

    print("Command received:", cmd_type)

    if cmd_type == "START_AUTO_LASER":
        hw.pan_tilt_system.start_auto()

    elif cmd_type == "STOP_AUTO_LASER":
        hw.pan_tilt_system.stop_auto()

    elif cmd_type == "LASER_ON":
        hw.pan_tilt_system.laser.on()

    elif cmd_type == "LASER_OFF":
        hw.pan_tilt_system.laser.off()

    elif cmd_type == "SET_LASER_POSITION":
        pan = params.get("pan", 0)
        tilt = params.get("tilt", -45)
        hw.pan_tilt_system.pan_tilt.set_position(pan, tilt)

    else:
        print("Unknown command:", cmd_type)


def check_command():
    if not ensure_connection():
        print("Skipping check_command: no connection")
        return

    try:
        res = urequests.get(GET_COMMAND_URL)
        cmd = res.json()
        res.close()

        if cmd:
            handle_command(cmd)

    except Exception as e:
        print("GET command failed:", e)


def main():
    global last_command_check
    global last_telemetry_send

    connect_wifi()

    while True:
        now = time.ticks_ms()

        hw.pan_tilt_system.update()

        if time.ticks_diff(now, last_command_check) >= COMMAND_INTERVAL_MS:
            check_command()
            last_command_check = now

        if time.ticks_diff(now, last_telemetry_send) >= TELEMETRY_INTERVAL_MS:
            send_data()
            last_telemetry_send = now

        time.sleep_ms(LOOP_SLEEP_MS)


main()