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
            print(f"❌ Error: Could not open video file at {video_path}")
            return {"error": "Could not open video file"}

        eye_contact_frames = 0
        total_analyzed_frames = 0
        wrist_movement_energy = []
        prev_wrist_y = None

        # Safely read FPS
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps is None or fps == 0 or np.isnan(fps):
            fps = 30.0

        # process approximately 1 frame every 2 seconds (configurable)
        frame_interval = max(1, int(fps * 2))

        print(f"ℹ️ Video FPS: {fps:.1f}. Processing 1 frame every {frame_interval} frames (~every 2 seconds).")

        frame_count = 0
        last_progress_time = time.time()

        # main loop
        while True:
            success, image = cap.read()
            if not success:
                # End of video or read error
                break

            frame_count += 1

            # progress indicator (every ~5 seconds)
            if time.time() - last_progress_time > 5:
                print(f"   ...scanned {frame_count} frames so far...")
                last_progress_time = time.time()

            # skip frames to speed up processing
            if frame_count % frame_interval != 0:
                continue

            total_analyzed_frames += 1

            try:
                # process frame
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Face mesh for eye contact
                face_results = self.face_mesh.process(image_rgb)
                if face_results.multi_face_landmarks:
                    # For each face (we use first)
                    face_landmarks = face_results.multi_face_landmarks[0]
                    if len(face_landmarks.landmark) > 362:
                        nose_tip = face_landmarks.landmark[4]
                        left_eye = face_landmarks.landmark[133]
                        right_eye = face_landmarks.landmark[362]
                        # Basic heuristic: if nose x inside eye x range => facing camera
                        if (left_eye.x < nose_tip.x < right_eye.x):
                            eye_contact_frames += 1
                    else:
                        # fallback: if any face detected count as eye-contact-ish
                        eye_contact_frames += 1

                # Pose for gesture energy
                pose_results = self.pose.process(image_rgb)
                if pose_results.pose_landmarks:
                    lm = pose_results.pose_landmarks.landmark
                    # MediaPipe pose uses indices; wrists are 15 (left) and 16 (right)
                    if len(lm) > 16:
                        left_wrist = lm[15]
                        right_wrist = lm[16]
                        current_wrist_y = (left_wrist.y + right_wrist.y) / 2.0
                        if prev_wrist_y is not None:
                            movement = abs(current_wrist_y - prev_wrist_y)
                            wrist_movement_energy.append(movement)
                        prev_wrist_y = current_wrist_y

            except Exception as e:
                print(f"⚠️ Warning: Error processing frame {frame_count}: {e}")
                # continue processing remaining frames

        cap.release()
        print("🎉 Video Analysis Complete.")

        # final metrics
        eye_contact_ratio = 0.0
        if total_analyzed_frames > 0:
            eye_contact_ratio = (eye_contact_frames / total_analyzed_frames) * 100.0

        gesture_score = 0.0
        if len(wrist_movement_energy) > 0:
            # energy aggregated and scaled to a friendly range
            gesture_score = float(np.sum(wrist_movement_energy) * 100.0)

        # feedback text
        if eye_contact_ratio > 70:
            eye_feedback = "Excellent connection with the camera."
        elif eye_contact_ratio < 30:
            eye_feedback = "Low Eye Contact. Look at the lens, not your screen."
        else:
            eye_feedback = "Good, but try to maintain gaze longer."

        if gesture_score < 5:
            body_feedback = "Stiff Body Language. Use hand gestures to explain."
        else:
            body_feedback = "Good use of gestures."

        return {
            "eye_contact_score": round(eye_contact_ratio, 1),
            "gesture_energy_score": round(gesture_score, 1),
            "eye_feedback": eye_feedback,
            "body_feedback": body_feedback,
            "frames_analyzed": total_analyzed_frames
        }
