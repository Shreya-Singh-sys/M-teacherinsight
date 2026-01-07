from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from coach_engine import CoachEngine
import shutil, os, json, asyncio, subprocess
from pathlib import Path
from datetime import datetime

# ==================================================
# Azure App Service Entry (FastAPI)
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
INPUT_DIR.mkdir(exist_ok=True)

JSON_FILE = BASE_DIR / "session_history.json"
USERS_FILE = BASE_DIR / "users.json"
CONFIG_FILE = BASE_DIR / "user_config.json"

# --- Import Engines (Local ML, Cloud-ready design) ---
from pdf_engine import PDFGenerator
from content_engine import ContentEngine
from vocal_engine import VocalEngine
from interaction_engine import InteractionEngine
from video_engine import VideoEngine

pdf_engine = PDFGenerator()
content_engine = ContentEngine()
vocal_engine = VocalEngine()
interaction_engine = InteractionEngine()
video_engine = VideoEngine()
coach_engine = CoachEngine()

app = FastAPI(title="Teacher Insight Engine – Azure Edition")

# --- Startup file safety (important for cloud containers) ---
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# --- CORS (Web App + Azure Frontend safe) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Frontend Hosting (Azure App Service static support) ---
app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")

# ==================================================
# DATA MODELS
# ==================================================
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

# ==================================================
# HELPERS
# ==================================================
def get_json(filename, default_val):
    if not os.path.exists(filename): return default_val
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return default_val

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# ==================================================
# ROUTES – FRONTEND
# ==================================================
@app.get("/")
async def read_root():
    return FileResponse(BASE_DIR / "frontend/index.html")

@app.get("/login")
@app.get("/login.html")
async def read_login():
    return FileResponse(BASE_DIR / "frontend/login.html")

@app.get("/register")
@app.get("/register.html")
async def read_register():
    return FileResponse(BASE_DIR / "frontend/register.html")

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

# ==================================================
# AUTH + SETTINGS
# ==================================================
@app.post("/api/register")
async def register_endpoint(user: RegisterModel):
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
    return {"status": "success"}

@app.post("/api/login")
async def login_endpoint(creds: LoginModel):
    users = get_json(USERS_FILE, {})
    if creds.email not in users or users[creds.email]["password"] != creds.password:
        return {"status": "error"}
    return {"status": "success", "user": users[creds.email]}

@app.get("/api/settings")
async def get_settings():
    return get_json(CONFIG_FILE, {})

@app.post("/api/settings/update")
async def update_settings(config: SettingsModel):
    save_json(CONFIG_FILE, config.dict())
    return {"status": "success"}

# ==================================================
# ANALYSIS PIPELINE (Multi-Modal AI)
# ==================================================
def optimize_files(input_path: Path):
    filename = input_path.stem
    fast_video = INPUT_DIR / f"{filename}_fast.mp4"
    fast_audio = INPUT_DIR / f"{filename}_fast.wav"
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(input_path), '-ss', '0', '-t', '45',
             '-vf', 'scale=480:-2', '-r', '15', '-preset', 'ultrafast', str(fast_video)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(fast_video), '-ac', '1', '-ar', '16000', str(fast_audio)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        return str(fast_video), str(fast_audio)
    except:
        return str(input_path), str(input_path)

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    save_path = INPUT_DIR / file.filename.replace(" ", "_")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    vid_path, aud_path = optimize_files(save_path)

    try:
        tasks = [
            asyncio.to_thread(content_engine.transcribe, aud_path),
            asyncio.to_thread(vocal_engine.analyze, aud_path),
            asyncio.to_thread(interaction_engine.analyze, aud_path),
            asyncio.to_thread(video_engine.analyze, vid_path)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        data = {
            "timestamp": datetime.now().strftime("%b %d, %Y"),
            "clarity": results[0],
            "vocal": results[1],
            "interaction": results[2],
            "video": results[3],
        }

        history = get_json(JSON_FILE, [])
        history.append(data)
        save_json(JSON_FILE, history)
        return data

    finally:
        for p in [save_path, vid_path, aud_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.post("/coach")
async def coach_endpoint(req: CoachRequest):
    reply = coach_engine.generate_feedback(req.analysis_data, req.user_query)
    return {"reply": reply}

@app.post("/generate_pdf")
async def pdf_endpoint(data: dict):
    path = "TIE_Report.pdf"
    pdf_engine.generate_report(data, path)
    return FileResponse(path, filename="TIE_Analysis.pdf")

