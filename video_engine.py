import cv2
import numpy as np

# ==================================================
# Vision Analysis Engine
# ==================================================
# Current: MediaPipe (local CV)
# Azure-ready: Can be extended using Azure AI Vision
# ==================================================

# --- SAFETY BLOCK: Handle Broken MediaPipe on Python 3.12 ---
try:
    import mediapipe as mp
    mp_available = True
    print("✅ MediaPipe Library Loaded Successfully.")
except ImportError:
    mp_available = False
    print("⚠️ MediaPipe Library NOT found. Using Backup Mode.")
except AttributeError:
    mp_available = False
    print("⚠️ MediaPipe Incompatible (Python 3.12 Error). Using Backup Mode.")

class VideoEngine:
    def __init__(self):
        self.active = False

        if mp_available:
            try:
                # Initialize MediaPipe solutions
                self.mp_face = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)
                self.mp_pose = mp.solutions.pose.Pose()
                self.active = True
                print("👁️ Vision AI Engine: ONLINE")
            except AttributeError:
                print("⚠️ Vision AI Engine: OFFLINE (Library Error).")
                self.active = False
        else:
            print("⚠️ Vision AI Engine: OFFLINE (Missing Library).")

    def analyze(self, video_path):
        """
        Analyzes teacher's eye contact and gesture energy from video.
        Falls back to safe mock scores if vision AI is unavailable.
        """

        # 1. Safe fallback (prevents crash on cloud / container)
        if not self.active:
            print("⚠️ Skipping detailed vision analysis (Using Fallback Data)")
            return {
                "eye_contact_score": 75,    # Default "Good"
                "gesture_energy_score": 60  # Default "Active"
            }

        # 2. Real MediaPipe-based analysis
        cap = cv2.VideoCapture(video_path)

        frames_analyzed = 0
        eye_contact = 0
        energy_list = []
        prev_y = None

        while cap.isOpened():
            success, img = cap.read()
            if not success:
                break

            frames_analyzed += 1

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img.flags.writeable = False

            # ---- Face / Eye Contact ----
            try:
                res_face = self.mp_face.process(img)
                if res_face.multi_face_landmarks:
                    lm = res_face.multi_face_landmarks[0].landmark
                    # Simple heuristic: nose between eyes
                    if lm[133].x < lm[4].x < lm[362].x:
                        eye_contact += 1
            except Exception:
                pass

            # ---- Body / Gesture Energy ----
            try:
                res_pose = self.mp_pose.process(img)
                if res_pose.pose_landmarks:
                    y = res_pose.pose_landmarks.landmark[15].y
                    if prev_y is not None:
                        energy_list.append(abs(y - prev_y))
                    prev_y = y
            except Exception:
                pass

        cap.release()

        # 3. Score normalization
        score_eye = int((eye_contact / frames_analyzed) * 100) if frames_analyzed else 0
        score_energy = int(min(sum(energy_list) * 500, 100)) if energy_list else 0

        return {
            "eye_contact_score": score_eye,
            "gesture_energy_score": score_energy
        }
