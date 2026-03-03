import os
import json
import threading
import serial
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

app = FastAPI()

# --- SERIAL SETUP ---
# run ls /dev/tty.*
# and replace with pico serial device
ser = serial.Serial("/dev/tty.wlan-debug", 115200, timeout=1)

latest_state = {}
websocket_clients = []

# -- STATIC FILE --
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# --- SERIAL READER THREAD ---
def serial_reader():
    global latest_state
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                data = json.loads(line)
                latest_state = data
                # Broadcast to all websocket clients
                for ws in websocket_clients:
                    try:
                        ws.send_json(data)
                    except:
                        pass
        except:
            pass

threading.Thread(target=serial_reader, daemon=True).start()

# --- REST ENDPOINT ---
from schemas import Command

@app.post("/api/command")
async def send_command(cmd: Command):
    ser.write((cmd.model_dump_json() + "\n").encode())
    return {"status": "sent"}

@app.get("/api/state")
async def get_state():
    return latest_state

# --- WEBSOCKET FOR LIVE DATA ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    websocket_clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # Keep alive
    except:
        websocket_clients.remove(ws)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)