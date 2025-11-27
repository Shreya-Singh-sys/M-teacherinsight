import os
import json
import subprocess
from pathlib import Path
from stream1_content import ContentAnalyzer
from stream2_vocal import VocalAnalyzer
from stream3_interaction import InteractionAnalyzer
from stream4_video import VideoAnalyzer

INPUT_DIR = Path("input")
INPUT_DIR.mkdir(exist_ok=True)

def ensure_wav(audio_path: Path) -> Path:
    """
    If input is mp3, try to convert to wav using ffmpeg.
    If conversion fails, return the original path and let vocal analyzer decide.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if audio_path.suffix.lower() in [".wav"]:
        return audio_path

    # try to convert mp3 -> wav
    wav_path = audio_path.with_suffix(".wav")
    try:
        cmd = ["ffmpeg", "-y", "-i", str(audio_path), str(wav_path)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Converted {audio_path.name} -> {wav_path.name}")
        return wav_path
    except Exception:
        print("⚠️ ffmpeg conversion failed or not installed. Proceeding with original file.")
        return audio_path

def safe_json_load(s):
    try:
        return json.loads(s) if isinstance(s, str) else (s or {})
    except Exception:
        return {}

def main():
    print("\n🚀 INITIALIZING TIE ENGINE\n")

    # Files (change names as required)
    audio_file = INPUT_DIR / "convo.mp3"   # your source file
    video_file = INPUT_DIR / "convo.mp4"   # your video file (must be a video)

    # Ensure audio is WAV if possible
    try:
        audio_for_analysis = ensure_wav(audio_file)
    except FileNotFoundError as e:
        print(e)
        return

    # Initialize analyzers
    content = ContentAnalyzer()
    vocal = VocalAnalyzer()
    interaction = InteractionAnalyzer()
    video = VideoAnalyzer()

    # 1) Content (Whisper + Gemini)
    print("\n[1/4] 📘 Content Analysis")
    try:
        transcript = content.transcribe_audio(str(audio_for_analysis))
    except Exception as e:
        print("Content analysis error:", e)
        transcript = ""
    print(transcript)

    clarity_raw = "{}"
    try:
        clarity_raw = content.analyze_clarity(transcript)
    except Exception as e:
        print("Content clarity error:", e)

    clarity = safe_json_load(clarity_raw)

    # 2) Vocal (Librosa)
    print("\n[2/4] 🎧 Vocal Analysis")
    try:
        vocal_data = vocal.analyze_audio(str(audio_for_analysis))
    except Exception as e:
        print("Vocal analysis error:", e)
        vocal_data = {"error": "vocal analysis failed"}
    print("\n[3/4] 🗣️ Interaction Analysis")
    try:
        interaction_data = interaction.analyze_interaction(str(audio_for_analysis))
    except Exception as e:
        print("Interaction analysis error:", e)
        interaction_data = {"error": "interaction analysis failed"}

    # 4) Video (MediaPipe)
    print("\n[4/4] 📷 Video Analysis")
    if Path(video_file).exists():
        try:
            video_data = video.analyze_video(str(video_file))
        except Exception as e:
            print("Video analysis error:", e)
            video_data = {"error": "video analysis failed"}
    else:
        print("No video file found. Skipping video analysis.")
        video_data = {}

    # Final combined report
    print("\n\n===== 🟩 FINAL TEACHER PERFORMANCE REPORT =====")
    print(f"Clarity Score: {clarity.get('clarity_score', 'N/A')}")
    print(f"Clarity Feedback: {clarity.get('feedback', 'N/A')}")
    print(f"Vocal Delivery: {vocal_data.get('delivery_status', vocal_data.get('error', 'N/A'))}")
    print(f"Vocal Avg Pitch: {vocal_data.get('avg_pitch', 'N/A')}")
    print(f"Student Interaction %: {interaction_data.get('interaction_ratio_percent', interaction_data.get('error', 'N/A'))}")
    print(f"Class Mode: {interaction_data.get('class_mode', 'N/A')}")
    print(f"Eye Contact Score: {video_data.get('eye_contact_score', 'N/A')}")
    print(f"Gesture Energy Score: {video_data.get('gesture_energy_score', 'N/A')}")
    print("\nEvaluation Complete.\n")

if __name__ == "__main__":
    main()
