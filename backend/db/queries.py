import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


DB_PATH = Path(__file__).with_name("catopia.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


@dataclass
class report:
    report_date: str
    water_intake: float
    food_intake: float
    weight: float
    short_message: str
    voice_tags: List[Dict[str, str]]


@dataclass
class ConsumptionEvent:
    id: int
    sensor_type: str
    start_time: str
    end_time: str
    before_value: float
    after_value: float
    consumed_amount: float
    unit: str


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def init_db() -> None:
    with _get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())


def getVoice_log(report_date: str) -> List[Dict[str, str]]:
    with _get_connection() as conn:
        rows = conn.execute(
            """
            WITH normalized_logs AS (
                SELECT
                    substr(timestamp, 1, 13) AS hour_key,
                    lower(trim(voice_type)) AS voice_type,
                    timestamp
                FROM voice_logs
                WHERE report_date = ?
                    AND lower(trim(voice_type)) IN ('food', 'brushing', 'isolation')
                    AND CAST(substr(timestamp, 12, 2) AS INTEGER) BETWEEN 8 AND 20
            ),
            hourly_counts AS (
                SELECT
                    hour_key,
                    voice_type,
                    COUNT(*) AS tag_count,
                    MAX(timestamp) AS latest_timestamp
                FROM normalized_logs
                GROUP BY hour_key, voice_type
            ),
            ranked AS (
                SELECT
                    hour_key,
                    voice_type,
                    ROW_NUMBER() OVER (
                        PARTITION BY hour_key
                        ORDER BY tag_count DESC, latest_timestamp DESC, voice_type ASC
                    ) AS rank
                FROM hourly_counts
            )
            SELECT
                hour_key || ':00' AS timestamp,
                voice_type
            FROM ranked
            WHERE rank = 1
            ORDER BY timestamp ASC
            """,
            (report_date,),
        ).fetchall()

    return [
        {
            "timestamp": row["timestamp"],
            "voice_type": row["voice_type"],
        }
        for row in rows
    ]


def getLatestVoice_log() -> Optional[Dict[str, str]]:
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                timestamp,
                lower(trim(voice_type)) AS voice_type
            FROM voice_logs
            WHERE lower(trim(voice_type)) IN ('food', 'brushing', 'isolation')
            ORDER BY timestamp DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return None

    return {
        "timestamp": row["timestamp"],
        "voice_type": row["voice_type"],
    }


def getReportbyDate(report_date: str) -> Optional[report]:
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                report_date,
                water_intake,
                food_intake,
                weight,
                short_message
            FROM daily_reports
            WHERE report_date = ?
            """,
            (report_date,),
        ).fetchone()

    if row is None:
        return None
    voice_log = getVoice_log(report_date)
    return report(
        report_date=row["report_date"],
        water_intake=row["water_intake"],
        food_intake=row["food_intake"],
        weight=row["weight"],
        short_message=row["short_message"],
        voice_tags=voice_log
    )


def addReport(
    report_date: str,
    water_intake: float,
    food_intake: float,
    weight: float,
    short_message: str = "",
) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO daily_reports (
                report_date,
                water_intake,
                food_intake,
                weight,
                short_message
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                report_date,
                water_intake,
                food_intake,
                weight,
                short_message,
            ),
        )


def addVoice_log(report_date: str, timestamp: str, voice_type: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO voice_logs (
                report_date,
                timestamp,
                voice_type
            )
            VALUES (?, ?, ?)
            """,
            (
                report_date,
                timestamp,
                voice_type,
            ),
        )


def getWaterIntakeByDateRange(start_date: str, end_date: str) -> List[Dict[str, float]]:
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                report_date,
                water_intake
            FROM daily_reports
            WHERE date(report_date) BETWEEN date(?) AND date(?)
            ORDER BY report_date ASC
            """,
            (start_date, end_date),
        ).fetchall()

    return [
        {
            "report_date": row["report_date"],
            "water_intake": row["water_intake"],
        }
        for row in rows
    ]


def addConsumptionEvent(
    sensor_type: str,
    start_time: str,
    end_time: str,
    before_value: float,
    after_value: float,
    consumed_amount: float,
    unit: str,
) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO consumption_events (
                sensor_type,
                start_time,
                end_time,
                before_value,
                after_value,
                consumed_amount,
                unit
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sensor_type,
                start_time,
                end_time,
                before_value,
                after_value,
                consumed_amount,
                unit,
            ),
        )


def getConsumptionEvents(report_date: Optional[str] = None) -> List[ConsumptionEvent]:
    query = """
        SELECT
            id,
            sensor_type,
            start_time,
            end_time,
            before_value,
            after_value,
            consumed_amount,
            unit
        FROM consumption_events
    """
    params = ()

    if report_date:
        query += " WHERE date(end_time) = date(?)"
        params = (report_date,)

    query += " ORDER BY end_time ASC"

    with _get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        ConsumptionEvent(
            id=row["id"],
            sensor_type=row["sensor_type"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            before_value=row["before_value"],
            after_value=row["after_value"],
            consumed_amount=row["consumed_amount"],
            unit=row["unit"],
        )
        for row in rows
    ]


def getDailyConsumptionTotals(report_date: str) -> Dict[str, float]:
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                sensor_type,
                SUM(consumed_amount) AS total
            FROM consumption_events
            WHERE date(end_time) = date(?)
            GROUP BY sensor_type
            """,
            (report_date,),
        ).fetchall()

    return {row["sensor_type"]: row["total"] or 0 for row in rows}
