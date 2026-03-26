from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

latest_data = {"led": None, "pump": None, "weight": 30}
pending_command = None

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/data")
async def receive_data(data: dict):
    global latest_data
    # Expected from Pico: {"knob": 12345, "led": 0}
    latest_data = data
    return {"status": "ok"}


@app.get("/api/state")
async def get_state():
    print(latest_data)
    return latest_data


@app.post("/api/command")
async def queue_command(cmd: dict):
    global pending_command
    # Example: {"type": "LED_TOGGLE"}
    pending_command = cmd
    print(cmd)
    return {"status": "queued"}


@app.get("/api/command")
async def get_command():
    global pending_command
    cmd = pending_command
    pending_command = None
    return cmd if cmd else {}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)