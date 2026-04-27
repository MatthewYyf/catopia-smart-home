from collections import defaultdict, deque
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

DEFAULT_DEVICE_ID = "pico_default"

# Latest telemetry/state per device_id
latest_data_by_device: dict[str, dict[str, Any]] = defaultdict(
    lambda: {"led": None, "pump": None, "weight": 30}
)

# FIFO command queue per device_id
command_queues_by_device: dict[str, deque[dict[str, Any]]] = defaultdict(deque)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/devices/{device_id}/telemetry")
async def receive_device_telemetry(device_id: str, data: dict):
    # Expected from Pico: {"knob": 12345, "led": 0, ...}
    latest_data_by_device[device_id] = data
    return {"status": "ok", "device_id": device_id}


@app.get("/api/devices/{device_id}/state")
async def get_device_state(device_id: str):
    return latest_data_by_device[device_id]


@app.post("/api/devices/{device_id}/commands")
async def queue_device_command(device_id: str, cmd: dict):
    # Example: {"type": "LED_TOGGLE", "params": {...}}
    command_queues_by_device[device_id].append(cmd)
    print({"device_id": device_id, "queued_command": cmd})
    return {"status": "queued", "device_id": device_id, "queue_depth": len(command_queues_by_device[device_id])}


@app.get("/api/devices/{device_id}/commands/next")
async def get_next_device_command(device_id: str):
    q = command_queues_by_device[device_id]
    if not q:
        return {}
    return q.popleft()


@app.post("/api/data")
async def receive_data(data: dict):
    """
    Backwards-compatible endpoint.

    If the payload includes "device_id", it will be used; otherwise we use a
    shared default device_id so older firmware keeps working.
    """
    device_id = str(data.get("device_id") or DEFAULT_DEVICE_ID)
    latest_data_by_device[device_id] = data
    return {"status": "ok", "device_id": device_id}

@app.get("/api/state")
async def get_state():
    # Backwards-compatible: return the default device's latest state
    return latest_data_by_device[DEFAULT_DEVICE_ID]


@app.post("/api/command")
async def queue_command(cmd: dict):
    # Backwards-compatible: queue for the default device
    command_queues_by_device[DEFAULT_DEVICE_ID].append(cmd)
    print({"device_id": DEFAULT_DEVICE_ID, "queued_command": cmd})
    return {"status": "queued", "device_id": DEFAULT_DEVICE_ID, "queue_depth": len(command_queues_by_device[DEFAULT_DEVICE_ID])}


@app.get("/api/command")
async def get_command():
    # Backwards-compatible: pop from the default device's queue
    q = command_queues_by_device[DEFAULT_DEVICE_ID]
    if not q:
        return {}
    return q.popleft()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)