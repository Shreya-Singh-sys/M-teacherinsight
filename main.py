import os
import shutil
import json
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel  # <--- NEW IMPORT

# Import your analyzers
from stream1_content import ContentAnalyzer
from stream2_vocal import VocalAnalyzer
from stream3_interaction import InteractionAnalyzer
from stream4_video import VideoAnalyzer
from coach_engine import CoachEngine
import asyncio  # <--- NEW IMPORT

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_DIR = Path("input")
INPUT_DIR.mkdir(exist_ok=True)

print("🚀 Initializing AI Engines...")
content_engine = ContentAnalyzer()
vocal_engine = VocalAnalyzer()
interaction_engine = InteractionAnalyzer()
video_engine = VideoAnalyzer()
coach_engine = CoachEngine()  # <--- NEW INITIALIZATION

# --- Data Model for Coaching ---
class CoachRequest(BaseModel):  # <--- NEW CLASS
    analysis_data: dict
    user_query: str

def ensure_wav(audio_path):
    path_obj = Path(audio_path)
    wav_path = path_obj.with_suffix(".wav")
    if not wav_path.exists():
        print(f"Converting to WAV: {wav_path}")
        os.system(f'ffmpeg -y -i "{audio_path}" -ac 1 -ar 16000 "{wav_path}" -loglevel quiet')
    return str(wav_path)

def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return clean_data(obj.tolist())
    else:
        return obj

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # ... (Your existing analyze code remains exactly the same) ...
    print(f"\n📥 Received file: {file.filename}")
    
    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    video_path = str(save_path)
    audio_path = ensure_wav(video_path)

    results = {}

    # Stream 1
    try:
        transcript = content_engine.transcribe_audio(audio_path)
        clarity_data = content_engine.analyze_clarity(transcript)
        if isinstance(clarity_data, str):
            try:
                results["clarity"] = json.loads(clarity_data)
            except:
                results["clarity"] = {"feedback": clarity_data, "clarity_score": 70}
        else:
            results["clarity"] = clarity_data
    except Exception as e:
        print(f"Stream 1 Error: {e}")
        results["clarity"] = {"error": str(e)}

    # Stream 2
    try:
        results["vocal"] = vocal_engine.analyze_audio(audio_path)
    except Exception as e:
        print(f"Stream 2 Error: {e}")
        results["vocal"] = {"error": str(e)}

    # Stream 3
    try:
        results["interaction"] = interaction_engine.analyze_interaction(audio_path)
    except Exception as e:
        print(f"Stream 3 Error: {e}")
        results["interaction"] = {"error": str(e)}

    # Stream 4
    try:
        results["video"] = video_engine.analyze_video(video_path)
    except Exception as e:
        print(f"Stream 4 Error: {e}")
        results["video"] = {"error": str(e)}

    print("✅ Analysis Complete. Cleaning Data & Sending...")
    safe_results = clean_data(results)
    return safe_results

    
    # Run Clarity Analysis (Must happen after transcript is done)
    # This is fast so we can run it normally
    try:
        clarity_data = content_engine.analyze_clarity(transcript)
        if isinstance(clarity_data, str):
            try:
                clarity_res = json.loads(clarity_data)
            except:
                clarity_res = {"feedback": clarity_data, "clarity_score": 70}
        else:
            clarity_res = clarity_data
    except Exception as e:
        clarity_res = {"error": str(e)}

    # Consolidate Results
    results = {
        "clarity": clarity_res,
        "vocal": vocal_res,
        "interaction": interaction_res,
        "video": video_res
    }

    print("✅ Analysis Complete. Cleaning Data & Sending...")
    safe_results = clean_data(results)
    return safe_results
# --- NEW ENDPOINT FOR COACHING ---
@app.post("/coach")
async def ask_coach(request: CoachRequest):
    print(f"\n🤖 Coach Query Received: {request.user_query}")
    advice = coach_engine.provide_coaching(
        request.analysis_data, 
        request.user_query
    )
    return {"reply": advice}

@app.get("/")
def home():
    return {"message": "TIE Backend is Running!"}