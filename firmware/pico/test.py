import sys
import json
import time
from machine import Pin


# tests LED connection to backend
led = machine.Pin(16, machine.Pin.OUT)

def send(data):
    print(json.dumps(data))

while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        if line:
            try:
                cmd = json.loads(line)

                # cmd type
                if cmd["type"] == "TURN_ON_LIGHT":
                    
                    send({"id": cmd["id"], "status": "ACCEPTED"})
                    
                    led.value(1)
                    time.sleep(2)
                    led.value(0)

                    send({"id": cmd["id"], "status": "COMPLETED"})
                except:
                    pass

        # send sensor update
        # TBI