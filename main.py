import os
import shutil
import json
import asyncio
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from fusion_engine import FusionEngine 
from fastapi.responses import FileResponse # <--- NEW IMPORT
from pdf_engine import ReportGenerator # <--- NEW IMPORT

# Import your analyzers
from stream1_content import ContentAnalyzer
from stream2_vocal import VocalAnalyzer
from stream3_interaction import InteractionAnalyzer
from stream4_video import VideoAnalyzer
from coach_engine import CoachEngine

app = FastAPI()

# Enable CORS (Allows Frontend to talk to Backend)
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
coach_engine = CoachEngine()
# ... inside Initializing AI Engines ...
fusion_engine = FusionEngine() 
pdf_engine = ReportGenerator() # <--- NEW INIT        # <--- NEW INIT

# --- Data Models ---
class CoachRequest(BaseModel):
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
    print(f"\n📥 Received file: {file.filename}")
    
    # Save File
    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    video_path = str(save_path)
    audio_path = ensure_wav(video_path)

    print("🚀 Starting PARALLEL Analysis...")

    # Run AI Tasks
    task_transcript = asyncio.to_thread(content_engine.transcribe_audio, audio_path)
    task_vocal = asyncio.to_thread(vocal_engine.analyze_audio, audio_path)
    task_interaction = asyncio.to_thread(interaction_engine.analyze_interaction, audio_path)
    task_video = asyncio.to_thread(video_engine.analyze_video, video_path)

    transcript, vocal_res, interaction_res, video_res = await asyncio.gather(
        task_transcript, task_vocal, task_interaction, task_video
    )
    
    # Run Clarity
    try:
        clarity_data = content_engine.analyze_clarity(transcript)
        if isinstance(clarity_data, str):
            try:
                clarity_res = json.loads(clarity_data)
            except:
                clarity_res = {"feedback": clarity_data, "clarity_score": 75}
        else:
            clarity_res = clarity_data
    except Exception as e:
        clarity_res = {"error": str(e), "clarity_score": 0}

    # Consolidate Stream Results
    raw_results = {
        "clarity": clarity_res,
        "vocal": vocal_res,
        "interaction": interaction_res,
        "video": video_res
    }

    # --- NEW: CALCULATE OVERALL SCORE ---
    overall_score = fusion_engine.calculate_overall(raw_results)

    # Add score to final response
    final_output = {
        **raw_results,
        "overall_score": overall_score 
    }

    print(f"✅ Analysis Complete. Overall Score: {overall_score}/100")
    return clean_data(final_output)

@app.post("/coach")
async def ask_coach(request: CoachRequest):
    print(f"\n🤖 Coach Query: {request.user_query}")
    advice = coach_engine.provide_coaching(
        request.analysis_data, 
        request.user_query
    )
    return {"reply": advice}
# --- PDF GENERATION ENDPOINT ---
@app.post("/generate_pdf")
async def generate_pdf(request: dict):
    print("📄 Generating PDF Report...")

    # Create a unique filename
    filename = "TIE_Report_Session.pdf"
    file_path = INPUT_DIR / filename

    # Generate PDF using the engine
    pdf_engine.generate_report(request, str(file_path))

    # Return as a downloadable file
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='application/pdf'
    )

@app.get("/")
def home():
    return {"message": "TIE Backend is Running!"}