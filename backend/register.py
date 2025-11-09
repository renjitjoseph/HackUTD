import cv2
import os
import pickle
from deepface import DeepFace

class FaceRegistration:
    def __init__(self, database_path="face_database", encodings_file="face_encodings.pkl"):
        self.database_path = database_path
        self.encodings_file = encodings_file
        self.model_name = "Facenet"
        
        # Create database directory if it doesn't exist
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        # Load existing encodings
        self.known_faces = {}
        if os.path.exists(encodings_file):
            with open(encodings_file, 'rb') as f:
                self.known_faces = pickle.load(f)
    
    def capture_face(self, name):
        """Capture a face from webcam and register it"""
        print(f"\nRegistering face for: {name}")
        print("Position your face in the frame and press SPACE to capture")
        print("Press 'q' to cancel\n")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return False
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        captured = False
        face_img = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to capture", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('Register Face', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and len(faces) > 0:
                # Capture the first detected face
                x, y, w, h = faces[0]
                face_img = frame[y:y+h, x:x+w]
                captured = True
                print("Face captured!")
                break
            elif key == ord('q'):
                print("Registration cancelled")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured and face_img is not None:
            return self.register_face(name, face_img)
        
        return False
    
    def register_face(self, name, face_img):
        """Register a face by computing its embedding"""
        try:
            print("Computing face embedding...")
            
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
            
            print(f"✓ Successfully registered {name}")
            print(f"  - Encoding saved to {self.encodings_file}")
            print(f"  - Image saved to {img_path}")
            
            return True
            
        except Exception as e:
            print(f"Error registering face: {e}")
            return False
    
    def list_registered_faces(self):
        """List all registered faces"""
        if len(self.known_faces) == 0:
            print("No faces registered yet.")
        else:
            print(f"\nRegistered faces ({len(self.known_faces)}):")
            for i, name in enumerate(self.known_faces.keys(), 1):
                print(f"  {i}. {name}")

if __name__ == "__main__":
    registration = FaceRegistration()
    
    print("="*50)
    print("FACE REGISTRATION SYSTEM")
    print("="*50)
    
    registration.list_registered_faces()
    
    while True:
        print("\nOptions:")
        print("1. Register new face")
        print("2. List registered faces")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            name = input("Enter person's name: ").strip()
            if name:
                registration.capture_face(name)
            else:
                print("Invalid name")
        elif choice == '2':
            registration.list_registered_faces()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice")
