"""
Face Detection Service for Active Session
Runs alongside sales_call_analyzer to detect and track faces.
Updates active_session table with current customer_id.
"""
import os
import sys
import time
import pickle
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np
from deepface import DeepFace
from supabase import create_client

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class FaceDetectorService:
    def __init__(self, supabase_url, supabase_key, encodings_file="face_encodings.pkl"):
        self.encodings_file = encodings_file
        self.known_faces = {}
        self.model_name = "Facenet"
        self.recognition_threshold = 10.0

        # Supabase client
        self.supabase = create_client(supabase_url, supabase_key)

        # Detection stability tracking
        self.current_detected_face = None
        self.face_detection_start_time = None
        self.stable_detection_duration = 5.0  # 5 seconds required

        # Load known faces
        self.load_encodings()

        # Video capture
        self.cap = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def load_encodings(self):
        """Load pre-computed face encodings from file"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                self.known_faces = pickle.load(f)
            print(f"✅ Loaded {len(self.known_faces)} known faces")
        else:
            print("⚠️  No face encodings found. Register faces first.")

    def recognize_face(self, face_img):
        """Recognize a face using DeepFace"""
        try:
            embedding = DeepFace.represent(
                face_img,
                model_name=self.model_name,
                enforce_detection=False
            )[0]["embedding"]

            min_distance = float('inf')
            recognized_name = None

            for name, known_embedding in self.known_faces.items():
                distance = np.linalg.norm(np.array(embedding) - np.array(known_embedding))

                if distance < min_distance:
                    min_distance = distance
                    recognized_name = name

            if min_distance < self.recognition_threshold and recognized_name:
                return recognized_name, min_distance
            else:
                return None, min_distance

        except Exception as e:
            print(f"Error in recognition: {e}")
            return None, float('inf')

    def update_active_session(self, customer_id):
        """Update active_session with stability check (5 seconds)"""
        current_time = time.time()

        # Check if this is a new face
        if customer_id != self.current_detected_face:
            # New face detected - start tracking
            self.current_detected_face = customer_id
            self.face_detection_start_time = current_time
            print(f"🔍 New face: {customer_id} (tracking...)")

            # Update as "detecting"
            try:
                self.supabase.table('active_session').update({
                    'confidence_level': 'detecting',
                }).eq('id', 1).execute()
            except Exception as e:
                print(f"Error updating: {e}")

            return

        # Same face - check stability
        time_elapsed = current_time - self.face_detection_start_time

        if time_elapsed >= self.stable_detection_duration:
            # Stable for 5 seconds - lock it in
            try:
                result = self.supabase.table('active_session').select('current_customer_id').eq('id', 1).execute()
                current_db_customer = result.data[0]['current_customer_id'] if result.data else None

                if current_db_customer != customer_id:
                    self.supabase.table('active_session').update({
                        'current_customer_id': customer_id,
                        'confidence_level': 'stable',
                    }).eq('id', 1).execute()

                    print(f"✅ LOCKED: {customer_id} (stable for {time_elapsed:.1f}s)")

            except Exception as e:
                print(f"Error locking customer: {e}")

    def run(self):
        """Main detection loop"""
        print("\n" + "="*50)
        print("FACE DETECTOR SERVICE")
        print("="*50)
        print("Monitoring for faces...")
        print("Press Ctrl+C to stop\n")

        # Open camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Could not open webcam")
            return

        frame_count = 0
        process_every_n_frames = 15  # Process every 15th frame (~2 fps)

        try:
            while True:
                # Check if session is still active
                try:
                    result = self.supabase.table('active_session').select('status').eq('id', 1).execute()
                    if result.data and result.data[0]['status'] != 'active':
                        print("⚠️  Session not active, waiting...")
                        time.sleep(2)
                        continue
                except:
                    pass

                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame_count += 1

                # Process periodically
                if frame_count % process_every_n_frames == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(80, 80)
                    )

                    if len(faces) > 0:
                        # Take first face
                        x, y, w, h = faces[0]
                        padding = 20
                        y1 = max(0, y - padding)
                        y2 = min(frame.shape[0], y + h + padding)
                        x1 = max(0, x - padding)
                        x2 = min(frame.shape[1], x + w + padding)
                        face_img = frame[y1:y2, x1:x2]

                        # Recognize
                        customer_id, distance = self.recognize_face(face_img)

                        if customer_id:
                            self.update_active_session(customer_id)
                    else:
                        # No face detected - reset tracking
                        if self.current_detected_face is not None:
                            print("⚠️  No face detected, resetting...")
                            self.current_detected_face = None
                            self.face_detection_start_time = None

                time.sleep(0.05)  # Small delay

        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        finally:
            if self.cap:
                self.cap.release()
            print("✅ Face detector stopped")

if __name__ == "__main__":
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
        sys.exit(1)

    detector = FaceDetectorService(supabase_url, supabase_key)
    detector.run()
