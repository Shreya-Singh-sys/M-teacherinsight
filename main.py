
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from coach_engine import CoachEngine # <-- Add this
import shutil
import os
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent

# Set Directories
INPUT_DIR = BASE_DIR / "input"
INPUT_DIR.mkdir(exist_ok=True)

# Set Files
JSON_FILE = BASE_DIR / "session_history.json"
USERS_FILE = BASE_DIR / "users.json"
CONFIG_FILE = BASE_DIR / "user_config.json"

# Import Engines
from pdf_engine import PDFGenerator
from stream1_content import ContentEngine
from stream2_vocal import VocalEngine
from stream3_interaction import InteractionEngine
from stream4_video import VideoEngine
# Initialize Engines
pdf_engine = PDFGenerator()
content_engine = ContentEngine()
vocal_engine = VocalEngine()
interaction_engine = InteractionEngine()
video_engine = VideoEngine()
coach_engine = CoachEngine() # <-- Add this

app = FastAPI()

# --- STARTUP CHECK: FORCE CREATE FILES ---
# This runs once when server starts to ensure files exist
print("--------------------------------------------------")
print(f"📂 Working Directory: {BASE_DIR}")
print(f"📄 Users File Path:   {USERS_FILE}")

if not os.path.exists(USERS_FILE):
    print("⚠️ users.json not found. Creating it now...")
    with open(USERS_FILE, "w") as f:
        json.dump({}, f) # Create empty JSON object
    print("✅ users.json created successfully!")
else:
    print("✅ users.json found.")
print("--------------------------------------------------")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Frontend
app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")

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

# 1. Root / Landing Page (FIXED PATH)
@app.get("/")
async def read_root():
    # Points to frontend/index.html now
    return FileResponse(BASE_DIR / "index.html")

# 2. Auth Pages
# @app.get("/login")
# async def read_login():
#     return FileResponse(BASE_DIR / "frontend/login.html")

# @app.get("/register")
# async def read_register():
#     return FileResponse(BASE_DIR / "frontend/register.html")

# # 3. App Pages
# @app.get("/dashboard")
# async def read_dashboard():
#     return FileResponse(BASE_DIR / "frontend/dashboard.html")

# @app.get("/performance")
# async def read_performance():
#     return FileResponse(BASE_DIR / "frontend/performance.html")

# @app.get("/sessions")
# async def read_sessions():
#     return FileResponse(BASE_DIR / "frontend/Session.html")

# @app.get("/settings")
# async def read_settings():
#     return FileResponse(BASE_DIR / "frontend/settings.html")
# --- ROUTES: PAGES ---

# 1. Root / Landing Page
# --- ROUTES: PAGES ---

# 1. Root / Landing Page
@app.get("/")
async def read_root():
    return FileResponse(BASE_DIR / "frontend/index.html")

# 2. Authentication Pages (Double decorators to support both links)
@app.get("/login")
@app.get("/login.html")
async def read_login():
    return FileResponse(BASE_DIR / "frontend/login.html")

@app.get("/register")
@app.get("/register.html")
async def read_register():
    return FileResponse(BASE_DIR / "frontend/register.html")

# 3. App Pages
@app.get("/dashboard")
@app.get("/dashboard.html")
async def read_dashboard():
    return FileResponse(BASE_DIR / "frontend/dashboard.html")

@app.get("/performance")
@app.get("/performance.html")
async def read_performance():
    return FileResponse(BASE_DIR / "frontend/performance.html")

@app.get("/sessions")
@app.get("/Session.html") 
async def read_sessions():
    return FileResponse(BASE_DIR / "frontend/Session.html")

@app.get("/settings")
@app.get("/settings.html")
async def read_settings():
    return FileResponse(BASE_DIR / "frontend/settings.html")

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
    print(f"✅ SAVED to {USERS_FILE}")  # Debug print
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
    return history[::-1]

@app.get("/api/latest-session")
async def get_latest():
    history = get_json(JSON_FILE, [])
    return history[-1] if history else {"error": "No data"}

@app.post("/coach")
async def coach_endpoint(req: CoachRequest):
    # Use the CoachEngine to generate smart feedback
    reply = coach_engine.generate_feedback(req.analysis_data, req.user_query)
    return {"reply": reply}

# --- MAIN ANALYSIS ENGINE ---
def optimize_files(input_path: Path):
    filename_no_ext = input_path.stem
    fast_video = INPUT_DIR / f"{filename_no_ext}_fast.mp4"
    fast_audio = INPUT_DIR / f"{filename_no_ext}_fast.wav"
    try:
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
        
        scores = [
            data["clarity"].get("clarity_score", 0),
            data["interaction"].get("interaction_ratio_percent", 0) * 2,
            data["video"].get("eye_contact_score", 0),
            min(data["video"].get("gesture_energy_score", 0) / 10, 100)
        ]
        data["overall_score"] = int(sum(scores) / len(scores))
        
        history = get_json(JSON_FILE, [])
        prev = history[-1] if history else {"overall_score": 60}
        
        data["comparison"] = {
            "overall_diff": data["overall_score"] - prev.get("overall_score", 0),
            "clarity_diff": data["clarity"].get("clarity_score", 0) - prev.get("clarity", {}).get("clarity_score", 0),
            "interaction_diff": data["interaction"].get("interaction_ratio_percent", 0) - prev.get("interaction", {}).get("interaction_ratio_percent", 0),
            "energy_diff": 0
        }
        
        graph_scores = [entry.get("overall_score", 0) for entry in history]
        graph_scores.append(data["overall_score"])
        data["history_scores"] = graph_scores

        if "_id" in data: del data["_id"]
        if "history_scores" in data: del data["history_scores"]
        history.append(data)
        save_json(JSON_FILE, history)

        data["history_scores"] = graph_scores
        
        return data

    finally:
        for p in [save_path, vid_path, aud_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.post("/generate_pdf")
async def pdf_endpoint(data: dict):
    path = "TIE_Report.pdf"
    pdf_engine.generate_report(data, path)
    return FileResponse(path, filename="TIE_Analysis.pdf")
