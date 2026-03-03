import json
import threading
import serial
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- SERIAL SETUP ---
# run ls /dev/tty.*
# and replace with pico serial device
ser = serial.Serial("SERIAL_DEVICE", 115200, timeout=1)

latest_state = {}
websocket_clients = []

# -- STATIC FILE --
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

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
@app.post("/api/command")
async def send_command(cmd: dict):
    ser.write((json.dumps(cmd) + "\n").encode())
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