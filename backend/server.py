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


@app.post("/api/data")
async def receive_data(data: dict):
    global latest_data
    # Expected from Pico: {"knob": 12345, "led": 0}
    latest_data = data
    return {"status": "ok"}

@app.get("/api/state")
async def get_state():
    # print(latest_data)
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
