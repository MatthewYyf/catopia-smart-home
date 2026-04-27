from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from db.queries import addReport, addVoice_log, getReportbyDate, getVoice_log, init_db

app = FastAPI()
init_db()  # Ensure the database is initialized at startup
latest_data = {"led": None, "pump": None, "weight": 30}
pending_command = None


class ReportPayload(BaseModel):
    report_date: str
    water_intake: float = Field(ge=0)
    food_intake: float = Field(ge=0)
    weight: float = Field(gt=0)
    short_message: str = Field(default="", max_length=255)


class VoiceTagPayload(BaseModel):
    timestamp: str = Field(min_length=1, max_length=64)
    voice_type: str = Field(min_length=1, max_length=80)


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
    global pending_command
    cmd = pending_command
    pending_command = None
    return cmd if cmd else {}


@app.post("/api/reports")
async def create_report(report: ReportPayload):
    try:
        addReport(
            report.report_date,
            report.water_intake,
            report.food_intake,
            report.weight,
            report.short_message,
        )
        saved_report = getReportbyDate(report.report_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "saved",
        "report": asdict(saved_report) if saved_report else None,
    }


@app.get("/api/reports/{report_date}")
async def read_report(report_date: str):
    report = getReportbyDate(report_date)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report": asdict(report)}


@app.post("/api/reports/{report_date}/voice-tags")
async def create_voice_tag(report_date: str, tag: VoiceTagPayload):
    voice_type = tag.voice_type.strip()
    if not voice_type:
        raise HTTPException(status_code=400, detail="Voice tag cannot be empty")

    try:
        addVoice_log(report_date, tag.timestamp, voice_type)
        report = getReportbyDate(report_date)
        voice_tags = getVoice_log(report_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "saved",
        "report": asdict(report) if report else None,
        "voice_tags": voice_tags,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
