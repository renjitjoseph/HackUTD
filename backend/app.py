from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import os
import pickle
import numpy as np
from deepface import DeepFace
import json
import base64
import time
import random
import string
import re
import speech_recognition as sr
import threading
from queue import Queue

app = Flask(__name__)
CORS(app)

class FaceRecognitionAPI:
    def __init__(self, database_path="face_database", encodings_file="face_encodings.pkl"):
        self.database_path = database_path
        self.encodings_file = encodings_file
        self.known_faces = {}
        self.model_name = "Facenet"
        self.recognition_threshold = 10.0
        self.new_face_cooldown = {}
        self.cooldown_duration = 5
        
        # Create database directory if it doesn't exist
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        # Load known faces
        self.load_encodings()
        
        # Video capture
        self.cap = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.last_recognition = {}
        self.frame_count = 0
        self.process_every_n_frames = 15
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = sr.Microphone(device_index=None)
        self.listening = False
        self.transcription_queue = Queue()
        self.speech_thread = None
    
    def load_encodings(self):
        """Load pre-computed face encodings from file"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                self.known_faces = pickle.load(f)
            print(f"Loaded {len(self.known_faces)} known faces from database")
        else:
            print("No existing face database found.")
            self.known_faces = {}
    
    def generate_random_name(self):
        """Generate a random name for unknown faces"""
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        name = f"Person_{random_id}"
        
        while name in self.known_faces:
            random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            name = f"Person_{random_id}"
        
        return name
    
    def register_new_face(self, face_img, face_position):
        """Automatically register a new face with a random name"""
        try:
            name = self.generate_random_name()
            
            print(f"\n[NEW FACE DETECTED] Registering as: {name}")
            
            embedding = DeepFace.represent(face_img, model_name=self.model_name, enforce_detection=False)[0]["embedding"]
            
            self.known_faces[name] = embedding
            
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
            
            img_path = os.path.join(self.database_path, f"{name}.jpg")
            cv2.imwrite(img_path, face_img)
            
            print(f"✓ Successfully registered {name}")
            
            return name, embedding
            
        except Exception as e:
            print(f"Error registering new face: {e}")
            return None, None
    
    def update_person_name(self, old_name, new_name):
        """Update a person's name in the database"""
        if old_name not in self.known_faces:
            return False, f"{old_name} not found in database"
        
        if new_name in self.known_faces:
            return False, f"{new_name} already exists in database"
        
        try:
            self.known_faces[new_name] = self.known_faces.pop(old_name)
            
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
            
            old_img_path = os.path.join(self.database_path, f"{old_name}.jpg")
            new_img_path = os.path.join(self.database_path, f"{new_name}.jpg")
            
            if os.path.exists(old_img_path):
                os.rename(old_img_path, new_img_path)
            
            print(f"\n✓ Successfully renamed {old_name} to {new_name}")
            return True, f"Successfully renamed {old_name} to {new_name}"
            
        except Exception as e:
            return False, f"Error updating name: {e}"
    
    def recognize_or_register_face(self, face_img, face_id):
        """Recognize a face or register it if unknown"""
        try:
            embedding = DeepFace.represent(face_img, model_name=self.model_name, enforce_detection=False)[0]["embedding"]
            
            min_distance = float('inf')
            recognized_name = None
            
            for name, known_embedding in self.known_faces.items():
                distance = np.linalg.norm(np.array(embedding) - np.array(known_embedding))
                
                if distance < min_distance:
                    min_distance = distance
                    recognized_name = name
            
            if min_distance < self.recognition_threshold and recognized_name:
                return recognized_name, min_distance, False
            else:
                current_time = time.time()
                
                if face_id in self.new_face_cooldown:
                    last_capture_time = self.new_face_cooldown[face_id]
                    if current_time - last_capture_time < self.cooldown_duration:
                        return "Unknown (processing...)", min_distance, False
                
                new_name, new_embedding = self.register_new_face(face_img, face_id)
                
                if new_name:
                    self.new_face_cooldown[face_id] = current_time
                    return new_name, 0.0, True
                else:
                    return "Unknown", min_distance, False
                
        except Exception as e:
            print(f"Error in recognition: {e}")
            return "Error", float('inf'), False
    
    def get_frame(self):
        """Get a frame from the webcam with face recognition"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        self.frame_count += 1
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        
        # Process faces periodically
        if self.frame_count % self.process_every_n_frames == 0 and len(faces) > 0:
            for i, (x, y, w, h) in enumerate(faces):
                padding = 20
                y1 = max(0, y - padding)
                y2 = min(frame.shape[0], y + h + padding)
                x1 = max(0, x - padding)
                x2 = min(frame.shape[1], x + w + padding)
                face_img = frame[y1:y2, x1:x2]
                
                name, distance, is_new = self.recognize_or_register_face(face_img, i)
                self.last_recognition[i] = (name, distance, is_new)
        
        # Draw rectangles and labels
        for i, (x, y, w, h) in enumerate(faces):
            if i in self.last_recognition:
                name, distance, is_new = self.last_recognition[i]
                
                if is_new:
                    color = (255, 165, 0)  # Orange
                elif distance < self.recognition_threshold:
                    color = (0, 255, 0)  # Green
                else:
                    color = (0, 0, 255)  # Red
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                label = f"{name}"
                if not is_new:
                    label += f" ({distance:.1f})"
                
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x, y-30), (x + text_width, y), color, -1)
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            else:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (128, 128, 128), 2)
        
        info_text = f"Known Faces: {len(self.known_faces)}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def release_camera(self):
        """Release the camera"""
        if self.cap is not None:
            self.cap.release()
    
    def parse_name_from_speech(self, text):
        """Extract names from speech and update database"""
        print(f"[NAME PARSE] Analyzing: '{text}'")
        
        # Patterns to detect name mentions
        patterns = [
            r"(?:this is|that's|thats|meet) ([a-z]+)",
            r"(?:his name is|her name is|their name is|name is) ([a-z]+)",
            r"(?:he's|she's|he is|she is) ([a-z]+)",
            r"(?:call (?:him|her|them)) ([a-z]+)",
        ]
        
        detected_name = None
        matched_pattern = None
        text_lower = text.lower()
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text_lower)
            if match:
                detected_name = match.group(1).capitalize()
                matched_pattern = i + 1
                break
        
        if detected_name:
            print(f"[NAME DETECTED]: {detected_name} (matched pattern #{matched_pattern})")
            
            # Find the most recent Person_XXX to rename
            person_names = [name for name in self.known_faces.keys() if name.startswith("Person_")]
            
            if person_names:
                # Get the most recently added Person_XXX
                most_recent = person_names[-1]
                print(f"[ACTION] Renaming {most_recent} to {detected_name}...")
                success, message = self.update_person_name(most_recent, detected_name)
                if success:
                    print(f"[SUCCESS] {message}")
                else:
                    print(f"[ERROR] {message}")
            else:
                print(f"[INFO] No 'Person_XXX' names found to rename. Current names: {list(self.known_faces.keys())}")
        else:
            print(f"[NAME PARSE] No name pattern matched")
    
    def listen_for_speech(self):
        """Continuously listen for speech and transcribe"""
        print("[SPEECH] Starting speech recognition...")
        try:
            with self.microphone as source:
                print("[SPEECH] Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"[SPEECH] Ready! Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"[SPEECH ERROR] Could not initialize microphone: {e}")
            self.transcription_queue.put({"error": str(e)})
            return
        
        while self.listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                    print("[SPEECH] Audio detected, processing...")
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"[SPEECH] Transcribed: {text}")
                    self.transcription_queue.put({"text": text, "timestamp": time.time()})
                    
                    # Parse for name mentions and auto-rename faces
                    self.parse_name_from_speech(text)
                    
                except sr.UnknownValueError:
                    print("[SPEECH] Could not understand audio")
                except sr.RequestError as e:
                    print(f"[SPEECH ERROR] Recognition error: {e}")
                    self.transcription_queue.put({"error": str(e)})
            except Exception as e:
                if self.listening:
                    print(f"[SPEECH ERROR] Listening error: {e}")
    
    def start_speech_recognition(self):
        """Start speech recognition in background thread"""
        if not self.listening:
            self.listening = True
            self.speech_thread = threading.Thread(target=self.listen_for_speech, daemon=True)
            self.speech_thread.start()
            print("[SPEECH] Speech recognition started")
    
    def stop_speech_recognition(self):
        """Stop speech recognition"""
        self.listening = False
        print("[SPEECH] Speech recognition stopped")

# Initialize the face recognition system
face_system = FaceRecognitionAPI()

def generate_frames():
    """Generate frames for video streaming"""
    while True:
        frame = face_system.get_frame()
        if frame is None:
            continue
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/faces', methods=['GET'])
def get_faces():
    """Get all registered faces"""
    faces = []
    for name in face_system.known_faces.keys():
        img_path = os.path.join(face_system.database_path, f"{name}.jpg")
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                faces.append({
                    'name': name,
                    'image': img_data
                })
        else:
            faces.append({
                'name': name,
                'image': None
            })
    
    return jsonify({
        'faces': faces,
        'count': len(faces)
    })

@app.route('/api/rename', methods=['POST'])
def rename_face():
    """Rename a person in the database"""
    data = request.json
    old_name = data.get('old_name')
    new_name = data.get('new_name')
    
    if not old_name or not new_name:
        return jsonify({'success': False, 'message': 'Missing old_name or new_name'}), 400
    
    success, message = face_system.update_person_name(old_name, new_name)
    
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/delete', methods=['POST'])
def delete_face():
    """Delete a person from the database"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'success': False, 'message': 'Missing name'}), 400
    
    if name not in face_system.known_faces:
        return jsonify({'success': False, 'message': f'{name} not found in database'}), 404
    
    try:
        # Remove from dictionary
        del face_system.known_faces[name]
        
        # Save updated encodings
        with open(face_system.encodings_file, 'wb') as f:
            pickle.dump(face_system.known_faces, f)
        
        # Delete image file
        img_path = os.path.join(face_system.database_path, f"{name}.jpg")
        if os.path.exists(img_path):
            os.remove(img_path)
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {name}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting {name}: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        'total_faces': len(face_system.known_faces),
        'model': face_system.model_name,
        'threshold': face_system.recognition_threshold
    })

@app.route('/api/speech/start', methods=['POST'])
def start_speech():
    """Start speech recognition"""
    face_system.start_speech_recognition()
    return jsonify({'success': True, 'message': 'Speech recognition started'})

@app.route('/api/speech/stop', methods=['POST'])
def stop_speech():
    """Stop speech recognition"""
    face_system.stop_speech_recognition()
    return jsonify({'success': True, 'message': 'Speech recognition stopped'})

@app.route('/api/speech/stream')
def speech_stream():
    """Stream transcribed text using Server-Sent Events"""
    def generate():
        while True:
            if not face_system.transcription_queue.empty():
                data = face_system.transcription_queue.get()
                yield f"data: {json.dumps(data)}\\n\\n"
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
    finally:
        face_system.stop_speech_recognition()
        face_system.release_camera()
