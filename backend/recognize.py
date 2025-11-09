import cv2
import os
import pickle
import numpy as np
from deepface import DeepFace
import time

class FaceRecognizer:
    def __init__(self, database_path="face_database", encodings_file="face_encodings.pkl"):
        self.database_path = database_path
        self.encodings_file = encodings_file
        self.known_faces = {}
        self.model_name = "Facenet"  # Fast and accurate model
        
        # Create database directory if it doesn't exist
        if not os.path.exists(database_path):
            os.makedirs(database_path)
            print(f"Created database directory: {database_path}")
        
        # Load known faces
        self.load_encodings()
    
    def load_encodings(self):
        """Load pre-computed face encodings from file"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                self.known_faces = pickle.load(f)
            print(f"Loaded {len(self.known_faces)} known faces from database")
        else:
            print("No existing face database found. Use register.py to add faces.")
    
    def recognize_face(self, face_img):
        """Recognize a face using DeepFace"""
        try:
            # Get embedding for the detected face
            embedding = DeepFace.represent(face_img, model_name=self.model_name, enforce_detection=False)[0]["embedding"]
            
            # Compare with known faces
            min_distance = float('inf')
            recognized_name = "Unknown"
            
            for name, known_embedding in self.known_faces.items():
                # Calculate Euclidean distance
                distance = np.linalg.norm(np.array(embedding) - np.array(known_embedding))
                
                if distance < min_distance:
                    min_distance = distance
                    recognized_name = name
            
            # Threshold for recognition (adjust based on testing)
            threshold = 10.0  # Lower = stricter matching
            
            if min_distance < threshold:
                return recognized_name, min_distance
            else:
                return "Unknown", min_distance
                
        except Exception as e:
            return "Unknown", float('inf')
    
    def start_recognition(self):
        """Start real-time face recognition from webcam"""
        print("\n" + "="*50)
        print("FACIAL RECOGNITION SYSTEM")
        print("="*50)
        print(f"Model: {self.model_name}")
        print(f"Known faces: {len(self.known_faces)}")
        print("Press 'q' to quit\n")
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Load face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        frame_count = 0
        process_every_n_frames = 10  # Process every 10th frame for better performance
        last_recognition = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            frame_count += 1
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
            
            # Process faces
            if frame_count % process_every_n_frames == 0 and len(faces) > 0:
                for i, (x, y, w, h) in enumerate(faces):
                    # Extract face region
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Recognize face
                    name, distance = self.recognize_face(face_img)
                    
                    # Store result
                    last_recognition[i] = (name, distance)
                    
                    # Print to terminal
                    print(f"\r[DETECTED] {name} (confidence: {distance:.2f})    ", end='', flush=True)
            
            # Draw rectangles and labels on frame
            for i, (x, y, w, h) in enumerate(faces):
                color = (0, 255, 0) if i in last_recognition and last_recognition[i][0] != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                if i in last_recognition:
                    name, distance = last_recognition[i]
                    label = f"{name} ({distance:.1f})"
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Display frame
            cv2.imshow('Facial Recognition', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n\nExiting...")
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam closed.")

if __name__ == "__main__":
    recognizer = FaceRecognizer()
    recognizer.start_recognition()
