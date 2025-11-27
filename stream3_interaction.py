# from pyannote.audio import Pipeline
# import os

# class InteractionAnalyzer:

#     def __init__(self):
#         print("\n🟣 Initializing Interaction Engine...")

#         # --- FIX IS HERE: PUT YOUR TOKEN DIRECTLY IN QUOTES ---
#         # Do not use os.getenv() for the token value itself.
#         # Replace the text below with your actual token starting with hf_
#         hf_token = "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"  # <--- PASTE YOUR FULL TOKEN HERE

#         if not hf_token:
#             print("❌ ERROR: No HuggingFace token found")
#             self.pipeline = None
#             return

#         try:
#             self.pipeline = Pipeline.from_pretrained(
#                 "pyannote/speaker-diarization",
#                 use_auth_token=hf_token
#             )
#         except Exception as e:
#             print("Pyannote Load ERROR:", e)
#             self.pipeline = None

#     def analyze_interaction(self, audio_path):
#         if self.pipeline is None:
#             return {"error": "Interaction Engine not initialized"}

#         print(f"\n📢 Running interaction analysis on {audio_path}")

#         try:
#             diarization = self.pipeline(audio_path)
#         except Exception:
#             return {"error": "Pyannote failed while processing audio"}

#         speaker_segments = list(diarization.itertracks(yield_label=True))
        
#         if len(speaker_segments) == 0:
#             return {"student_ratio": 0, "class_mode": "Teacher Only"}

#         speaker_ids = {label for _, _, label in speaker_segments}

#         if len(speaker_ids) == 1:
#             return {"student_ratio": 0, "class_mode": "Teacher Only"}

#         # Calculate durations
#         teacher_duration = sum(seg.end - seg.start for seg, _, label in speaker_segments if label == "SPEAKER_00")
#         other_duration = sum(seg.end - seg.start for seg, _, label in speaker_segments if label != "SPEAKER_00")

#         total_duration = teacher_duration + other_duration
#         if total_duration == 0:
#              return {"interaction_ratio_percent": 0, "class_mode": "Teacher Only"}

#         ratio = (other_duration / total_duration) * 100

#         return {
#             "interaction_ratio_percent": round(ratio, 1),
#             "class_mode": "Interactive" if ratio > 20 else "Lecture Mode"
#         }
from pyannote.audio import Pipeline
import os

class InteractionAnalyzer:

    def __init__(self):
        print("\n🟣 Initializing Interaction Engine...")

        # --- PASTE YOUR TOKEN BELOW ---
        hf_token = "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" # Paste your full token inside these quotes

        if not hf_token:
            print("❌ ERROR: No HuggingFace token found")
            self.pipeline = None
            return

        try:
            # --- FIX: Changed 'use_auth_token' to 'token' ---
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token 
            )
        except Exception as e:
            print(f"Pyannote Load ERROR: {e}")
            self.pipeline = None

    def analyze_interaction(self, audio_path):
        if self.pipeline is None:
            return {"error": "Interaction Engine not initialized"}

        print(f"\n📢 Running interaction analysis on {audio_path}")

        try:
            diarization = self.pipeline(audio_path)
        except Exception as e:
            # If it fails here, it usually means the Terms of Service weren't accepted
            return {"error": f"Pyannote failed: {e}"}

        speaker_segments = list(diarization.itertracks(yield_label=True))
        
        if len(speaker_segments) == 0:
            return {"student_ratio": 0, "class_mode": "Teacher Only"}

        speaker_ids = {label for _, _, label in speaker_segments}

        if len(speaker_ids) == 1:
            return {"student_ratio": 0, "class_mode": "Teacher Only"}

        # Calculate durations
        teacher_duration = sum(seg.end - seg.start for seg, _, label in speaker_segments if label == "SPEAKER_00")
        other_duration = sum(seg.end - seg.start for seg, _, label in speaker_segments if label != "SPEAKER_00")

        total_duration = teacher_duration + other_duration
        if total_duration == 0:
             return {"interaction_ratio_percent": 0, "class_mode": "Teacher Only"}

        ratio = (other_duration / total_duration) * 100

        return {
            "interaction_ratio_percent": round(ratio, 1),
            "class_mode": "Interactive" if ratio > 20 else "Lecture Mode"
        }