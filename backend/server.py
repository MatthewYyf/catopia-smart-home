from collections import defaultdict, deque
from dataclasses import asdict
from datetime import date, timedelta
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from db.queries import (
    addReport,
    addVoice_log,
    getConsumptionEvents,
    getDailyConsumptionTotals,
    getLatestVoice_log,
    getReportbyDate,
    getVoice_log,
    getWaterIntakeByDateRange,
    init_db,
)
from services.consumption_tracker import ConsumptionTrackerService

app = FastAPI()
init_db()  # Ensure the database is initialized at startup

DEFAULT_DEVICE_ID = "001"
ALLOWED_VOICE_TYPES = {"food", "brushing", "isolation"}

# Latest telemetry/state per device_id (Pico POSTs here)
latest_data_by_device: dict[str, dict[str, Any]] = defaultdict(
    lambda: {"led": None, "pump": None, "weight": 30}
)

# FIFO command queue per device_id (browser POSTs, Pico GETs next)
command_queues_by_device: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
consumption_service = ConsumptionTrackerService()

class ReportPayload(BaseModel):
    report_date: str
    water_intake: float = Field(ge=0)
    food_intake: float = Field(ge=0)
    weight: float = Field(gt=0)
    short_message: str = Field(default="", max_length=255)


class VoiceTagPayload(BaseModel):
    timestamp: str = Field(min_length=1, max_length=64)
    voice_type: str = Field(min_length=1, max_length=80)


class LatestVoicePayload(BaseModel):
    timestamp: str = Field(min_length=1, max_length=64)
    voice_type: str = Field(min_length=1, max_length=80)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/devices/{device_id}/telemetry")
async def receive_device_telemetry(device_id: str, data: dict):
    # Expected from Pico: {"load": 12345, "led": 0, ...}
    events = consumption_service.process_readings(data)
    latest_data_by_device[device_id] = consumption_service.normalize_state_payload(data)
    return {
        "status": "ok",
        "device_id": device_id,
        "events_recorded": len(events),
        "events": events,
    }


@app.get("/api/devices/{device_id}/state")
async def get_device_state(device_id: str):
    latest_data_by_device[device_id]["consumption"] = consumption_service.state()
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
    events = consumption_service.process_readings(data)
    latest_data_by_device[device_id] = consumption_service.normalize_state_payload(data)
    return {
        "status": "ok",
        "device_id": device_id,
        "events_recorded": len(events),
        "events": events,
    }

@app.get("/api/state")
async def get_state():
    # Backwards-compatible: return the default device's latest state
    latest_data_by_device[DEFAULT_DEVICE_ID]["consumption"] = consumption_service.state()
    return latest_data_by_device[DEFAULT_DEVICE_ID]


@app.get("/api/consumption/events")
async def read_consumption_events(report_date: Optional[str] = None):
    events = getConsumptionEvents(report_date)
    return {"events": [asdict(event) for event in events]}


@app.get("/api/consumption/daily/{report_date}")
async def read_daily_consumption(report_date: str):
    events = getConsumptionEvents(report_date)
    return {
        "report_date": report_date,
        "totals": getDailyConsumptionTotals(report_date),
        "events": [asdict(event) for event in events],
    }


@app.post("/api/consumption/reset")
async def reset_consumption(sensor_type: str = "food", clear_baseline: bool = False):
    if not consumption_service.reset_session(sensor_type, clear_baseline=clear_baseline):
        raise HTTPException(status_code=404, detail="Unknown sensor type")

    return {
        "status": "reset",
        "sensor_type": sensor_type,
        "clear_baseline": clear_baseline,
        "consumption": consumption_service.state(),
    }


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


@app.get("/api/reports/water-intake/last-7-days")
async def read_water_intake_last_7_days():
    today = date.today()
    start_date = today - timedelta(days=6)
    rows = getWaterIntakeByDateRange(start_date.isoformat(), today.isoformat())
    intake_by_date = {
        row["report_date"]: row["water_intake"]
        for row in rows
    }

    points = []
    for offset in range(7):
        current_date = start_date + timedelta(days=offset)
        date_key = current_date.isoformat()
        points.append(
            {
                "date": date_key,
                "label": current_date.strftime("%a").upper(),
                "water_intake": intake_by_date.get(date_key, 0),
            }
        )

    return {"points": points}


@app.get("/api/reports/{report_date}")
async def read_report(report_date: str):
    report = getReportbyDate(report_date)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report": asdict(report)}


@app.post("/api/reports/{report_date}/voice-tags")
async def create_voice_tag(report_date: str, tag: VoiceTagPayload):
    voice_type = tag.voice_type.strip().lower()
    if voice_type not in ALLOWED_VOICE_TYPES:
        raise HTTPException(status_code=400, detail="Voice tag must be food, brushing, or isolation")

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


@app.post("/api/emotion/latest")
async def update_latest_emotion(tag: LatestVoicePayload):
    voice_type = tag.voice_type.strip().lower()
    if voice_type not in ALLOWED_VOICE_TYPES:
        raise HTTPException(status_code=400, detail="Voice tag must be food, brushing, or isolation")

    try:
        report_date = tag.timestamp[:10]
        addVoice_log(report_date, tag.timestamp, voice_type)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "saved",
        "latest": {
            "timestamp": tag.timestamp,
            "voice_type": voice_type,
        },
    }


@app.get("/api/emotion/latest")
async def read_latest_emotion():
    latest = getLatestVoice_log()
    return {
        "latest": latest or {
            "timestamp": None,
            "voice_type": None,
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
