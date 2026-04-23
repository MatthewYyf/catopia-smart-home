import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DB_PATH = Path(__file__).with_name("catopia.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


@dataclass
class report:
    report_date: str
    water_intake: float
    food_intake: float
    weight: float
    short_message: str
    voice_tags: dict[str, str]


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def init_db() -> None:
    with _get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())

def getVoice_log(report_date: str) -> dict[str,str]:
    output = {}
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                report_date,
                timestamp,
                voice_type,
            FROM voice_logs
            WHERE report_date = ?
            ORDER BY timestamp DESC
            """,
            (report_date,),
        ).fetchall()
    for row in rows:
        output[row["report_date"], row["timestamp"]] = row["voice_type"]
    return output


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


def addReport (
    report_date: str,
    water_intake: float,
    food_intake: float,
    weight: float,
    short_message: str = "",
) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO daily_reports (
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
            INSERT INTO voice_logs (
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
