# Catopia Smart Home System

Embedded systems project for a smart-home style dashboard and device API.

## Quick start

1. Create and activate a virtual environment (choose one method):

**Using venv:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Using conda:**
```bash
conda create -n catopia python=3.10
conda activate catopia
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
cd backend
python server.py
```

4. Open the app:

- http://localhost:8000

## API endpoints

- `GET /` -> serves the frontend page
- `POST /api/data` -> receives latest device data
- `GET /api/state` -> returns latest known state
- `GET /api/consumption/events` -> returns recorded food/water consumption events
- `GET /api/consumption/events?report_date=YYYY-MM-DD` -> returns events for one day
- `GET /api/consumption/daily/YYYY-MM-DD` -> returns daily consumption totals and events
- `POST /api/command` -> queues a command
- `GET /api/command` -> fetches and clears queued command

## Example payloads

`POST /api/data`

```json
{
  "led": 0,
  "pump": 1,
  "load": 30
}
```

For two bowl sensors, send explicit keys:

```json
{
  "food_weight": 120,
  "water_weight": 300
}
```

The server keeps recent raw readings in memory for filtering. SQLite only stores confirmed consumption events after readings settle to a new stable lower value.

`POST /api/command`

```json
{
  "type": "LED_TOGGLE"
}
```
