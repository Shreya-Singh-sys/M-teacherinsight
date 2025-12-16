import whisper
import re
import numpy as np
import os
from pathlib import Path

class ContentAnalyzer:
    def __init__(self):
        print("✅ Local Clarity Engine Loaded (Whisper Only)")
        # Load the base model
        self.whisper_model = whisper.load_model("tiny.en")
    def transcribe_audio(self, audio_path):
        print(f"🎤 Transcribing....")
        
        # Load audio using Whisper's tool
        audio = whisper.load_audio(audio_path)
        
        # HARD LIMIT: Crop audio to first 45 seconds
        # 16000 Hz * 45 = 720,000 samples
        audio = whisper.pad_or_trim(audio, length=16000 * 45)
        
        # Transcribe
        result = self.whisper_model.transcribe(audio)
        return result["text"]
    # ---------- STEP 2: LOCAL CLARITY ANALYSIS ----------
    def analyze_clarity(self, transcript):
        print("🧠 Running Local Clarity Analysis (No Gemini)...")

        # 1. Handle Empty Transcript (Agar audio silent tha)
        if not transcript or not transcript.strip():
            return {
                "clarity_score": 0,
                "feedback": "No speech detected in the video.",
                "total_words": 0,
                "filler_words": 0,
                "pace": 0
            }

        words = transcript.split()
        total_words = len(words)

        # Filler word detection
        filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically"]
        
        transcript_lower = transcript.lower()
        filler_count = 0
        for fw in filler_words:
            # Regex to match whole words only
            filler_count += len(re.findall(r'\b' + re.escape(fw) + r'\b', transcript_lower))

        # Sentence count
        sentences = re.split(r'[.!?]', transcript)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = max(len(sentences), 1)

        # Speech rate (words per sentence)
        # Avoid Division by Zero
        if sentence_count > 0:
            pace = total_words / sentence_count
        else:
            pace = 0

        # ---- CLARITY SCORING LOGIC ----
        clarity_score = 100

        if filler_count > 8:
            clarity_score -= 20
        elif filler_count > 4:
            clarity_score -= 10

        if pace < 6:
            clarity_score -= 10
        elif pace > 20:
            clarity_score -= 10

        clarity_score = max(40, min(clarity_score, 100))

        feedback = []
        if clarity_score > 85:
            feedback.append("Excellent clarity and smooth explanation.")
        elif clarity_score > 70:
            feedback.append("Good clarity with minor improvements possible.")
        elif clarity_score > 55:
            feedback.append("Average clarity. Try reducing filler words and improve pace.")
        else:
            feedback.append("Low clarity. Improve pacing and articulation.")

        response = {
            "clarity_score": int(clarity_score),
            "feedback": " ".join(feedback),
            "total_words": total_words,
            "filler_words": filler_count,
            "pace": round(pace, 2)
        }

        print("✅ Local Clarity Analysis Completed")
        return response