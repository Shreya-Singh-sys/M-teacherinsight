# import os
# import whisper
# import google.generativeai as genai
# import soundfile as sf
# import json

# class ContentAnalyzer:

#     def __init__(self):
#         print("\n📘 Initializing Content Engine (Whisper + Gemini)...")
#         self.whisper_model = whisper.load_model("base")

#         # Load Gemini key safely
#         # api_key = os.getenv("AIzaSyBIRIbMnHtS2vjNaL1p7N8v8nx-jEqLt_g")
#         genai.configure(api_key="AIzaSyBIRIbMnHtS2vjNaL1p7N8v8nx-jEqLt_g")

#         self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")

#     def transcribe_audio(self, audio_path):
#         print(f"\n🎤 Transcribing audio: {audio_path}")

#         if not os.path.exists(audio_path):
#             return "ERROR: Audio file not found."

#         # result = self.whisper_model.transcribe(audio_path)
#         result = self.whisper_model.transcribe(audio_path, language="en", task="transcribe")

#         return result["text"]
    

#     def analyze_clarity(self, transcript_text):
#         print("🧠 Sending transcript to Gemini...")

#         prompt = f"""
# You are an expert teacher evaluator.

# Analyze this classroom transcript and return ONLY a raw JSON object:
# {transcript_text}

# Return JSON with keys:
# - clarity_score (1-100)
# - jargon_count
# - filler_count
# - sentiment
# - feedback
# """

#         try:
#             response = self.gemini_model.generate_content(prompt)
#             cleaned_text = response.text
#             if "```" in cleaned_text:
#                 cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()
#             return cleaned_text
#         except Exception as e:
#             print("Gemini ERROR:", e)
#             # fallback JSON
#             return json.dumps({
#                 "clarity_score": 0,
#                 "jargon_count": 0,
#                 "filler_count": 0,
#                 "sentiment": "Neutral",
#                 "feedback": "AI failed to grade transcript."
#             })
import os
import whisper
import google.generativeai as genai
import json

class ContentAnalyzer:
    
    def __init__(self):
        print("\n📄 Initializing Content Engine (Whisper + Gemini)...")
        self.whisper_model = whisper.load_model("base")

        # --- SECURITY NOTE: REPLACE WITH YOUR ACTUAL API KEY ---
        # Make sure you revoke the key visible in your screenshot and generate a new one!
        api_key = "AIzaSyCsOXRO5W5zwJX86zAmsncw7LVF5K4MO1w" 
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash") # Updated to latest model if available, or keep 1.5-flash

    def transcribe_audio(self, audio_path):
        print(f"\n🎤 Transcribing audio: {audio_path}")
        
        if not os.path.exists(audio_path):
            return "ERROR: Audio file not found."

        # Transcribe
        result = self.whisper_model.transcribe(audio_path, language="en", task="transcribe")
        return result["text"]

    def analyze_clarity(self, transcript_text):
        print("🧠 Sending transcript to Gemini...")

        prompt = f"""
        You are an expert teacher evaluator.
        
        Analyze this classroom transcript and return ONLY a raw JSON object:
        "{transcript_text}"
        
        Return JSON with keys:
        - clarity_score (1-100)
        - jargon_count
        - filler_count
        - sentiment
        - feedback
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            raw_text = response.text
            
            # --- FIX: CLEAN THE JSON ---
            # Gemini often wraps JSON in markdown (```json ... ```). We must remove it.
            if "```" in raw_text:
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            return raw_text

        except Exception as e:
            print("Gemini ERROR:", e)
            # Fallback JSON if API fails
            return json.dumps({
                "clarity_score": 0,
                "jargon_count": 0,
                "filler_count": 0,
                "sentiment": "Neutral",
                "feedback": "AI failed to grade transcript."
            })