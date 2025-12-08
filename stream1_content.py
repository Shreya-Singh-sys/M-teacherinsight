import whisper
import re
import numpy as np

class ContentAnalyzer:
    # ---------------------------------------------------------
    # FIX: Changed _init_ to __init__ (Double Underscores)
    # ---------------------------------------------------------
    def __init__(self):
        print("✅ Local Clarity Engine Loaded (Whisper Only)")
        # This now runs automatically when you create the object
        self.model = whisper.load_model("base")

    # ---------- STEP 1: SPEECH TO TEXT ----------
    def transcribe_audio(self, audio_path):
        print(f"🎤 Transcribing audio locally: {audio_path}")
        # self.model now exists, so this won't crash
        result = self.model.transcribe(audio_path)
        transcript = result["text"]
        print("✅ Transcription Complete")
        return transcript

    # ---------- STEP 2: LOCAL CLARITY ANALYSIS ----------
    def analyze_clarity(self, transcript):
        print("🧠 Running Local Clarity Analysis (No Gemini)...")

        words = transcript.split()
        total_words = len(words)

        # Filler word detection
        filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically"]
        
        # Improved filler count to ensure we don't count "so" inside "also"
        transcript_lower = transcript.lower()
        filler_count = 0
        for fw in filler_words:
            # Using regex to match whole words only for accuracy
            filler_count += len(re.findall(r'\b' + re.escape(fw) + r'\b', transcript_lower))

        # Sentence count
        sentences = re.split(r'[.!?]', transcript)
        # Filter out empty strings from split result
        sentences = [s for s in sentences if s.strip()]
        sentence_count = max(len(sentences), 1)

        # Speech rate (words per sentence)
        pace = total_words / sentence_count

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