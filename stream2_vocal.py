# class VocalEngine:
#     def analyze(self, path):
#         return {"avg_pitch": 120, "delivery_status": "Normal"}
import librosa
import numpy as np

class VocalEngine:
    def analyze(self, audio_path):
        try:
            # 1. Load the audio file
            y, sr = librosa.load(audio_path)
            
            # 2. Extract Pitch (Fundamental Frequency - F0) using pYIN
            f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            
            # 3. Filter out "NaN" (silence) values to get only spoken pitch
            valid_pitch = f0[~np.isnan(f0)]
            
            if len(valid_pitch) == 0:
                return {"avg_pitch": 0, "delivery_status": "Silent"}

            avg_pitch = int(np.mean(valid_pitch))

            # 4. Determine Delivery Status based on pitch
            # (Avg male speech ~85-180Hz, Female ~165-255Hz)
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
            return {"avg_pitch": 0, "delivery_status": "Error"}