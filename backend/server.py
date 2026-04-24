from collections import deque
from dataclasses import asdict
from datetime import datetime
from statistics import median
from threading import Lock
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from db.queries import (
    addConsumptionEvent,
    addReport,
    addVoice_log,
    getConsumptionEvents,
    getDailyConsumptionTotals,
    getReportbyDate,
    getVoice_log,
    init_db,
)

app = FastAPI()
init_db()  # Ensure the database is initialized at startup
latest_data = {"led": None, "pump": None, "weight": 30}
pending_command = None
tracker_lock = Lock()


class StableConsumptionTracker:
    def __init__(
        self,
        sensor_type,
        unit,
        stable_window=5,
        median_window=5,
        tolerance=3,
        min_drop=2,
        max_drop=80,
        memory_size=300,
    ):
        self.sensor_type = sensor_type
        self.unit = unit
        self.stable_window = stable_window
        self.median_window = median_window
        self.tolerance = tolerance
        self.min_drop = min_drop
        self.max_drop = max_drop
        self.raw_readings = deque(maxlen=memory_size)
        self.filtered_readings = deque(maxlen=memory_size)
        self.last_stable_value = None
        self.last_stable_time = None
        self.latest_raw = None
        self.latest_filtered = None
        self.latest_is_stable = False
        self.latest_stable_value = None
        self.last_event = None
        self.session_total = 0

    def add_reading(self, value, timestamp):
        self.latest_raw = value
        self.raw_readings.append(value)

        recent_raw = list(self.raw_readings)[-self.median_window:]
        filtered = median(recent_raw)
        self.latest_filtered = filtered
        self.filtered_readings.append(filtered)

        if len(self.filtered_readings) < self.stable_window:
            self.latest_is_stable = False
            return None

        recent_filtered = list(self.filtered_readings)[-self.stable_window:]
        self.latest_is_stable = max(recent_filtered) - min(recent_filtered) <= self.tolerance

        if not self.latest_is_stable:
            return None

        current_stable = median(recent_filtered)
        self.latest_stable_value = current_stable

        if self.last_stable_value is None:
            self.last_stable_value = current_stable
            self.last_stable_time = timestamp
            return None

        drop = self.last_stable_value - current_stable

        if self.min_drop <= drop <= self.max_drop:
            event = {
                "sensor_type": self.sensor_type,
                "start_time": self.last_stable_time or timestamp,
                "end_time": timestamp,
                "before_value": self.last_stable_value,
                "after_value": current_stable,
                "consumed_amount": drop,
                "unit": self.unit,
            }
            self.last_stable_value = current_stable
            self.last_stable_time = timestamp
            self.last_event = event
            self.session_total += drop
            return event

        # A stable increase is a refill/reset, not consumption.
        if current_stable > self.last_stable_value + self.tolerance:
            self.last_stable_value = current_stable
            self.last_stable_time = timestamp

        return None

    def reset_session(self):
        self.session_total = 0
        self.last_event = None

    def state_dict(self):
        return {
            "latest_raw": self.latest_raw,
            "filtered_value": self.latest_filtered,
            "is_stable": self.latest_is_stable,
            "stable_value": self.latest_stable_value,
            "baseline_value": self.last_stable_value,
            "recent_sample_count": len(self.raw_readings),
            "last_event": self.last_event,
            "session_total": self.session_total,
            "unit": self.unit,
        }


consumption_trackers = {
    "food": StableConsumptionTracker("food", "g", tolerance=3, min_drop=2, max_drop=80),
    "water": StableConsumptionTracker(
        "water",
        "ml",
        stable_window=7,
        tolerance=5,
        min_drop=3,
        max_drop=200,
    ),
}


SENSOR_KEYS = {
    "food": ("food_weight", "food_load", "food_level"),
    "water": ("water_weight", "water_load", "water_level"),
}
GENERIC_WEIGHT_KEYS = ("load", "weight")


class ReportPayload(BaseModel):
    report_date: str
    water_intake: float = Field(ge=0)
    food_intake: float = Field(ge=0)
    weight: float = Field(gt=0)
    short_message: str = Field(default="", max_length=255)


class VoiceTagPayload(BaseModel):
    timestamp: str = Field(min_length=1, max_length=64)
    voice_type: str = Field(min_length=1, max_length=80)


def _local_timestamp():
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _local_date():
    return datetime.now().date().isoformat()


def _coerce_number(value):
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_numeric(data, keys):
    for key in keys:
        value = _coerce_number(data.get(key))
        if value is not None:
            return value

    sensor_data = data.get("sensor")
    if isinstance(sensor_data, dict):
        for key in keys:
            value = _coerce_number(sensor_data.get(key))
            if value is not None:
                return value

    return None


def _extract_consumption_readings(data):
    readings = {}

    for sensor_type, keys in SENSOR_KEYS.items():
        value = _first_numeric(data, keys)
        if value is not None:
            readings[sensor_type] = value

    if not readings:
        generic_value = _first_numeric(data, GENERIC_WEIGHT_KEYS)
        if generic_value is not None:
            readings["food"] = generic_value

    return readings


def _process_consumption_readings(data):
    timestamp = _local_timestamp()
    readings = _extract_consumption_readings(data)
    events = []

    with tracker_lock:
        for sensor_type, value in readings.items():
            event = consumption_trackers[sensor_type].add_reading(value, timestamp)
            if event:
                addConsumptionEvent(**event)
                events.append(event)

    return events


def _consumption_state():
    report_date = _local_date()
    totals = getDailyConsumptionTotals(report_date)

    with tracker_lock:
        sensors = {
            sensor_type: tracker.state_dict()
            for sensor_type, tracker in consumption_trackers.items()
        }

    for sensor_type, sensor_state in sensors.items():
        sensor_state["today_total"] = totals.get(sensor_type, 0)

    return {
        "date": report_date,
        "sensors": sensors,
    }


def _normalize_state_payload(data):
    state = dict(data)
    display_weight = _first_numeric(data, GENERIC_WEIGHT_KEYS + SENSOR_KEYS["food"])
    if display_weight is not None:
        state["weight"] = display_weight
    state["consumption"] = _consumption_state()
    return state


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/data")
async def receive_data(data: dict):
    global latest_data
    # Expected from Pico: {"load": 12345, "led": 0}. Also supports food/water-specific keys.
    events = _process_consumption_readings(data)
    latest_data = _normalize_state_payload(data)
    return {
        "status": "ok",
        "events_recorded": len(events),
    }

@app.get("/api/state")
async def get_state():
    latest_data["consumption"] = _consumption_state()
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
    tracker = consumption_trackers.get(sensor_type)
    if tracker is None:
        raise HTTPException(status_code=404, detail="Unknown sensor type")

    with tracker_lock:
        tracker.reset_session()

    return {
        "status": "reset",
        "sensor_type": sensor_type,
        "consumption": _consumption_state(),
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

@app.get("/api/reports/{report_date}/voice-tags")
async def get_emotion_chart(report_date:str):
    voice_tags = getVoice_log(report_date)
    if voice_tags is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"voice_tags": voice_tags}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
