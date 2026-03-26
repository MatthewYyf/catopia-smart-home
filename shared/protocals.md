# Catopia Serial Protocol v1

All messages are newline-delimited JSON.

## Command (Backend → Pico)

{
  "id": string,
  "type": string,
  "params": object (optional)
}

### Command Types
- LED_TOGGLE
- DISPENSE

---

## Acknowledgement (Pico → Backend)

{
  "id": string,
  "status": "ACCEPTED" | "COMPLETED" | "ERROR",
  "error": string (optional)
}

---

## Telemetry (Pico → Backend)

{
  "sensor": {
    "knob": number,
    "weight": number
  },
  "state": {
    "motor": 0 | 1
  }
}