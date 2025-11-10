import cv2
import os
import pickle
import numpy as np
from deepface import DeepFace
import time
import random
import string
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UnifiedFaceSystem:
    def __init__(self, database_path="face_database", encodings_file="face_encodings.pkl", enable_supabase=True):
        self.database_path = database_path
        self.encodings_file = encodings_file
        self.known_faces = {}
        self.model_name = "Facenet"
        self.recognition_threshold = 8.0  # Lowered to prevent false matches
        self.new_face_cooldown = {}  # Track when we last saw unknown faces
        self.cooldown_duration = 3  # Reduced from 5 to 3 seconds

        # Supabase integration
        self.supabase = None
        if enable_supabase:
            try:
                supabase_url = os.getenv('SUPABASE_URL', 'https://xmyjprtuztwqqovonrzb.supabase.co')
                supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhteWpwcnR1enR3cXFvdm9ucnpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2NTY2NTQsImV4cCI6MjA3ODIzMjY1NH0.sC1hue1SeB5iJJypKKkVHcQ5Gup7ckKX-yP79tUN9Ek')
                self.supabase = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️  Supabase initialization failed: {e}")
                self.supabase = None

        # Customer locking for active_session tracking
        self.locked_customer_id = None
        self.customer_lock_time = None
        self.lock_duration = 2.0  # 2 seconds of stable detection before locking
        self.last_face_seen_time = None  # Track when we last saw any face
        self.no_face_timeout = 10.0  # Unlock customer if no face for 10 seconds

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
            print("No existing face database found. Will auto-register new faces.")
            self.known_faces = {}
    
    def generate_random_name(self):
        """Generate a random name for unknown faces"""
        # Generate a name like "Person_ABC123"
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        name = f"Person_{random_id}"
        
        # Make sure it's unique
        while name in self.known_faces:
            random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            name = f"Person_{random_id}"
        
        return name
    
    def register_new_face(self, face_img, face_position):
        """Automatically register a new face with a random name"""
        try:
            # Generate random name
            name = self.generate_random_name()

            print(f"\n[NEW FACE DETECTED] Registering as: {name}")

            # Get face embedding
            embedding = DeepFace.represent(face_img, model_name=self.model_name, enforce_detection=False)[0]["embedding"]

            # Save to database
            self.known_faces[name] = embedding

            # Save encodings to file
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_faces, f)

            # Save face image
            img_path = os.path.join(self.database_path, f"{name}.jpg")
            cv2.imwrite(img_path, face_img)

            # Upload to Supabase
            if self.supabase:
                try:
                    self.supabase.table('customers').upsert({
                        'customer_id': name,
                        'name': name,
                        'personal_details': [],
                        'professional_details': [],
                        'sales_context': []
                    }).execute()
                    print(f"  ✅ Uploaded to Supabase")
                except Exception as e:
                    print(f"  ⚠️  Supabase upload failed: {e}")

            print(f"✓ Successfully registered {name}")
            print(f"  Total faces in database: {len(self.known_faces)}")

            return name, embedding

        except Exception as e:
            print(f"Error registering new face: {e}")
            return None, None
    
    
    def recognize_or_register_face(self, face_img, face_id):
        """Recognize a face or register it if unknown"""
        try:
            # Get embedding for the detected face
            embedding = DeepFace.represent(face_img, model_name=self.model_name, enforce_detection=False)[0]["embedding"]
            
            # Compare with known faces
            min_distance = float('inf')
            recognized_name = None
            
            for name, known_embedding in self.known_faces.items():
                # Calculate Euclidean distance
                distance = np.linalg.norm(np.array(embedding) - np.array(known_embedding))
                
                if distance < min_distance:
                    min_distance = distance
                    recognized_name = name
            
            # Check if face is recognized (use higher threshold of 12.0 to prevent duplicate registrations)
            if min_distance < 12.0 and recognized_name:
                # If distance is less than 8.0, it's a confident match
                if min_distance < self.recognition_threshold:
                    return recognized_name, min_distance, False  # Known face
                else:
                    # Between 8.0 and 12.0 - likely the same person but don't register as new
                    return f"{recognized_name} (?)", min_distance, False
            else:
                # Unknown face - check cooldown before registering
                current_time = time.time()
                
                # Use face_id to track cooldown per face position
                if face_id in self.new_face_cooldown:
                    last_capture_time = self.new_face_cooldown[face_id]
                    if current_time - last_capture_time < self.cooldown_duration:
                        return "Unknown (processing...)", min_distance, False
                
                # Register new face
                new_name, new_embedding = self.register_new_face(face_img, face_id)
                
                if new_name:
                    # Update cooldown
                    self.new_face_cooldown[face_id] = current_time
                    return new_name, 0.0, True  # Newly registered
                else:
                    return "Unknown", min_distance, False
                
        except Exception as e:
            print(f"Error in recognition: {e}")
            return "Error", float('inf'), False
    
    def update_active_session(self, customer_id=None, status='active'):
        """Update active_session table in Supabase"""
        if not self.supabase:
            return

        try:
            if status == 'active' and customer_id:
                # Lock customer
                self.supabase.table('active_session').update({
                    'status': 'active',
                    'current_customer_id': customer_id,
                    'confidence_level': 'stable'
                }).eq('id', 1).execute()
                print(f"\n✅ LOCKED CUSTOMER: {customer_id}")
            elif status == 'active':
                # Mark active but no customer yet
                self.supabase.table('active_session').update({
                    'status': 'active',
                    'current_customer_id': None,
                    'confidence_level': 'detecting'
                }).eq('id', 1).execute()
            elif status == 'idle':
                # Clear session
                self.supabase.table('active_session').update({
                    'status': 'idle',
                    'current_customer_id': None,
                    'confidence_level': 'detecting'
                }).eq('id', 1).execute()
        except Exception as e:
            print(f"⚠️  Failed to update active_session: {e}")

    def start_system(self):
        """Start the unified face recognition and registration system"""
        print("\n" + "="*60)
        print("UNIFIED FACE RECOGNITION & AUTO-REGISTRATION SYSTEM")
        print("="*60)
        print(f"Model: {self.model_name}")
        print(f"Known faces: {len(self.known_faces)}")
        print(f"Recognition threshold: {self.recognition_threshold}")
        print("\nSystem will:")
        print("  • Recognize known faces and display their names")
        print("  • Automatically capture and register new faces")
        print("  • Assign random names to new faces")
        print("  • Update active_session for mobile app integration")
        print("  • Gemini will extract names from conversations")
        print("\nPress 'q' to quit\n")

        # Mark session as active
        self.update_active_session(status='active')
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Load face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        frame_count = 0
        process_every_n_frames = 5  # Reduced from 15 to 5 for more frequent processing
        last_recognition = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Rotate frame 90 degrees counter-clockwise
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            frame_count += 1
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with stricter parameters
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=8,  # Higher value = more strict (fewer false positives)
                minSize=(80, 80),  # Minimum face size in pixels
                maxSize=(500, 500)  # Maximum face size to avoid detecting large objects
            )
            
            # Filter faces by aspect ratio (faces should be roughly square)
            valid_faces = []
            for (x, y, w, h) in faces:
                aspect_ratio = w / float(h)
                # Face aspect ratio should be between 0.7 and 1.3 (roughly square)
                if 0.7 <= aspect_ratio <= 1.3:
                    valid_faces.append((x, y, w, h))
            
            faces = valid_faces
            
            # Process faces periodically
            if frame_count % process_every_n_frames == 0 and len(faces) > 0:
                for i, (x, y, w, h) in enumerate(faces):
                    # Extract face region with some padding
                    padding = 20
                    y1 = max(0, y - padding)
                    y2 = min(frame.shape[0], y + h + padding)
                    x1 = max(0, x - padding)
                    x2 = min(frame.shape[1], x + w + padding)
                    face_img = frame[y1:y2, x1:x2]
                    
                    # Verify it's actually a face using DeepFace
                    try:
                        # Quick face verification - if DeepFace can't detect a face, skip it
                        DeepFace.extract_faces(face_img, detector_backend='opencv', enforce_detection=True)
                        # Recognize or register face
                        name, distance, is_new = self.recognize_or_register_face(face_img, i)
                    except:
                        # Not a valid face, skip this detection
                        continue
                    
                    # Store result
                    last_recognition[i] = (name, distance, is_new)

                    # Update last face seen time
                    self.last_face_seen_time = time.time()

                    # Track customer locking (2 seconds of stable detection)
                    clean_name = name.replace(" (?)", "")  # Remove uncertainty marker
                    if distance < 12.0:  # Within recognition range
                        if self.locked_customer_id is None:
                            # No customer locked yet - start tracking
                            if self.customer_lock_time is None:
                                self.customer_lock_time = time.time()
                            elif time.time() - self.customer_lock_time >= self.lock_duration:
                                # Lock achieved after 2 seconds
                                self.locked_customer_id = clean_name
                                self.update_active_session(customer_id=clean_name, status='active')
                                self.customer_lock_time = None
                                print(f"\n🔒 Customer locked and will persist even if they move out of frame")
                        # else: Already locked, keep the lock (persistent locking)

                    # Print to terminal
                    if is_new:
                        print(f"\n[NEW] {name} registered!")
                    else:
                        status = "KNOWN" if distance < self.recognition_threshold else "UNKNOWN"
                        lock_status = f" [LOCKED]" if self.locked_customer_id == clean_name else ""
                        print(f"\r[{status}] {name} (distance: {distance:.2f}){lock_status}    ", end='', flush=True)
            
            # Draw rectangles and labels on frame
            for i, (x, y, w, h) in enumerate(faces):
                if i in last_recognition:
                    name, distance, is_new = last_recognition[i]
                    
                    # Color: Green for known, Blue for newly registered, Red for unknown
                    if is_new:
                        color = (255, 165, 0)  # Orange for new
                    elif distance < self.recognition_threshold:
                        color = (0, 255, 0)  # Green for known
                    else:
                        color = (0, 0, 255)  # Red for unknown
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Label
                    label = f"{name}"
                    if not is_new:
                        label += f" ({distance:.1f})"
                    
                    # Background for text
                    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x, y-30), (x + text_width, y), color, -1)
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                else:
                    # Face detected but not yet processed
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (128, 128, 128), 2)
            
            # Display info on frame
            info_text = f"Known Faces: {len(self.known_faces)} | Press 'q' to quit"
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Unified Face Recognition System', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n\nExiting...")
                break

        # Cleanup
        self.update_active_session(status='idle')  # Clear active session
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nSystem stopped. Total faces in database: {len(self.known_faces)}")

if __name__ == "__main__":
    system = UnifiedFaceSystem()
    system.start_system()
