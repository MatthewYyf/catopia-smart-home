import network
import time
import urequests
import config
from hardware import Hardware

POST_DATA_URL = "http://{}:8000/api/data".format(config.PI_IP)
GET_COMMAND_URL = "http://{}:8000/api/command".format(config.PI_IP)

hw = Hardware()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.SSID, config.PASSWORD)

    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        print("Waiting...")
        time.sleep(1)

    print("Connected:", wlan.ifconfig())


def send_data():
    payload = hw.state_dict()
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

    elif cmd_type == "DISPENSE":
        print(params)
        # add dispense mechanism

    elif cmd_type == "PING":
        print("Received ping")

    else:
        print("Unknown command:", cmd_type)


def check_command():
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