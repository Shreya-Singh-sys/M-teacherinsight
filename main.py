import os
import shutil
import json
import numpy as np  # Added to handle the scientific numbers
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Import your existing analyzers
from stream1_content import ContentAnalyzer
from stream2_vocal import VocalAnalyzer
from stream3_interaction import InteractionAnalyzer
from stream4_video import VideoAnalyzer

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

def ensure_wav(audio_path):
    path_obj = Path(audio_path)
    wav_path = path_obj.with_suffix(".wav")
    if not wav_path.exists():
        print(f"Converting to WAV: {wav_path}")
        os.system(f'ffmpeg -y -i "{audio_path}" -ac 1 -ar 16000 "{wav_path}" -loglevel quiet')
    return str(wav_path)

# --- THE MAGIC FIX FUNCTION ---
def clean_data(obj):
    """
    Recursively converts 'Scientific Numbers' (NumPy) into 
    standard Python numbers so the Web Server doesn't crash.
    """
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
# -----------------------------

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
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
            # Try to parse string JSON, handle if it's messy
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
    
    # Use the cleaner function before returning
    safe_results = clean_data(results)
    
    return safe_results

@app.get("/")
def home():
    return {"message": "TIE Backend is Running!"}