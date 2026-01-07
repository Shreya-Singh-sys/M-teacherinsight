import librosa
import numpy as np

class InteractionEngine:
    """
    Classroom Interaction Analysis Engine
    -------------------------------------
    Measures silence vs speech to estimate student interaction.
    Current: Local audio-based estimation (librosa)
    Azure-ready: Can be extended using Azure Speech diarization / turn-taking
    """

    def analyze(self, audio_path):
        try:
            # 1. Load audio (preserve original sampling rate)
            y, sr = librosa.load(audio_path, sr=None)

            if len(y) == 0:
                return {
                    "interaction_ratio_percent": 0,
                    "class_mode": "No Audio"
                }

            # 2. Detect non-silent (spoken) intervals
            non_silent_intervals = librosa.effects.split(y, top_db=20)

            # 3. Calculate speech vs silence duration
            total_samples = len(y)
            speech_samples = sum(
                end - start for start, end in non_silent_intervals
            )

            speech_ratio = speech_samples / total_samples
            silence_ratio = 1.0 - speech_ratio

            # 4. Interaction score derived from silence gaps
            interaction_score = int(silence_ratio * 100)

            # Cap to avoid misinterpretation of dead air
            if interaction_score > 60:
                interaction_score = 60

            # 5. Determine classroom mode
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
            return {
                "interaction_ratio_percent": 0,
                "class_mode": "Error"
            }
