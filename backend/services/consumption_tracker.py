from collections import deque
from datetime import datetime
from statistics import median
from threading import Lock

from db.queries import addConsumptionEvent, getDailyConsumptionTotals


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


class ConsumptionTrackerService:
    sensor_keys = {
        "food": ("food_weight", "food_load", "food_level"),
        "water": ("water_weight", "water_load", "water_level"),
    }
    generic_weight_keys = ("load", "weight")

    def __init__(self):
        self.lock = Lock()
        self.trackers = {
            "food": StableConsumptionTracker(
                "food",
                "g",
                tolerance=3,
                min_drop=2,
                max_drop=80,
            ),
            "water": StableConsumptionTracker(
                "water",
                "ml",
                stable_window=7,
                tolerance=5,
                min_drop=3,
                max_drop=200,
            ),
        }

    def process_readings(self, data):
        timestamp = self._local_timestamp()
        readings = self.extract_readings(data)
        events = []

        with self.lock:
            for sensor_type, value in readings.items():
                event = self.trackers[sensor_type].add_reading(value, timestamp)
                if event:
                    addConsumptionEvent(**event)
                    events.append(event)

        return events

    def state(self):
        report_date = self._local_date()
        totals = getDailyConsumptionTotals(report_date)

        with self.lock:
            sensors = {
                sensor_type: tracker.state_dict()
                for sensor_type, tracker in self.trackers.items()
            }

        for sensor_type, sensor_state in sensors.items():
            sensor_state["today_total"] = totals.get(sensor_type, 0)

        return {
            "date": report_date,
            "sensors": sensors,
        }

    def normalize_state_payload(self, data):
        state = dict(data)
        display_weight = self.first_numeric(
            data,
            self.generic_weight_keys + self.sensor_keys["food"],
        )
        if display_weight is not None:
            state["weight"] = display_weight
        state["consumption"] = self.state()
        return state

    def reset_session(self, sensor_type):
        tracker = self.trackers.get(sensor_type)
        if tracker is None:
            return False

        with self.lock:
            tracker.reset_session()

        return True

    def extract_readings(self, data):
        readings = {}

        for sensor_type, keys in self.sensor_keys.items():
            value = self.first_numeric(data, keys)
            if value is not None:
                readings[sensor_type] = value

        if not readings:
            generic_value = self.first_numeric(data, self.generic_weight_keys)
            if generic_value is not None:
                readings["food"] = generic_value

        return readings

    def first_numeric(self, data, keys):
        for key in keys:
            value = self.coerce_number(data.get(key))
            if value is not None:
                return value

        sensor_data = data.get("sensor")
        if isinstance(sensor_data, dict):
            for key in keys:
                value = self.coerce_number(sensor_data.get(key))
                if value is not None:
                    return value

        return None

    @staticmethod
    def coerce_number(value):
        if isinstance(value, bool):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _local_timestamp():
        return datetime.now().replace(microsecond=0).isoformat(sep=" ")

    @staticmethod
    def _local_date():
        return datetime.now().date().isoformat()
