import collections
import io
import wave
from dataclasses import dataclass

import numpy as np

from scipy.signal import butter, lfilter

@dataclass
class AudioConfig:
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    sample_width: int = 2  # 16-bit audio
    pre_roll_chunks: int = 8
    silence_chunks_to_end: int = 6
    min_event_chunks: int = 4
    max_event_chunks: int = 60
    rms_threshold: float = 0.015
    cooldown_seconds: float = 0.75


def pcm16_bytes_to_float32(audio_bytes: bytes) -> np.ndarray:
    """Convert raw 16-bit PCM bytes to float32 numpy array in [-1, 1]."""
    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio /= 32768.0
    return audio


def compute_rms(audio_float: np.ndarray) -> float:
    """Compute RMS energy of a float audio signal."""
    if audio_float.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio_float))))

def encode_wav_bytes(
    pcm_frames: list[bytes],
    sample_rate: int,
    channels: int,
    sample_width: int,
) -> bytes:
    """Pack raw PCM frames into a WAV file stored in memory."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(pcm_frames))
    return buffer.getvalue()

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    return butter(order, [low, high], btype='band')

def apply_bandpass_filter(audio_float, lowcut, highcut, fs):
    b, a = butter_bandpass(lowcut, highcut, fs)
    filtered = lfilter(b, a, audio_float)
    return filtered


class VocalizationDetector:
    """
    Tracks an audio stream and segments likely vocal events.
    """

    def __init__(self, config: AudioConfig):
        self.config = config
        self.pre_roll = collections.deque(maxlen=config.pre_roll_chunks)
        self.in_event = False
        self.event_frames: list[bytes] = []
        self.silence_count = 0
        self.b, self.a = butter_bandpass(300, 4000, config.sample_rate)

    def process_chunk(self, chunk: bytes) -> bytes | None:
        """
        Feed one chunk at a time.
        Returns WAV bytes when a full event is finished, else None.
        """
        audio_float = pcm16_bytes_to_float32(chunk)

        filtered = lfilter(self.b, self.a, audio_float)

        rms = compute_rms(filtered)

   
        # print(rms)
        active = rms >= self.config.rms_threshold

        if not self.in_event:
            self.pre_roll.append(chunk)
            
            if active:
                self.in_event = True
                self.event_frames = list(self.pre_roll)
                self.event_frames.append(chunk)
                self.silence_count = 0
                print(rms)
            return None

        self.event_frames.append(chunk)

        if active:
            self.silence_count = 0
        else:
            self.silence_count += 1

        too_long = len(self.event_frames) >= self.config.max_event_chunks
        ended_by_silence = self.silence_count >= self.config.silence_chunks_to_end

        if too_long or ended_by_silence:
            event_length_ok = len(self.event_frames) >= self.config.min_event_chunks
            wav_bytes = None

            if event_length_ok:
                wav_bytes = encode_wav_bytes(
                    pcm_frames=self.event_frames,
                    sample_rate=self.config.sample_rate,
                    channels=self.config.channels,
                    sample_width=self.config.sample_width,
                )
            else:
                print("Sound event did not meet minimum length requirements and was discarded.")

            self.reset()
            return wav_bytes

        return None

    def reset(self) -> None:
        self.in_event = False
        self.event_frames = []
        self.silence_count = 0
        self.pre_roll.clear()