# 🎓 Teacher Insight Engine (TIE)
### *A Coach, Not a Monitor.*

## 📖 Overview
**TIE (Teacher Insight Engine)** is an ethical AI Co-Pilot designed to help educators improve their teaching quality through data-driven self-reflection. Moving "Beyond Test Scores," TIE provides teachers with a **100% private, objective, and asynchronous** tool for growth.

It utilizes a multimodal AI pipeline to analyze classroom recordings and provide unbiased feedback on **Clarity**, **Engagement**, and **Delivery**—without storing raw video data.

---

## 🚀 Key Features (MVP)

### 👂 AI-Ears: The Auditory Pipeline
* **Content Analysis:** Uses **OpenAI Whisper** for robust transcription (accent-agnostic) and **Google Gemini** to detect jargon, filler words, and structural clarity.
* **Vocal Physics:** Uses **LibROSA** to mathematically measure pitch variance (monotone detection), energy levels, and speaking pace.
* **Interaction Tracking:** Uses **Pyannote Audio** for Speaker Diarization to calculate the *Student-to-Teacher Talk Ratio*, ensuring the class is interactive.

### 👁️ AI-Eyes: The Visual Pipeline
* **Privacy-First Vision:** Uses **MediaPipe** (Edge Inference) to extract facial landmarks and skeletal pose data.
* **Engagement Metrics:** Tracks **Eye Contact Ratio** (connection with students) and **Gesture Energy** (body language enthusiasm).
* **Security:** No raw video frames are stored; only numerical vector embeddings are retained.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **AI Models:** OpenAI Whisper, Google Gemini 1.5 Flash, Pyannote 3.1, MediaPipe, LibROSA.
* **Data Processing:** NumPy, FFmpeg.
* **Frameworks:** Torch, OpenCV.

---

## 📂 Project Structure
```text
TIE_Project/
├── input/                  # Place .mp4 or .wav files here for analysis
├── stream1_content.py      # Whisper + Gemini (Clarity & Jargon Analysis)
├── stream2_vocal.py        # LibROSA (Pitch & Energy Analysis)
├── stream3_interaction.py  # Pyannote (Speaker Diarization)
├── stream4_video.py        # MediaPipe (Eye Contact & Gestures)
├── main.py                 # Fusion Engine (Runs all streams together)
├── requirements.txt        # Project dependencies
└── .env                    # API Keys (Google & HuggingFace)

