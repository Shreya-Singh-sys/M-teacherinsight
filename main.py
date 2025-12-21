# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from pydantic import BaseModel # <--- NEW IMPORT
# import shutil
# import os
# import json
# import asyncio
# import subprocess
# from pathlib import Path
# from datetime import datetime

# # --- CONFIGURATION ---
# INPUT_DIR = Path("input")
# INPUT_DIR.mkdir(exist_ok=True)
# JSON_FILE = "session_history.json"

# # Import Engines
# from pdf_engine import PDFGenerator
# from stream1_content import ContentEngine
# from stream2_vocal import VocalEngine
# from stream3_interaction import InteractionEngine
# from stream4_video import VideoEngine

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Engines
# pdf_engine = PDFGenerator()
# content_engine = ContentEngine()
# vocal_engine = VocalEngine()
# interaction_engine = InteractionEngine()
# video_engine = VideoEngine()

# # --- HELPER: History Manager ---
# def get_history_data():
#     if not os.path.exists(JSON_FILE): return []
#     try:
#         with open(JSON_FILE, "r") as f: return json.load(f)
#     except: return []

# def save_history_data(data):
#     history = get_history_data()
#     if "_id" in data: del data["_id"]
#     history.append(data)
#     with open(JSON_FILE, "w") as f:
#         json.dump(history, f, indent=4)

# MOCK_BASELINE = {
#     "overall_score": 60,
#     "clarity": {"clarity_score": 65, "wpm": 110},
#     "interaction": {"interaction_ratio_percent": 15},
#     "video": {"eye_contact_score": 40, "gesture_energy_score": 40}
# }

# # --- NEW: COACH REQUEST MODEL ---
# class CoachRequest(BaseModel):
#     analysis_data: dict
#     user_query: str

# @app.get("/")
# async def read_root():
#     return FileResponse("index.html")

# # --- NEW: CHATBOT ENDPOINT (Fixes "undefined") ---
# @app.post("/coach")
# async def coach_endpoint(req: CoachRequest):
#     query = req.user_query.lower()
#     data = req.analysis_data
    
#     # 1. Extract Scores safely
#     clarity = data.get("clarity", {}).get("clarity_score", 0)
#     wpm = data.get("clarity", {}).get("wpm", 0)
#     pitch = data.get("vocal", {}).get("avg_pitch", 0)
#     energy = data.get("video", {}).get("gesture_energy_score", 0)
    
#     # 2. Smart Logic (Rule-Based for reliability)
#     reply = ""
    
#     if "voice" in query or "pitch" in query:
#         if pitch < 100:
#             reply = f"Your average pitch was low ({pitch} Hz). Try to vary your intonation to keep students engaged."
#         else:
#             reply = f"Your vocal modulation is good ({pitch} Hz). To improve further, try pausing for 2 seconds after asking a question."
            
#     elif "energy" in query or "gesture" in query:
#         if energy < 50:
#             reply = "Your visual energy score is low. Try standing up or using more hand gestures to emphasize key points."
#         else:
#             reply = "Your energy levels are fantastic! You are creating a very dynamic classroom environment."
            
#     elif "clarity" in query or "fast" in query or "slow" in query:
#         if wpm > 150:
#             reply = f"You are speaking quite fast ({wpm} WPM). Slow down slightly to ensure students can take notes."
#         elif wpm < 110:
#             reply = f"Your pace is a bit slow ({wpm} WPM). Try to pick up the tempo to maintain excitement."
#         else:
#             reply = "Your speaking pace is perfect. Focus on eliminating filler words like 'um' and 'uh'."
            
#     elif "improve" in query:
#         reply = "Based on your data, the best area to improve is Interaction. Try asking open-ended questions every 5 minutes."
        
#     else:
#         # Generic Fallback
#         reply = f"I analyzed your session! Your Overall Score is {data.get('overall_score', 0)}. Ask me specifically about 'Voice', 'Energy', or 'Clarity' for more details."

#     return {"reply": reply}

# # --- OPTIMIZATION ---
# def optimize_files(input_path: Path):
#     filename_no_ext = input_path.stem
#     fast_video = INPUT_DIR / f"{filename_no_ext}_fast.mp4"
#     fast_audio = INPUT_DIR / f"{filename_no_ext}_fast.wav"
#     print(f"⚡ Optimizing: {input_path.name}...")
#     try:
#         cmd_vid = ['ffmpeg', '-y', '-i', str(input_path), '-ss', '0', '-t', '45', '-vf', 'scale=480:-2', '-r', '15', '-c:v', 'libx264', '-preset', 'ultrafast', str(fast_video)]
#         subprocess.run(cmd_vid, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
#         cmd_aud = ['ffmpeg', '-y', '-i', str(fast_video), '-ac', '1', '-ar', '16000', str(fast_audio)]
#         subprocess.run(cmd_aud, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
#         return str(fast_video), str(fast_audio)
#     except subprocess.CalledProcessError:
#         return str(input_path), str(input_path)

# @app.post("/analyze")
# async def analyze_endpoint(file: UploadFile = File(...)):
#     print(f"\n🚀 New Upload: {file.filename}")
#     safe_filename = file.filename.replace(" ", "_")
#     save_path = INPUT_DIR / safe_filename
#     with open(save_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        
#     vid_path, aud_path = optimize_files(save_path)
    
#     try:
#         print("🧠 Running AI Engines...")
#         task1 = asyncio.to_thread(content_engine.transcribe, aud_path)
#         task2 = asyncio.to_thread(vocal_engine.analyze, aud_path)
#         task3 = asyncio.to_thread(interaction_engine.analyze, aud_path)
#         task4 = asyncio.to_thread(video_engine.analyze, vid_path)
        
#         results = await asyncio.gather(task1, task2, task3, task4, return_exceptions=True)

#         def get_res(result, default): return result if not isinstance(result, Exception) else default

#         data = {
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
#             "clarity": get_res(results[0], {"clarity_score": 0, "wpm": 0, "feedback": "Processing Error"}),
#             "vocal": get_res(results[1], {"avg_pitch": 0, "delivery_status": "Neutral"}),
#             "interaction": get_res(results[2], {"interaction_ratio_percent": 0}),
#             "video": get_res(results[3], {"eye_contact_score": 0, "gesture_energy_score": 0})
#         }
        
#         scores = [
#             data["clarity"].get("clarity_score", 0),
#             data["interaction"].get("interaction_ratio_percent", 0) * 2,
#             data["video"].get("eye_contact_score", 0),
#             min(data["video"].get("gesture_energy_score", 0) / 10, 100)
#         ]
#         overall = int(sum(scores) / len(scores))
#         data["overall_score"] = min(overall, 100)
        
#         history = get_history_data()
#         prev = history[-1] if len(history) > 0 else MOCK_BASELINE
#         data["comparison"] = {
#             "overall_diff": data["overall_score"] - prev.get("overall_score", 0),
#             "clarity_diff": data["clarity"].get("clarity_score", 0) - prev.get("clarity", {}).get("clarity_score", 0),
#             "interaction_diff": data["interaction"].get("interaction_ratio_percent", 0) - prev.get("interaction", {}).get("interaction_ratio_percent", 0),
#             "energy_diff": 0
#         }
        
#         save_history_data(data)
#         return data

#     finally:
#         print("🗑️ Cleaning up temp files...")
#         for p in [save_path, vid_path, aud_path]:
#             if os.path.exists(p):
#                 try: os.remove(p)
#                 except: pass

# @app.post("/generate_pdf")
# async def pdf_endpoint(data: dict):
#     path = "TIE_Report.pdf"
#     pdf_engine.generate_report(data, path)
#     return FileResponse(path, filename="TIE_Analysis.pdf")
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles # <--- NEW IMPORT
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

# Import Engines
from pdf_engine import PDFGenerator
from stream1_content import ContentEngine
from stream2_vocal import VocalEngine
from stream3_interaction import InteractionEngine
from stream4_video import VideoEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
pdf_engine = PDFGenerator()
content_engine = ContentEngine()
vocal_engine = VocalEngine()
interaction_engine = InteractionEngine()
video_engine = VideoEngine()

# --- 1. MOUNT THE FRONTEND FOLDER (THE FIX) ---
# This tells Python: "Allow access to any file inside the 'frontend' folder"
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# --- HELPER: History Manager ---
def get_history_data():
    if not os.path.exists(JSON_FILE): return []
    try:
        with open(JSON_FILE, "r") as f: return json.load(f)
    except: return []

def save_history_data(data):
    history = get_history_data()
    if "_id" in data: del data["_id"]
    if "history_scores" in data: del data["history_scores"]
    history.append(data)
    with open(JSON_FILE, "w") as f:
        json.dump(history, f, indent=4)

MOCK_BASELINE = {
    "overall_score": 60,
    "clarity": {"clarity_score": 65, "wpm": 110},
    "interaction": {"interaction_ratio_percent": 15},
    "video": {"eye_contact_score": 40, "gesture_energy_score": 40}
}

class CoachRequest(BaseModel):
    analysis_data: dict
    user_query: str

@app.get("/")
async def read_root():
    return FileResponse("index.html")

# 2. DASHBOARD ROUTE -> Show Dashboard
@app.get("/dashboard")
async def read_dashboard():
    return FileResponse("dashboard.html")

@app.post("/coach")
async def coach_endpoint(req: CoachRequest):
    query = req.user_query.lower()
    data = req.analysis_data
    
    # 1. Extract Scores
    clarity = data.get("clarity", {}).get("clarity_score", 0)
    wpm = data.get("clarity", {}).get("wpm", 0)
    pitch = data.get("vocal", {}).get("avg_pitch", 0)
    energy = data.get("video", {}).get("gesture_energy_score", 0)
    
    # 2. Logic
    reply = ""
    if "voice" in query or "pitch" in query:
        reply = f"Your average pitch was {pitch} Hz. " + ("Try to vary your intonation more." if pitch < 100 else "Good modulation.")
    elif "energy" in query or "gesture" in query:
        reply = "Your visual energy is low. Use more hand gestures." if energy < 50 else "Great dynamic energy!"
    elif "clarity" in query or "fast" in query:
        reply = f"You are speaking at {wpm} WPM. " + ("Slow down slightly." if wpm > 150 else "Pace is good.")
    elif "improve" in query:
        reply = "Focus on student interaction ratios next time."
    else:
        reply = f"I analyzed your session! Your Overall Score is {data.get('overall_score', 0)}."
    return {"reply": reply}

def optimize_files(input_path: Path):
    filename_no_ext = input_path.stem
    fast_video = INPUT_DIR / f"{filename_no_ext}_fast.mp4"
    fast_audio = INPUT_DIR / f"{filename_no_ext}_fast.wav"
    print(f"⚡ Optimizing: {input_path.name}...")
    try:
        cmd_vid = ['ffmpeg', '-y', '-i', str(input_path), '-ss', '0', '-t', '45', '-vf', 'scale=480:-2', '-r', '15', '-c:v', 'libx264', '-preset', 'ultrafast', str(fast_video)]
        subprocess.run(cmd_vid, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        cmd_aud = ['ffmpeg', '-y', '-i', str(fast_video), '-ac', '1', '-ar', '16000', str(fast_audio)]
        subprocess.run(cmd_aud, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return str(fast_video), str(fast_audio)
    except subprocess.CalledProcessError:
        return str(input_path), str(input_path)

# --- NEW: API TO GET LATEST SESSION DATA ---
@app.get("/api/latest-session")
async def get_latest_session():
    history = get_history_data()
    if not history:
        return {"error": "No data found"}
    
    # Return the most recent entry (Last item in the list)
    return history[-1]
# --- ADD THIS TO main.py ---
@app.get("/api/history")
async def get_full_history():
    history = get_history_data()
    # Reverse list so newest shows first
    return history[::-1]

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    print(f"\n🚀 New Upload: {file.filename}")
    safe_filename = file.filename.replace(" ", "_")
    save_path = INPUT_DIR / safe_filename
    with open(save_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        
    vid_path, aud_path = optimize_files(save_path)
    
    try:
        print("🧠 Running AI Engines...")
        task1 = asyncio.to_thread(content_engine.transcribe, aud_path)
        task2 = asyncio.to_thread(vocal_engine.analyze, aud_path)
        task3 = asyncio.to_thread(interaction_engine.analyze, aud_path)
        task4 = asyncio.to_thread(video_engine.analyze, vid_path)
        
        results = await asyncio.gather(task1, task2, task3, task4, return_exceptions=True)

        def get_res(result, default): return result if not isinstance(result, Exception) else default

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "clarity": get_res(results[0], {"clarity_score": 0, "wpm": 0, "feedback": "Processing Error"}),
            "vocal": get_res(results[1], {"avg_pitch": 0, "delivery_status": "Neutral"}),
            "interaction": get_res(results[2], {"interaction_ratio_percent": 0}),
            "video": get_res(results[3], {"eye_contact_score": 0, "gesture_energy_score": 0})
        }
        
        scores = [
            data["clarity"].get("clarity_score", 0),
            data["interaction"].get("interaction_ratio_percent", 0) * 2,
            data["video"].get("eye_contact_score", 0),
            min(data["video"].get("gesture_energy_score", 0) / 10, 100)
        ]
        overall = int(sum(scores) / len(scores))
        data["overall_score"] = min(overall, 100)
        
        save_history_data(data)
        
        full_history = get_history_data()
        graph_scores = [entry.get("overall_score", 0) for entry in full_history]
        data["history_scores"] = graph_scores
        
        prev = full_history[-2] if len(full_history) > 1 else MOCK_BASELINE
        data["comparison"] = {
            "overall_diff": data["overall_score"] - prev.get("overall_score", 0),
            "clarity_diff": data["clarity"].get("clarity_score", 0) - prev.get("clarity", {}).get("clarity_score", 0),
            "interaction_diff": data["interaction"].get("interaction_ratio_percent", 0) - prev.get("interaction", {}).get("interaction_ratio_percent", 0),
            "energy_diff": 0
        }
        
        return data

    finally:
        print("🗑️ Cleaning up temp files...")
        for p in [save_path, vid_path, aud_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.post("/generate_pdf")
async def pdf_endpoint(data: dict):
    path = "TIE_Report.pdf"
    pdf_engine.generate_report(data, path)
    return FileResponse(path, filename="TIE_Analysis.pdf")
# --- SETTINGS CONFIGURATION ---
CONFIG_FILE = "user_config.json"

# Default Settings (if file doesn't exist)
DEFAULT_CONFIG = {
    "name": "Sarah Jenkins",
    "email": "sarah.jenkins@school.edu",
    "theme": "light",
    "notifications": {"email": True, "weekly": True}
}

def get_user_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def save_user_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- API: GET SETTINGS ---
@app.get("/api/settings")
async def get_settings_endpoint():
    return get_user_config()

# --- API: UPDATE SETTINGS ---
class SettingsModel(BaseModel):
    name: str
    email: str
    theme: str

@app.post("/api/settings/update")
async def update_settings_endpoint(config: SettingsModel):
    current = get_user_config()
    # Update fields
    current["name"] = config.name
    current["email"] = config.email
    current["theme"] = config.theme
    
    save_user_config(current)
    return {"status": "success", "message": "Settings updated!", "data": current}
# ... (Keep all your existing imports) ...

# --- USER AUTHENTICATION SYSTEM ---
USERS_FILE = "users.json"

# Helper to load users
def get_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Helper to save users
def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Models
class RegisterModel(BaseModel):
    name: str
    email: str
    password: str

class LoginModel(BaseModel):
    email: str
    password: str

# 1. REGISTER API
@app.post("/api/register")
async def register_endpoint(user: RegisterModel):
    users = get_users()
    
    if user.email in users:
        return {"status": "error", "message": "Email already exists!"}
    
    # Save new user
    users[user.email] = {
        "name": user.name,
        "email": user.email,
        "password": user.password, # Note: In a real app, hash this!
        "joined": datetime.now().strftime("%Y-%m-%d")
    }
    save_users(users)
    return {"status": "success", "message": "Account created!"}

# 2. LOGIN API
@app.post("/api/login")
async def login_endpoint(creds: LoginModel):
    users = get_users()
    
    if creds.email not in users:
        return {"status": "error", "message": "User not found"}
    
    stored_user = users[creds.email]
    
    if stored_user["password"] != creds.password:
        return {"status": "error", "message": "Incorrect password"}
    
    # Return user info (excluding password)
    return {
        "status": "success",
        "user": {
            "name": stored_user["name"],
            "email": stored_user["email"]
        }
    }