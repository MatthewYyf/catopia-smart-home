# catopia-smart-home

Simple starter project for a smart-home style dashboard and device API.

## What this project does

- Serves a static frontend from `backend/static/index.html`
- Receives sensor/device data
- Exposes current state to the frontend
- Queues commands for a connected device (for example, a Pico)

## Tech stack

- Python
- FastAPI
- Uvicorn

## Quick start

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install fastapi uvicorn
```

3. Start the server:

```bash
python backend/server.py
```

4. Open the app:

- http://localhost:8000

## API endpoints

- `GET /` -> serves the frontend page
- `POST /api/data` -> receives latest device data
- `GET /api/state` -> returns latest known state
- `POST /api/command` -> queues a command
- `GET /api/command` -> fetches and clears queued command

## Example payloads

`POST /api/data`

```json
{
  "led": 0,
  "pump": 1,
  "weight": 30
}
```

`POST /api/command`

```json
{
  "type": "LED_TOGGLE"
}
```