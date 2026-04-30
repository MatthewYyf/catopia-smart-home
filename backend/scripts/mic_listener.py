import json
import os
import sys
import time
from datetime import datetime

import numpy as np
import requests
import sounddevice as sd

# Allow imports from backend/app when running this file directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from services.audio_service import AudioConfig, VocalizationDetector
from services.ml_service import CatVocalModel


POST_URL = "http://0.0.0.0:8000/api/emotion/latest"
ALLOWED_LABELS = {"food", "brushing", "isolation"}


def post_prediction(payload: dict) -> None:
    try:
        label = str(payload.get("label", "")).strip().lower()
        if label not in ALLOWED_LABELS:
            print(f"Skipping unsupported prediction label: {label or 'unknown'}")
            return

        response = requests.post(
            POST_URL,
            json={
                "timestamp": payload["timestamp"],
                "voice_type": label,
            },
            timeout=3,
        )
        response.raise_for_status()
    except Exception as exc:
        print(f"POST failed: {exc}")


def main() -> None:
    config = AudioConfig(
        sample_rate=16000,
        chunk_size=1024,
        channels=1,
        rms_threshold=0.015,      # tune this for your room
        pre_roll_chunks=8,
        silence_chunks_to_end=6,
        min_event_chunks=4,
        max_event_chunks=60,
        cooldown_seconds=0.75,
    )

    detector = VocalizationDetector(config)

    model_path = os.path.join(BACKEND_DIR, "models", "cs_classifier.pkl")
    model = CatVocalModel(model_path)

    last_prediction_time = 0.0

    print("Starting microphone listener...")
    print("Press Ctrl+C to stop.")

    stream = sd.RawInputStream(
        samplerate=config.sample_rate,
        blocksize=config.chunk_size,
        channels=config.channels,
        dtype="int16",
    )

    with stream:
        while True:
            chunk, overflowed = stream.read(config.chunk_size)

            if overflowed:
                print("Warning: audio overflow")

            wav_bytes = detector.process_chunk(bytes(chunk))

            if wav_bytes is None:
                continue

            now = time.time()
            if now - last_prediction_time < config.cooldown_seconds:
                continue

            prediction = model.predict(wav_bytes)

            payload = {
                "timestamp": datetime.now().isoformat(),
                "event": "cat_vocalization",
                "label": prediction["label"],
            }

            print(json.dumps(payload, indent=2))
            post_prediction(payload)

            last_prediction_time = now


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped microphone listener.")
