# 🎓 TIE Hacks - AI Teaching Assistant

**TIE (Teacher Insight Engine)** is an AI-powered dashboard designed to help teachers improve their classroom delivery. By analyzing video and audio from class sessions, TIE provides data-driven feedback on clarity, engagement, energy levels, and vocal modulation.




## 🚀 Features

* **📹 Video Analysis:** Upload classroom recordings to get instant feedback.
* **📊 Performance Metrics:** Tracks key metrics like:
    * **Clarity:** Speech rate (WPM) and filler word usage.
    * **Engagement:** Student interaction ratios.
    * **Energy:** Visual gesture frequency and movement analysis.
    * **Vocal Delivery:** Pitch variation and tone analysis.
* **🤖 AI Coach:** Generates personalized, actionable advice based on analysis data (e.g., "Slow down by 10% during complex topics").
* **📈 Progress Tracking:** Visual history of past sessions to monitor improvement over time.
* **🔐 User Authentication:** Secure Login and Registration system with persistent user sessions.
* **⚙️ Custom Settings:** Profile management and theme preferences (Light/Dark mode).

## 🛠️ Tech Stack

* **Frontend:** HTML5, Tailwind CSS, JavaScript (Vanilla)
* **Backend:** Python, FastAPI
* **AI/Processing:** `ffmpeg` (Media processing), Custom Python Engines (`content`, `vocal`, `interaction`, `video`)
* **Data Storage:** JSON (File-based storage for demo purposes)

  ⚡ Getting Started
Prerequisites
Python 3.8+ installed.

FFmpeg installed and added to your system PATH (required for video processing).

Installation
Clone the repository:

Bash

git clone https://github.com/bhargavibhadani-gif/TIE_SQUAD_

cd tie-hacks

Create a virtual environment (optional but recommended):

Bash

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
Install dependencies:

Bash

pip install -r requirements.txt
Run the Server:

Bash

uvicorn main:app --reload
Open in Browser: Go to http://127.0.0.1:8000 to see the Landing Page.

📝 Usage Guide
Sign Up: Create a new account on the Register page.

Dashboard: Log in to view your main stats.

Analyze: Upload a video file (.mp4) via the dashboard. Wait for the AI engines to process the content.

Review: Click "Performance Overview" to see detailed graphs and the AI Coach's advice.

History: Check "Class Sessions" to see a list of all your past uploads.

🔮 Future Improvements
Integration with MongoDB for robust database management.

Real-time live streaming analysis.

PDF Report generation improvements.

More advanced emotion recognition models.


## 📂 Project Structure

```bash
TIE_New/
├── main.py                 # FastAPI Backend & API Routes
├── users.json              # User credentials storage
├── session_history.json    # Analysis data storage
├── user_config.json        # User settings (theme, profile)
├── requirements.txt        # Python dependencies
├── input/                  # Temp folder for uploaded videos
└── frontend/               # Frontend UI
    ├── index.html          # Landing Page
    ├── login.html          # Login Page
    ├── register.html       # Sign-up Page
    ├── dashboard.html      # Main Dashboard
    ├── performance.html    # Detailed Analysis View
    ├── Session.html        # History/List View
    └── settings.html       # User Settings




