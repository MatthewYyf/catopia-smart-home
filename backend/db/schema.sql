CREATE TABLE IF NOT EXISTS daily_reports (
    report_date DATE PRIMARY KEY,
    water_intake REAL NOT NULL,
    food_intake REAL NOT NULL,
    weight REAL NOT NULL,
    short_message VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS voice_logs (
    report_date DATE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    voice_type TEXT NOT NULL,
    PRIMARY KEY (report_date, timestamp)
);

CREATE TABLE IF NOT EXISTS consumption_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_type TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    before_value REAL NOT NULL,
    after_value REAL NOT NULL,
    consumed_amount REAL NOT NULL,
    unit TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_consumption_events_end_time
ON consumption_events(end_time);

CREATE INDEX IF NOT EXISTS idx_consumption_events_sensor_type
ON consumption_events(sensor_type);
