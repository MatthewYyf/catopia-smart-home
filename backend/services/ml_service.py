import pickle
import io
import struct
import numpy as np
import librosa
import webrtcvad


class CatVocalModel:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.labels     = ["isolation", "food", "brushing"]

        # Load saved model
        with open(model_path, 'rb') as f:
            saved = pickle.load(f)

        self.hmm_models = saved['hmm_models']   # {class_idx: GMMHMM}
        self.le         = saved['le']
        self.sr         = saved['SR']
        self.n_fft      = saved['N_FFT']
        self.hop_len    = saved['HOP_LEN']
        self.frame_len  = saved['FRAME_LEN']

    # ----------------------------------------------------------
    def _remove_silence(self, y: np.ndarray) -> np.ndarray:
        """WebRTC VAD silence removal, falls back to energy trim."""
        try:
            target_sr  = 16000
            y_vad      = librosa.resample(y, orig_sr=self.sr, target_sr=target_sr)
            vad        = webrtcvad.Vad(2)
            frame_len  = int(target_sr * 30 / 1000)
            pcm        = (y_vad * 32767).astype(np.int16)
            scale      = self.sr / target_sr
            orig_frame = int(frame_len * scale)
            voiced_mask = np.zeros(len(y), dtype=bool)

            for i in range(0, len(pcm) - frame_len, frame_len):
                frame_bytes = struct.pack('%dh' % frame_len, *pcm[i:i + frame_len])
                try:
                    is_speech = vad.is_speech(frame_bytes, target_sr)
                except Exception:
                    is_speech = False
                orig_start = int(i * scale)
                orig_end   = min(orig_start + orig_frame, len(y))
                if is_speech:
                    voiced_mask[orig_start:orig_end] = True

            y_voiced = y[voiced_mask]
            if len(y_voiced) > self.sr * 0.05:
                return y_voiced
        except Exception:
            pass

        # Fallback: energy-based trim
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)
        return y_trimmed if len(y_trimmed) > self.sr * 0.05 else y

    # ----------------------------------------------------------
    def _extract_mfcc(self, y: np.ndarray) -> np.ndarray:
        """52-dim MFCC sequence: 13-dim (12 coeff + energy) + Δ/ΔΔ/ΔΔΔ."""
        mfcc = librosa.feature.mfcc(
            y=y, sr=self.sr,
            n_mfcc=12, n_mels=23,
            n_fft=self.n_fft,
            hop_length=self.hop_len,
            win_length=self.frame_len,
            window='hamming'
        )
        energy    = np.log(librosa.feature.rms(
            y=y, frame_length=self.frame_len, hop_length=self.hop_len
        ) + 1e-10)
        mfcc_full = np.vstack([energy, mfcc]).T                          # (T, 13)

        d1        = librosa.feature.delta(mfcc_full.T, order=1).T
        d2        = librosa.feature.delta(mfcc_full.T, order=2).T
        d3        = librosa.feature.delta(mfcc_full.T, order=3).T
        mfcc_full = np.hstack([mfcc_full, d1, d2, d3])                   # (T, 52)

        # Z-score normalise per sequence
        mfcc_full = (mfcc_full - mfcc_full.mean(axis=0)) / (mfcc_full.std(axis=0) + 1e-10)

        return mfcc_full

    # ----------------------------------------------------------
    def _hmm_score(self, model, sequence: np.ndarray) -> float:
        try:
            return model.score(sequence)
        except Exception:
            return -np.inf

    # ----------------------------------------------------------
    def predict(self, wav_bytes: bytes) -> dict:
        """
        Preprocess wav bytes and return predicted label.

        Parameters
        ----------
        wav_bytes : raw WAV file bytes (e.g. from open('meow.wav', 'rb').read())

        Returns
        -------
        {"label": "food" | "isolation" | "brushing"}
        """
        # 1. Decode bytes → numpy array
        y, _ = librosa.load(io.BytesIO(wav_bytes), sr=self.sr, mono=True)

        # 2. Silence removal
        y = self._remove_silence(y)

        # 3. Feature extraction
        seq = self._extract_mfcc(y)

        if seq.shape[0] < 5:
            return {"label": "unknown"}

        # 4. Score against each class HMM
        scores = {
            cls: self._hmm_score(model, seq)
            for cls, model in self.hmm_models.items()
        }

        # 5. Pick highest log-likelihood
        best_idx = max(scores, key=scores.get)
        label    = self.le.inverse_transform([best_idx])[0]

        return {"label": label}