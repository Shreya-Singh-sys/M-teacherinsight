import whisper

class ContentEngine:
    def __init__(self):
        print("🎧 Loading Audio AI (Tiny)...")
        # English only model is 2x faster
        self.whisper_model = whisper.load_model("tiny.en")

    def transcribe(self, audio_path):
        # 1. Transcribe
        result = self.whisper_model.transcribe(audio_path)
        text = result["text"]
        
        # 2. Calculate WPM (Words Per Minute)
        # We assume the clip is approx 45 seconds long
        word_count = len(text.split())
        wpm = int(word_count / 0.75) 
        
        # 3. Generate Detailed 3-4 Line Feedback
        feedback = self._generate_detailed_feedback(wpm)
        
        return {
            "transcript_preview": text[:100] + "...",
            "wpm": wpm,
            "clarity_score": self._calculate_score(wpm),
            "feedback": feedback
        }

    def _calculate_score(self, wpm):
        # Ideal WPM is around 130-150. Drops if too fast or too slow.
        if 120 <= wpm <= 160: return 95
        if 100 <= wpm < 120: return 85
        if wpm > 160: return 80
        return 60

    def _generate_detailed_feedback(self, wpm):
        if wpm < 100:
            return (
                f"Your speaking pace is quite slow ({wpm} WPM), which might cause student disengagement during longer explanations. "
                "Try to increase your tempo slightly to maintain higher energy levels in the classroom. "
                "Consider using more dynamic pauses rather than long silences to keep the momentum going. "
                "A target of 130 WPM would be ideal for this subject matter."
            )
        elif 100 <= wpm <= 120:
            return (
                f"Your pacing is steady ({wpm} WPM) and easy to follow, but could benefit from a slight energy boost. "
                "You are very clear, which is excellent for complex topics, but adding a bit more speed in excitement areas would help. "
                "Try varying your speed—slow down for key definitions, but speed up for examples. "
                "Overall, a solid delivery that prioritizes clarity."
            )
        elif 120 < wpm <= 160:
            return (
                f"Excellent delivery speed ({wpm} WPM)! You are hitting the 'Goldilocks zone' for teaching. "
                "Your rate allows students to take notes while keeping their attention focused on you. "
                "The flow of information is efficient without feeling rushed. "
                "Maintain this energy, as it demonstrates confidence and mastery of the material."
            )
        else: # > 160
            return (
                f"You are speaking quite fast ({wpm} WPM). While this shows passion, some students might fall behind. "
                "Try to deliberately slow down when introducing new terminology or complex formulas. "
                "Pausing after key statements will allow the information to 'sink in' better. "
                "Remember, silence is a powerful teaching tool—don't be afraid to use it."
            )