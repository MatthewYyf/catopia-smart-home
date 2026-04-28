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
    except:
        pass

    time.sleep(1)
    return connect_wifi()


def server_check():
    """
    Try a lightweight GET request to confirm we can reach the Pi server.
    Returns True if successful, False otherwise.
    """
    try:
        res = urequests.get(GET_COMMAND_URL)
        res.close()
        print("Server reachable")
        return True
    except Exception as e:
        print("Server check failed:", e)
        return False


def ensure_connection():
    """
    Make sure Wi-Fi is connected and server is reachable.
    If initial server check fails, retry Wi-Fi connection once.
    """
    wlan = get_wlan()

    if not wlan.isconnected():
        if not connect_wifi():
            return False

    if server_check():
        return True

    print("Initial REST check failed, retrying connection...")
    if not reconnect_wifi():
        return False

    return server_check()


def send_data():
    payload = hw.state_dict()

    if not ensure_connection():
        print("Skipping send_data: no connection")
        return

    try:
        res = urequests.post(POST_DATA_URL, json=payload)
        res.close()
    except Exception as e:
        print("POST failed:", e)


def handle_command(cmd):
    cmd_type = cmd.get("type")
    params = cmd.get("params", {})

    if cmd_type == "LED_TOGGLE":
        hw.led.toggle()

    elif cmd_type == "WATER_ON":
        hw.pump.on()

    elif cmd_type == "WATER_OFF":
        hw.pump.off()

    elif cmd_type == "PUMP_TOGGLE":
        hw.pump.toggle()

    elif cmd_type == "DISPENSE":
        print(params)
        # add dispense mechanism

    elif cmd_type == "PING":
        print("Received ping")

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
    connect_wifi()

    while True:
        check_command()
        send_data()
        time.sleep(1)


main()