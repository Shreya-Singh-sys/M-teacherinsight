import librosa
import numpy as np

class VocalEngine:
    """
    Vocal Delivery Analysis Engine
    ------------------------------
    Current: Local pitch analysis using librosa (pYIN)
    Azure-ready: Can be extended using Azure Speech prosody APIs
    """

    def analyze(self, audio_path):
        try:
            # 1. Load audio file
            # sr=None keeps original sampling rate (more accurate pitch)
            y, sr = librosa.load(audio_path, sr=None)

            # 2. Extract Pitch (Fundamental Frequency - F0) using pYIN
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7')
            )

            # 3. Filter out silence (NaN values)
            valid_pitch = f0[~np.isnan(f0)]

            if valid_pitch.size == 0:
                return {
                    "avg_pitch": 0,
                    "delivery_status": "Silent"
                }

            avg_pitch = int(np.mean(valid_pitch))

            # 4. Determine delivery style
            # Avg male speech: ~85–180 Hz
            # Avg female speech: ~165–255 Hz
            if avg_pitch < 100:
                status = "Monotone/Low"
            elif avg_pitch > 220:
                status = "High Energy/Excited"
            else:
                status = "Normal/Balanced"

            return {
                "avg_pitch": avg_pitch,
                "delivery_status": status
            }

        except Exception as e:
            print(f"Vocal Error: {e}")
            return {
                "avg_pitch": 0,
                "delivery_status": "Error"
            }
