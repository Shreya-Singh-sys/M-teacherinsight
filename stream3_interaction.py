# class InteractionEngine:
#     def analyze(self, path):
#         return {"interaction_ratio_percent": 30, "class_mode": "Lecture"}
import librosa
import numpy as np

class InteractionEngine:
    def analyze(self, audio_path):
        try:
            # 1. Load audio
            y, sr = librosa.load(audio_path)
            
            # 2. Split audio into non-silent chunks
            # top_db=20 means anything 20 decibels quieter than max is "silence"
            non_silent_intervals = librosa.effects.split(y, top_db=20)
            
            # 3. Calculate total duration of speech vs total time
            total_samples = len(y)
            speech_samples = sum([end - start for start, end in non_silent_intervals])
            
            speech_ratio = speech_samples / total_samples
            silence_ratio = 1.0 - speech_ratio
            
            # 4. Interaction Logic
            # If silence is between 15% and 40%, it likely means students are engaging/teacher is pausing.
            # < 10% means continuous lecturing.
            interaction_score = int(silence_ratio * 100) 
            
            # Cap it reasonable (e.g., silence > 60% is probably just dead air, not interaction)
            if interaction_score > 60: interaction_score = 60
            
            # Determine Mode
            if interaction_score < 10:
                mode = "Lecture (Low Interaction)"
            elif interaction_score < 30:
                mode = "Interactive Lecture"
            else:
                mode = "Discussion / Q&A"

            return {
                "interaction_ratio_percent": interaction_score, 
                "class_mode": mode
            }

        except Exception as e:
            print(f"Interaction Error: {e}")
            return {"interaction_ratio_percent": 0, "class_mode": "Error"}