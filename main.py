from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import os
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
INPUT_DIR = Path("input")
INPUT_DIR.mkdir(exist_ok=True)
JSON_FILE = "session_history.json"
USERS_FILE = "users.json"
CONFIG_FILE = "user_config.json"

# Import Engines
from pdf_engine import PDFGenerator
from stream1_content import ContentEngine
from stream2_vocal import VocalEngine
from stream3_interaction import InteractionEngine
from stream4_video import VideoEngine

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Frontend Folder
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Initialize Engines
pdf_engine = PDFGenerator()
content_engine = ContentEngine()
vocal_engine = VocalEngine()
interaction_engine = InteractionEngine()
video_engine = VideoEngine()

# --- DATA MODELS ---
class LoginModel(BaseModel):
    email: str
    password: str

class RegisterModel(BaseModel):
    name: str
    email: str
    password: str

class SettingsModel(BaseModel):
    name: str
    email: str
    theme: str

class CoachRequest(BaseModel):
    analysis_data: dict
    user_query: str

# --- HELPER FUNCTIONS ---
def get_json(filename, default_val):
    if not os.path.exists(filename): return default_val
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return default_val

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- ROUTES: PAGES ---
@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse("frontend/dashboard.html")

# --- ROUTES: AUTHENTICATION ---
@app.post("/api/register")
async def register_endpoint(user: RegisterModel):
    print(f"📝 Registering: {user.email}")
    users = get_json(USERS_FILE, {})
    
    if user.email in users:
        return {"status": "error", "message": "Email already registered"}
    
    users[user.email] = {
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "joined": datetime.now().strftime("%Y-%m-%d")
    }
    save_json(USERS_FILE, users)
    return {"status": "success", "message": "Account created"}

@app.post("/api/login")
async def login_endpoint(creds: LoginModel):
    print(f"🔑 Login Attempt: {creds.email}")
    users = get_json(USERS_FILE, {})
    
    if creds.email not in users:
        return {"status": "error", "message": "User does not exist"}
    
    user = users[creds.email]
    if user["password"] != creds.password:
        return {"status": "error", "message": "Incorrect password"}
    
    return {
        "status": "success",
        "user": {"name": user["name"], "email": user["email"]}
    }

# --- ROUTES: SETTINGS ---
@app.get("/api/settings")
async def get_settings():
    return get_json(CONFIG_FILE, {
        "name": "Teacher", 
        "email": "teacher@school.edu", 
        "theme": "light"
    })

@app.post("/api/settings/update")
async def update_settings(config: SettingsModel):
    data = get_json(CONFIG_FILE, {})
    data.update({"name": config.name, "email": config.email, "theme": config.theme})
    save_json(CONFIG_FILE, data)
    return {"status": "success"}

# --- ROUTES: ANALYSIS & HISTORY ---
@app.get("/api/history")
async def get_history():
    history = get_json(JSON_FILE, [])
    return history[::-1] # Newest first

@app.get("/api/latest-session")
async def get_latest():
    history = get_json(JSON_FILE, [])
    return history[-1] if history else {"error": "No data"}

@app.post("/coach")
async def coach_endpoint(req: CoachRequest):
    # Simple Logic for Coach
    q = req.user_query.lower()
    if "voice" in q: reply = "Your pitch variation is good. Try pausing more."
    elif "energy" in q: reply = "Your energy score is high! Keep it up."
    elif "fast" in q: reply = "You are speaking a bit fast. Slow down for emphasis."
    else: reply = "I analyzed your session. Ask me about Clarity or Energy."
    return {"reply": reply}

# --- MAIN ANALYSIS ENGINE ---
def optimize_files(input_path: Path):
    filename_no_ext = input_path.stem
    fast_video = INPUT_DIR / f"{filename_no_ext}_fast.mp4"
    fast_audio = INPUT_DIR / f"{filename_no_ext}_fast.wav"
    try:
        # Scale video to prevent odd-height errors (480:-2)
        subprocess.run(['ffmpeg', '-y', '-i', str(input_path), '-ss', '0', '-t', '45', 
                        '-vf', 'scale=480:-2', '-r', '15', '-c:v', 'libx264', '-preset', 'ultrafast', 
                        str(fast_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        subprocess.run(['ffmpeg', '-y', '-i', str(fast_video), '-ac', '1', '-ar', '16000', 
                        str(fast_audio)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return str(fast_video), str(fast_audio)
    except:
        return str(input_path), str(input_path)

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    print(f"\n🚀 Analyzing: {file.filename}")
    save_path = INPUT_DIR / file.filename.replace(" ", "_")
    with open(save_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    
    vid_path, aud_path = optimize_files(save_path)
    
    try:
        task1 = asyncio.to_thread(content_engine.transcribe, aud_path)
        task2 = asyncio.to_thread(vocal_engine.analyze, aud_path)
        task3 = asyncio.to_thread(interaction_engine.analyze, aud_path)
        task4 = asyncio.to_thread(video_engine.analyze, vid_path)
        
        results = await asyncio.gather(task1, task2, task3, task4, return_exceptions=True)
        
        def get_val(res, default): return res if not isinstance(res, Exception) else default
        
        data = {
            "timestamp": datetime.now().strftime("%b %d, %Y"),
            "clarity": get_val(results[0], {"clarity_score": 0, "wpm": 0}),
            "vocal": get_val(results[1], {"avg_pitch": 0, "delivery_status": "Neutral"}),
            "interaction": get_val(results[2], {"interaction_ratio_percent": 0}),
            "video": get_val(results[3], {"eye_contact_score": 0, "gesture_energy_score": 0})
        }
        
        # Calculate Overall Score
        scores = [
            data["clarity"].get("clarity_score", 0),
            data["interaction"].get("interaction_ratio_percent", 0) * 2,
            data["video"].get("eye_contact_score", 0),
            min(data["video"].get("gesture_energy_score", 0) / 10, 100)
        ]
        data["overall_score"] = int(sum(scores) / len(scores))
        
        # Comparison Logic
        history = get_json(JSON_FILE, [])
        prev = history[-1] if history else {"overall_score": 60} # Default baseline
        
        data["comparison"] = {
            "overall_diff": data["overall_score"] - prev.get("overall_score", 0),
            "clarity_diff": data["clarity"].get("clarity_score", 0) - prev.get("clarity", {}).get("clarity_score", 0),
            "interaction_diff": data["interaction"].get("interaction_ratio_percent", 0) - prev.get("interaction", {}).get("interaction_ratio_percent", 0),
            "energy_diff": 0
        }
        
        # Add Graph Data
        graph_scores = [entry.get("overall_score", 0) for entry in history]
        graph_scores.append(data["overall_score"])
        data["history_scores"] = graph_scores

        # Save to History
        if "_id" in data: del data["_id"]
        if "history_scores" in data: del data["history_scores"] # Don't save graph array to file
        history.append(data)
        save_json(JSON_FILE, history)

        # Restore Graph Data for Frontend
        data["history_scores"] = graph_scores
        
        return data

    finally:
        # Cleanup
        for p in [save_path, vid_path, aud_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.post("/generate_pdf")
async def pdf_endpoint(data: dict):
    path = "TIE_Report.pdf"
    pdf_engine.generate_report(data, path)
    return FileResponse(path, filename="TIE_Analysis.pdf")