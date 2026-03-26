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