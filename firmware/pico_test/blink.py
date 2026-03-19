import sys
import json
import time
from machine import Pin, ADC, PWM

# tests LED connection to backend
# led = Pin(16, Pin.OUT)
led = PWM(Pin(18))

# test knob connection
knob = ADC(0)

def send(data):
    print(json.dumps(data))

def check_stdin():
    """Return a line from stdin if available, else None."""
    import select
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None

try:
    import select
    use_select = True
except ImportError:
    use_select = False

while True:
    line = None
    if use_select:
        line = check_stdin()
    else:
        # If select not available, fallback to blocking read (not ideal)
        # or skip reading from sys.stdin
        pass

    if line:
        try:
            cmd = json.loads(line)

            # cmd type
            if cmd["type"] == "LED_TOGGLE":
                send({"id": cmd["id"], "status": "ACCEPTED"})
                
                led.value(1)
                time.sleep(2)
                led.value(0)

                send({"id": cmd["id"], "status": "COMPLETED"})
        except:
            pass

    # send sensor update
    send({
        "sensor": {"knob": knob.read_u16()}
    })

    time.sleep(1)