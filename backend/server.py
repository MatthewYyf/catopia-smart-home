from dataclasses import asdict
from typing import Optional

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
    getReportbyDate,
    getVoice_log,
    init_db,
)
from services.consumption_tracker import ConsumptionTrackerService

app = FastAPI()
init_db()  # Ensure the database is initialized at startup
latest_data = {"led": None, "pump": None, "weight": 30}
pending_command = None
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


ALLOWED_VOICE_TAGS = {"brushing", "food", "isolation"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/data")
async def receive_data(data: dict):
    global latest_data
    # Expected from Pico: {"load": 12345, "led": 0}. Also supports food/water-specific keys.
    events = consumption_service.process_readings(data)
    latest_data = consumption_service.normalize_state_payload(data)
    return {
        "status": "ok",
        "events_recorded": len(events),
    }

@app.get("/api/state")
async def get_state():
    latest_data["consumption"] = consumption_service.state()
    return latest_data


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
async def reset_consumption(sensor_type: str = "food"):
    if not consumption_service.reset_session(sensor_type):
        raise HTTPException(status_code=404, detail="Unknown sensor type")

    return {
        "status": "reset",
        "sensor_type": sensor_type,
        "consumption": consumption_service.state(),
    }


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
    voice_type = tag.voice_type.strip().lower()
    if voice_type not in ALLOWED_VOICE_TAGS:
        raise HTTPException(
            status_code=400,
            detail="Voice tag must be one of: brushing, food, isolation",
        )

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

@app.get("/api/reports/{report_date}/voice-tags")
async def get_emotion_chart(report_date:str):
    voice_tags = getVoice_log(report_date)
    if voice_tags is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"voice_tags": voice_tags}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
