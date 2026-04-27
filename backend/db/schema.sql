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

