import os
import shutil
import json
import asyncio
import subprocess
import numpy as np
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from fusion_engine import FusionEngine 
from fastapi.responses import FileResponse # <--- NEW IMPORT
from pdf_engine import PDFGenerator # <--- NEW IMPORT
from fastapi.responses import JSONResponse  # <--- YEH LINE ADD KAREIN
from stream1_content import ContentAnalyzer
from stream2_vocal import VocalAnalyzer
from stream3_interaction import InteractionAnalyzer
from stream4_video import VideoAnalyzer
from coach_engine import CoachEngine
from history_engine import HistoryEngine

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
pdf_engine = PDFGenerator()
history_engine = HistoryEngine()

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


def create_fast_file(input_path):
    # output name: video_fast.mp4
    output_path = str(input_path).replace(".mp4", "_fast.mp4")
    print("⚡ Optimizing video for speed...")
    command = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-ss', '0', '-t', '45',
        '-vf', 'scale=480:-1',
        '-r', '15',
        output_path
    ]
    # Run silently
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

@app.post("/upload_video")
async def analyze_video(file: UploadFile = File(...)):
    print(f"\n📥 Received file: {file.filename}")
    
    # 1. Save Original
    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. CREATE THE "FAST" VERSION
    # This takes ~2 seconds but saves 2 minutes of processing time
    fast_video_path = create_fast_file(str(save_path))
    fast_audio_path = ensure_wav(fast_video_path) # Extract audio from the short file

    print("🚀 Starting PARALLEL Analysis on Fast Version...")

    # 3. Analyze the Small Files
    task_transcript = asyncio.to_thread(content_engine.transcribe_audio, fast_audio_path)
    task_vocal = asyncio.to_thread(vocal_engine.analyze_audio, fast_audio_path)
    task_interaction = asyncio.to_thread(interaction_engine.analyze_interaction, fast_audio_path)
    # Note: We analyze the FAST video here
    task_video = asyncio.to_thread(video_engine.analyze_video, fast_video_path)

    transcript, vocal_res, interaction_res, video_res = await asyncio.gather(
        task_transcript, 
        task_vocal, 
        task_interaction, 
        task_video
    )
    
    # ... (Rest of your fusion/response code is unchanged) ...    
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
    # 1. Get Previous Session (for comparison)
    prev_session = history_engine.get_previous_session()

    comparison = {}
    if prev_session:
        comparison = {
            "overall_diff": overall_score - prev_session.get("overall_score", 0),
        
        # Use .get() here to prevent crash if clarity is missing
            "clarity_diff": raw_results["clarity"].get("clarity_score", 0) - prev_session["clarity"].get("clarity_score", 0),
        
        # This was the line causing your error. I added .get() to the first part.
            "interaction_diff": raw_results["interaction"].get("interaction_ratio_percent", 0) - prev_session["interaction"].get("interaction_ratio_percent", 0),
        
        # Use .get() here too for safety
           "energy_diff": raw_results["video"].get("gesture_energy_score", 0) - prev_session["video"].get("gesture_energy_score", 0)}        
    else:
        comparison = {
            "overall_diff": 0, "clarity_diff": 0, "interaction_diff": 0, "energy_diff": 0}

# 2. Build Final Output
    final_output = {
        **raw_results,
        "overall_score": overall_score,
        "comparison": comparison,  # <--- SEND DIFFS TO FRONTEND
        "timestamp": datetime.now().strftime("%Y-%m-%d")}
    final_output = clean_data(final_output)

# 3. SAVE this session for next time
    history_engine.save_session(final_output)

    print(f"✅ Comparison Data Generated. Diff: {comparison['overall_diff']}")
    return final_output
    # ---- MongoDB Store ----

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