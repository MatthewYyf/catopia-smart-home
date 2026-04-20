from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
from datetime import datetime
from pathlib import Path

app = FastAPI()
latest_data = {"led": None, "pump": None, "weight": 30}
pending_command = None

# ── Voice Memo Storage ──
MEMOS_DIR = Path("voice_memos")
MEMOS_DIR.mkdir(exist_ok=True)
MEMOS_META = MEMOS_DIR / "metadata.json"

def load_meta() -> list:
    if MEMOS_META.exists():
        with open(MEMOS_META) as f:
            return json.load(f)
    return []

def save_meta(data: list):
    with open(MEMOS_META, "w") as f:
        json.dump(data, f, indent=2)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/voice_memos", StaticFiles(directory="voice_memos"), name="voice_memos")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# ── Hardware API ──
@app.post("/api/data")
async def receive_data(data: dict):
    global latest_data
    latest_data = data
    return {"status": "ok"}

@app.get("/api/state")
async def get_state():
    return latest_data

@app.post("/api/command")
async def queue_command(cmd: dict):
    global pending_command
    pending_command = cmd
    print(cmd)
    return {"status": "queued"}

@app.get("/api/command")
async def get_command():
    global pending_command
    cmd = pending_command
    pending_command = None
    return cmd if cmd else {}

# ── Voice Memo API ──
@app.get("/api/memos")
async def list_memos():
    return load_meta()

@app.post("/api/memos")
async def upload_memo(
    file: UploadFile = File(...),
    label: str = "Voice Memo"
):
    # Generate unique filename
    ts = datetime.now()
    filename = f"memo_{ts.strftime('%Y%m%d_%H%M%S')}.webm"
    filepath = MEMOS_DIR / filename

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    meta = load_meta()
    entry = {
        "id": filename,
        "label": label,
        "filename": filename,
        "url": f"/voice_memos/{filename}",
        "created_at": ts.isoformat(),
        "size_bytes": len(contents)
    }
    meta.insert(0, entry)  # newest first
    save_meta(meta)

    return entry

@app.delete("/api/memos/{memo_id}")
async def delete_memo(memo_id: str):
    meta = load_meta()
    entry = next((m for m in meta if m["id"] == memo_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Memo not found")

    filepath = MEMOS_DIR / entry["filename"]
    if filepath.exists():
        filepath.unlink()

    meta = [m for m in meta if m["id"] != memo_id]
    save_meta(meta)
    return {"status": "deleted"}

@app.patch("/api/memos/{memo_id}")
async def rename_memo(memo_id: str, body: dict):
    meta = load_meta()
    for entry in meta:
        if entry["id"] == memo_id:
            entry["label"] = body.get("label", entry["label"])
            save_meta(meta)
            return entry
    raise HTTPException(status_code=404, detail="Memo not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
