import librosa
import numpy as np
import warnings

warnings.filterwarnings("ignore")

class VocalAnalyzer:

    def __init__(self):
        print("\n🎧 Initializing Vocal Engine...")

    def analyze_audio(self, audio_path):
        print(f"\n🎵 Loading audio: {audio_path}")

        try:
            y, sr = librosa.load(audio_path, sr=None)
        except Exception:
            return {"error": "Failed to load audio (try WAV format)"}

        # ----- PITCH -----
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7")
        )

        valid_pitch = f0[~np.isnan(f0)]
        if len(valid_pitch) == 0:
            avg_pitch = 0
            pitch_variance = 0
        else:
            avg_pitch = float(np.mean(valid_pitch))
            pitch_variance = float(np.var(valid_pitch))

        # ----- ENERGY -----
        rms = librosa.feature.rms(y=y)
        energy_level = float(np.mean(rms))

        # ----- TEMPO -----
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # ----- FEEDBACK -----
        if avg_pitch < 80:
            delivery = "Too Monotone"
        elif avg_pitch > 200:
            delivery = "Too High-Pitched"
        else:
            delivery = "Good Vocal Delivery"

        return {
            "pitch_variance": round(pitch_variance, 2),
            "avg_pitch": round(avg_pitch, 2),
            "energy": round(energy_level, 4),
            "tempo_bpm": tempo,
            "delivery_status": delivery
        }

