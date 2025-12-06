import cv2
import mediapipe as mp
import numpy as np
import time

class VideoAnalyzer:
    def __init__(self):
        print("👁️ Initializing AI-Eyes (MediaPipe)...")
        self.mp_face_mesh = mp.solutions.face_mesh
        # Use static_image_mode=False for video, refine_landmarks optional
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def analyze_video(self, video_path):
        print(f"📷 Processing Video: {video_path}...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Could not open video file"}

        # Metrics Storage
        eye_contact_frames = 0
        total_analyzed_frames = 0
        wrist_movement_energy = []
        prev_wrist_y = None
        
        # --- OPTIMIZATION SETTINGS ---
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0: fps = 30 # Fallback
        
        # SKIP LOGIC: Process only 1 frame every 1 second
        frame_skip = int(fps) 
        frame_count = 0
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            frame_count += 1
            
            # --- THE SPEED TRICK ---
            # If this is not the "1st second" frame, skip it immediately
            if frame_count % frame_skip != 0:
                continue

            # Resize image to low res (640x480) for faster AI processing
            image = cv2.resize(image, (640, 480))
            
            total_analyzed_frames += 1
            
            # Convert BGR (OpenCV) to RGB (MediaPipe)
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # ... (Rest of your MediaPipe logic stays exactly the same) ...
            
            # --- 1. FACE ANALYSIS ---
            face_results = self.face_mesh.process(image_rgb)
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    nose_tip = face_landmarks.landmark[4]
                    left_eye = face_landmarks.landmark[133]
                    right_eye = face_landmarks.landmark[362]
                    if (left_eye.x < nose_tip.x < right_eye.x):
                        eye_contact_frames += 1

            # --- 2. BODY ANALYSIS ---
            pose_results = self.pose.process(image_rgb)
            if pose_results.pose_landmarks:
                left_wrist = pose_results.pose_landmarks.landmark[15]
                right_wrist = pose_results.pose_landmarks.landmark[16]
                current_wrist_y = (left_wrist.y + right_wrist.y) / 2
                if prev_wrist_y is not None:
                    movement = abs(current_wrist_y - prev_wrist_y)
                    wrist_movement_energy.append(movement)
                prev_wrist_y = current_wrist_y

        cap.release()
        
        # --- FINAL CALCULATIONS ---
        if total_analyzed_frames > 0:
            eye_contact_ratio = (eye_contact_frames / total_analyzed_frames) * 100
        else:
            eye_contact_ratio = 0

        if len(wrist_movement_energy) > 0:
            gesture_score = np.sum(wrist_movement_energy) * 100 
        else:
            gesture_score = 0

        # Simple Feedback Logic
        eye_feedback = "Good eye contact" if eye_contact_ratio > 50 else "Low eye contact"
        body_feedback = "Active gestures" if gesture_score > 5 else "Stiff body language"

        return {
            "eye_contact_score": round(eye_contact_ratio, 1),
            "gesture_energy_score": round(gesture_score, 1),
            "eye_feedback": eye_feedback,
            "body_feedback": body_feedback,
            "frames_analyzed": total_analyzed_frames
        }
