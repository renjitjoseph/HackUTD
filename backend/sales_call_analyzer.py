"""
Complete Sales Call Analysis System
Combines voice transcription with Gemini API for real-time strategic insights.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from voice_transcription_local import LocalVoiceTranscriber
from google import genai
from datetime import datetime
import time
import threading
import pyttsx3
from supabase import create_client, Client
import json

# Try to import facial sentiment (optional)
try:
    from facial_sentiment_headless import HeadlessFacialSentiment
    FACIAL_AVAILABLE = True
except ImportError:
    FACIAL_AVAILABLE = False
    print("⚠️  Facial sentiment not available (install: pip install fer tensorflow keras)")

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class SalesCallAnalyzer:
    """
    Real-time sales call analyzer that provides strategic insights.
    """

    def __init__(self, gemini_api_key: str, model_size: str = "base",
                 camera_index: int = 0, enable_facial: bool = True,
                 supabase_url: str = None, supabase_key: str = None,
                 customer_id: str = None):
        """
        Initialize the sales call analyzer.

        Args:
            gemini_api_key: Your Google Gemini API key
            model_size: Whisper model size (tiny, base, small, medium, large)
            camera_index: Camera device index for facial analysis (default: 0)
            enable_facial: Enable facial sentiment analysis (default: True)
            supabase_url: Supabase project URL (optional)
            supabase_key: Supabase API key (optional)
            customer_id: Customer identifier from face recognition (optional)
        """
        # Set API key in environment for genai.Client()
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        self.client = genai.Client()

        # Initialize Supabase client (optional)
        self.supabase = None
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️  Supabase initialization failed: {e}")
                self.supabase = None

        # Store customer ID for linking conversations
        self.customer_id = customer_id
        if customer_id:
            print(f"👤 Customer ID set: {customer_id}")

        # Face detection stability tracking
        self.face_detection_enabled = True
        self.locked_customer_id = customer_id  # The confirmed customer for this call
        self.currently_detected_face = None  # What we're seeing right now
        self.detection_start_time = None  # When we first saw this new face
        self.stable_detection_duration = 5.0  # 5 seconds required to change customer
        self.face_detection_thread = None
        self.face_detection_running = False

        # Face recognition setup (matching main.py logic)
        self.known_faces = {}
        self.face_model_name = "Facenet"
        self.recognition_threshold = 8.0  # Confident match threshold
        self.uncertain_threshold = 12.0  # Don't re-register between 8.0-12.0
        self.new_face_cooldown = {}  # Prevent rapid re-registration
        self.cooldown_duration = 3  # seconds
        self.load_face_encodings()

        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 175)  # Speed (default is 200)
        self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Create transcriber
        self.transcriber = LocalVoiceTranscriber(
            on_transcript=self._handle_new_transcript,
            model_size=model_size
        )
        
        # Storage for analysis
        self.insights = []
        self.latest_recommendation = "No recommendation yet"
        
        # Initialize facial sentiment analyzer (optional)
        self.facial_analyzer = None
        self.facial_enabled = False
        
        if enable_facial and FACIAL_AVAILABLE:
            try:
                print("\n🎥 Initializing facial sentiment analysis...")
                self.facial_analyzer = HeadlessFacialSentiment(
                    camera_index=camera_index,
                    use_mtcnn=False,  # Use fast OpenCV detector
                    sample_interval=1.0  # Sample every 1 second
                )
                if self.facial_analyzer.start_capture():
                    self.facial_enabled = True
                    print("✅ Facial sentiment enabled")
                else:
                    print("⚠️  Facial sentiment disabled (camera error)")
                    self.facial_analyzer = None
            except Exception as e:
                print(f"⚠️  Facial sentiment disabled: {e}")
                self.facial_analyzer = None
        elif enable_facial and not FACIAL_AVAILABLE:
            print("⚠️  Facial sentiment disabled (libraries not installed)")
        
        # Start keyboard listener thread
        self.listening = True
        self.keyboard_thread = threading.Thread(target=self._listen_for_enter)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
    def _handle_new_transcript(self, new_chunk: str, full_context: str):
        """
        Called every 10 seconds with new transcript.
        Sends to Gemini for analysis in a separate thread (non-blocking).
        """
        print("\n" + "="*70)
        print("📝 NEW TRANSCRIPT CHUNK")
        print("="*70)
        print(f"Latest 10s: {new_chunk}")
        print(f"\nFull conversation ({len(full_context)} chars): ")
        if len(full_context) > 200:
            print(f"   ...{full_context[-200:]}")
        else:
            print(f"   {full_context}")
        print("="*70)
        
        # Get strategic insights from Gemini IN PARALLEL (don't block recording)
        print("\n🤖 Analyzing with Gemini AI (in background)...")
        
        # Run Gemini analysis in separate thread so recording continues
        analysis_thread = threading.Thread(
            target=self._analyze_async,
            args=(new_chunk, full_context)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _analyze_async(self, new_chunk: str, full_context: str):
        """
        Run Gemini analysis asynchronously so it doesn't block recording.
        """
        try:
            # Get facial emotion data if available
            emotion_data = None
            if self.facial_enabled and self.facial_analyzer:
                emotion_data = self.facial_analyzer.get_emotion_summary(duration_seconds=10)

            insights = self._get_sales_insights(full_context, emotion_data)

            # Store insights with emotion data
            self.insights.append({
                'timestamp': datetime.now(),
                'transcript': new_chunk,
                'full_context': full_context,
                'emotion_data': emotion_data,
                'insights': insights
            })

            # Display insights (compact)
            print("\n" + "⚡"*35)
            print(insights)
            print("⚡"*35 + "\n")

            # Parse and save insights to active_session
            self._save_insights_to_active_session(insights)

            # Speak the status report
            self._speak_insights(insights)

        except Exception as e:
            print(f"❌ Error getting insights: {e}")
    
    def _save_insights_to_active_session(self, insights: str):
        """
        Parse Gemini insights and save to active_session table.
        Only updates recommendation/reason if status changes.
        Score is always updated.
        """
        if not self.supabase:
            return

        try:
            # Parse new insights
            lines = insights.strip().split('\n')
            parsed = {}

            for line in lines:
                if line.startswith('STATUS:'):
                    parsed['status'] = line.replace('STATUS:', '').strip()
                elif line.startswith('REASON:'):
                    parsed['reason'] = line.replace('REASON:', '').strip()
                elif line.startswith('SAY THIS:'):
                    parsed['recommendation'] = line.replace('SAY THIS:', '').strip().strip('"')
                elif line.startswith('SCORE:'):
                    score_text = line.replace('SCORE:', '').strip()
                    try:
                        parsed['score'] = int(score_text)
                    except:
                        parsed['score'] = None

            if not parsed:
                return

            # Get current insight to check if status changed
            current = self.supabase.table('active_session').select('current_insight').eq('id', 1).single().execute()
            current_insight = current.data.get('current_insight') if current.data else None

            # Determine what to update
            new_status = parsed.get('status')
            if current_insight and current_insight.get('status') == new_status:
                # Status hasn't changed - only update score
                current_insight['score'] = parsed.get('score')
                current_insight['timestamp'] = datetime.now().isoformat()
                update_data = current_insight
                print(f"💡 Updated score for existing status: {new_status} (score: {parsed.get('score')})")
            else:
                # Status changed - update everything
                update_data = {
                    'status': new_status,
                    'reason': parsed.get('reason'),
                    'recommendation': parsed.get('recommendation'),
                    'score': parsed.get('score'),
                    'timestamp': datetime.now().isoformat()
                }
                print(f"💡 Status changed to: {new_status} (score: {parsed.get('score')})")

            # Save to active_session
            self.supabase.table('active_session').update({
                'current_insight': update_data
            }).eq('id', 1).execute()

        except Exception as e:
            print(f"⚠️  Error saving insights to active_session: {e}")

    def _speak_insights(self, insights: str):
        """
        Convert insights to speech (TTS) - ONLY the status line.
        Also extracts and saves the recommendation.
        """
        try:
            # Extract status and recommendation
            lines = insights.strip().split('\n')

            status_text = ""
            for line in lines:
                if line.startswith('STATUS:'):
                    status = line.replace('STATUS:', '').strip()
                    status_text = status
                elif line.startswith('SAY THIS:'):
                    recommendation = line.replace('SAY THIS:', '').strip().strip('"')
                    self.latest_recommendation = recommendation

            if status_text:
                print(f"🔊 Speaking: {status_text}")
                self.tts_engine.say(status_text)
                self.tts_engine.runAndWait()

        except Exception as e:
            print(f"⚠️  TTS error: {e}")
    
    def _listen_for_enter(self):
        """
        Listen for Enter key press to speak the latest recommendation.
        """
        import sys
        while self.listening:
            try:
                # Wait for Enter key
                input()  # This blocks until Enter is pressed
                
                # Speak the latest recommendation
                if self.latest_recommendation and self.latest_recommendation != "No recommendation yet":
                    print(f"\n💬 Speaking recommendation: {self.latest_recommendation}\n")
                    self.tts_engine.say(self.latest_recommendation)
                    self.tts_engine.runAndWait()
                else:
                    print("\n⚠️  No recommendation available yet. Wait for first analysis.\n")
                    
            except:
                break
            
    def _get_sales_insights(self, transcript: str, emotion_data: dict = None) -> str:
        """
        Get strategic insights from Gemini based on transcript and facial emotions.
        
        Args:
            transcript: The complete conversation transcript (full history)
            emotion_data: Optional dict with facial emotion analysis
            
        Returns:
            Strategic insights and recommendations
        """
        # Build emotion context if available
        emotion_context = ""
        if emotion_data:
            dominant = emotion_data['dominant_emotion']
            confidence = emotion_data['confidence'] * 100
            trajectory = emotion_data['emotion_trajectory']
            
            # Format top 3 emotions
            breakdown = emotion_data['emotion_breakdown']
            top_emotions = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            emotion_list = "\n".join([
                f"- {emotion.capitalize()}: {score*100:.0f}%" 
                for emotion, score in top_emotions
            ])
            
            emotion_context = f"""

CUSTOMER FACIAL EXPRESSIONS (last 10 seconds):
Dominant Emotion: {dominant.capitalize()} ({confidence:.0f}% confidence)
Emotion Trajectory: {trajectory.capitalize()}
Breakdown:
{emotion_list}
"""
        
        prompt = f"""You are a sales coach. Analyze this conversation{' and the customer\'s facial expressions' if emotion_data else ''} and give a quick status update.

CONVERSATION TRANSCRIPT:
{transcript}{emotion_context}

Respond in this EXACT format (keep it SHORT):

STATUS: [Pick ONE: Ready to Buy | Highly Interested | Engaged & Curious | Feeling Neutral | Showing Hesitation | Has Objections | Feeling Confused | Losing Interest | Not a Fit]

REASON: [One short sentence why{' - consider BOTH words AND facial expressions' if emotion_data else ''}]

SAY THIS: "[Exact phrase to say next - max 20 words]"

SCORE: [1-10]

Keep it brief and actionable."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
        
    def set_active_session(self, status='active'):
        """Update the active_session table to mark session as active/idle."""
        if not self.supabase:
            return

        try:
            data = {
                'status': status
            }

            if status == 'active':
                data['session_started_at'] = datetime.now().isoformat()
                data['current_customer_id'] = None
                data['confidence_level'] = 'detecting'
                data['detection_started_at'] = None
            else:  # idle
                data['current_customer_id'] = None
                data['confidence_level'] = 'detecting'
                data['detection_started_at'] = None
                data['session_started_at'] = None

            self.supabase.table('active_session').update(data).eq('id', 1).execute()
            print(f"✅ Active session status: {status}")

        except Exception as e:
            print(f"❌ Error updating active session: {e}")

    def load_face_encodings(self):
        """Load face encodings for recognition"""
        encodings_file = "face_encodings.pkl"
        if os.path.exists(encodings_file):
            try:
                import pickle
                with open(encodings_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
                print(f"✅ Loaded {len(self.known_faces)} known faces for detection")
            except Exception as e:
                print(f"⚠️  Could not load face encodings: {e}")
        else:
            # No encodings file - create empty one, will auto-register first face
            print("⚠️  No face_encodings.pkl found - will auto-register new faces")
            self.known_faces = {}
            # Don't disable face detection - we'll register the first face we see

    def recognize_face(self, face_img):
        """
        Highly accurate face recognition using DeepFace - matches main.py logic.

        Strategy (from main.py):
        1. Use Facenet model with enforce_detection=False for robustness
        2. Two-tier threshold system:
           - < 8.0: Confident match (same person)
           - 8.0-12.0: Uncertain (likely same, don't re-register)
           - > 12.0: Different person (register as new)
        3. Cooldown system: Prevent rapid re-registration (3 seconds)
        """
        try:
            from deepface import DeepFace
            import numpy as np

            # Validate input image
            if face_img is None or face_img.size == 0:
                return None

            # Get embedding (use enforce_detection=False like main.py for robustness)
            try:
                result = DeepFace.represent(
                    face_img,
                    model_name=self.face_model_name,
                    enforce_detection=False  # More forgiving like main.py
                )
                embedding = result[0]["embedding"]
            except Exception as e:
                print(f"   ⚠️  Could not generate embedding: {e}")
                return None

            # Find closest match
            min_distance = float('inf')
            recognized_name = None

            for name, known_embedding in self.known_faces.items():
                distance = np.linalg.norm(np.array(embedding) - np.array(known_embedding))
                if distance < min_distance:
                    min_distance = distance
                    recognized_name = name

            # Two-tier threshold system (matching main.py)
            if min_distance < self.uncertain_threshold and recognized_name:
                # Within uncertain threshold (< 12.0)
                if min_distance < self.recognition_threshold:
                    # HIGH CONFIDENCE (< 8.0) - Definite match
                    print(f"   ✓ Recognized: {recognized_name} (distance: {min_distance:.2f})")
                    return recognized_name
                else:
                    # MEDIUM CONFIDENCE (8.0-12.0) - Likely same person, don't re-register
                    print(f"   ✓ Recognized: {recognized_name} (?) (distance: {min_distance:.2f})")
                    return recognized_name
            else:
                # UNKNOWN (> 12.0) - Check cooldown before registering
                current_time = time.time()

                # Use a unique face_id for cooldown tracking
                face_id = f"face_{int(current_time * 1000)}"

                # Check cooldown to prevent rapid re-registration
                if face_id in self.new_face_cooldown:
                    last_capture_time = self.new_face_cooldown[face_id]
                    if current_time - last_capture_time < self.cooldown_duration:
                        print(f"   ⏳ Processing... (distance: {min_distance:.2f})")
                        return None

                # Register new face (pass face_img first, then embedding like main.py)
                print(f"   🆕 New person detected (distance: {min_distance:.2f}, threshold: {self.uncertain_threshold})")
                new_customer_id = self.register_new_face(face_img, embedding)

                if new_customer_id:
                    # Update cooldown
                    self.new_face_cooldown[face_id] = current_time

                return new_customer_id

        except Exception as e:
            print(f"   ❌ Recognition error: {e}")
            return None

    def register_new_face(self, face_img, embedding=None):
        """
        Auto-register a new unknown face - matches main.py exactly.

        Args:
            face_img: Face image to register
            embedding: Pre-computed embedding (optional, will compute if None)

        Returns:
            customer_id: Generated ID like "Person_ABC123"
        """
        import random
        import string
        import pickle
        import cv2
        from deepface import DeepFace

        try:
            # Generate unique customer ID (matches main.py logic)
            random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            customer_id = f"Person_{random_id}"

            # Make sure it's unique
            while customer_id in self.known_faces:
                random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                customer_id = f"Person_{random_id}"

            print(f"\n[NEW FACE DETECTED] Registering as: {customer_id}")

            # Get embedding if not provided (matches main.py)
            if embedding is None:
                embedding = DeepFace.represent(
                    face_img,
                    model_name=self.face_model_name,
                    enforce_detection=False
                )[0]["embedding"]

            # Save to database (matches main.py)
            self.known_faces[customer_id] = embedding

            # Save encodings to file
            encodings_file = "face_encodings.pkl"
            with open(encodings_file, 'wb') as f:
                pickle.dump(self.known_faces, f)

            # Save face image
            database_path = "face_database"
            if not os.path.exists(database_path):
                os.makedirs(database_path)

            img_path = os.path.join(database_path, f"{customer_id}.jpg")
            cv2.imwrite(img_path, face_img)

            print(f"✓ Successfully registered {customer_id}")
            print(f"  Total faces in database: {len(self.known_faces)}")

            return customer_id

        except Exception as e:
            print(f"Error registering new face: {e}")
            return None

    def face_detection_loop(self):
        """Continuous face detection loop with GUI in main thread"""
        import cv2

        # MUST open new camera - cannot share with facial analyzer for GUI
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open webcam for face detection")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        frame_count = 0
        last_detected_id = None  # Track last detected ID to reduce spam
        last_print_time = time.time()  # For periodic status updates

        print("👁️  Face detection monitoring started")
        print("📺 Camera window opened - Press 'q' to close")

        while self.face_detection_running:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_count += 1
            display_frame = frame.copy()
            current_time = time.time()

            # Process every 10 frames (~3 fps for more responsive detection)
            if frame_count % 10 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

                if len(faces) > 0:
                    # Extract first face
                    x, y, w, h = faces[0]

                    # Draw rectangle around face
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    padding = 20
                    y1 = max(0, y - padding)
                    y2 = min(frame.shape[0], y + h + padding)
                    x1 = max(0, x - padding)
                    x2 = min(frame.shape[1], x + w + padding)
                    face_img = frame[y1:y2, x1:x2]

                    # Recognize face
                    detected_id = self.recognize_face(face_img)

                    if detected_id:
                        # Only print if ID changed
                        if detected_id != last_detected_id:
                            self.process_detected_face(detected_id)
                            last_detected_id = detected_id
                        else:
                            # Silently process without printing
                            self.process_detected_face(detected_id)

                        # Display name on frame
                        status = f"{detected_id}"
                        if self.locked_customer_id:
                            status = f"LOCKED: {self.locked_customer_id}"
                        cv2.putText(display_frame, status, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        if last_detected_id is not None:
                            print(f"⚠️  Face detected but recognition failed")
                            last_detected_id = None
                else:
                    # No face in frame
                    if self.currently_detected_face is not None:
                        print(f"👤 Current: {self.locked_customer_id or 'None'} | Detected: [No face in frame]")
                        self.currently_detected_face = None
                        self.detection_start_time = None
                        last_detected_id = None

            # Print status updates to console instead of GUI (GUI doesn't work in thread on macOS)
            if self.locked_customer_id and frame_count % 150 == 0:  # Every ~5 seconds
                print(f"📹 Face Detection Active | Customer: {self.locked_customer_id} | Status: LOCKED")
            elif self.currently_detected_face and frame_count % 30 == 0:  # Every second during verification
                elapsed = current_time - self.detection_start_time
                remaining = max(0, self.stable_detection_duration - elapsed)
                print(f"📹 Verifying customer... {remaining:.1f}s remaining")

            time.sleep(0.05)  # ~20fps processing

        cap.release()
        cv2.destroyAllWindows()
        print("✅ Face detection stopped")

    def process_detected_face(self, detected_id):
        """Process a detected face with 5-second stability check"""
        current_time = time.time()

        # Print status
        print(f"👤 Current: {self.locked_customer_id or 'None'} | Detected: {detected_id}")

        # If this is a different face than what we're currently tracking
        if detected_id != self.currently_detected_face:
            # Start tracking this new face
            self.currently_detected_face = detected_id
            self.detection_start_time = current_time
            print(f"   🔍 New face detected, tracking for 5 seconds...")

            # Update active_session to "detecting"
            if self.supabase:
                try:
                    self.supabase.table('active_session').update({
                        'confidence_level': 'detecting'
                    }).eq('id', 1).execute()
                except:
                    pass

            return

        # Same face as we're tracking - check if it's been 5 seconds
        time_elapsed = current_time - self.detection_start_time

        # Lock customer if:
        # 1. It's been 5 seconds AND
        # 2. Either no customer locked yet OR detected face is different from locked customer
        if time_elapsed >= self.stable_detection_duration:
            if self.locked_customer_id is None or detected_id != self.locked_customer_id:
                # Check if this is first lock or a change
                is_first_lock = (self.locked_customer_id is None)

                # Lock in the new customer
                self.locked_customer_id = detected_id
                self.customer_id = detected_id

                if is_first_lock:
                    print(f"   ✅ CUSTOMER LOCKED: {detected_id} (stable for {time_elapsed:.1f}s)")
                else:
                    print(f"   ✅ CUSTOMER CHANGED: {detected_id} (stable for {time_elapsed:.1f}s)")

                # Update active_session
                if self.supabase:
                    try:
                        self.supabase.table('active_session').update({
                            'current_customer_id': detected_id,
                            'confidence_level': 'stable'
                        }).eq('id', 1).execute()
                        print(f"   ✅ Updated active_session with customer: {detected_id}")
                    except Exception as e:
                        print(f"   ❌ Error updating active session: {e}")

    def start(self):
        """Start the sales call analysis."""
        print("\n" + "🚀"*35)
        print("SALES CALL ANALYZER STARTED")
        print("🚀"*35)
        print("\nListening to sales call...")
        print("⚡ Real-time transcription + AI insights every 10 seconds")
        print("📚 Maintains FULL conversation history for context")
        print("🔄 Parallel processing - NO GAPS in recording!")
        print("🔊 TTS enabled - Status reports spoken out loud!")
        if self.facial_enabled:
            print("🎥 Facial sentiment analysis ACTIVE")
        print("⌨️  Press ENTER anytime to hear latest recommendation!")
        print("Press Ctrl+C to stop\n")

        # Mark session as active
        self.set_active_session('active')

        # Start face detection in background thread (even if no faces registered yet)
        if self.face_detection_enabled:
            self.face_detection_running = True
            # Use daemon=False so window stays open
            self.face_detection_thread = threading.Thread(target=self.face_detection_loop, daemon=False)
            self.face_detection_thread.start()
            print("👁️  Face detection enabled - will auto-register new faces")
            print("💡 TIP: Press 'q' in camera window to close it")

        self.transcriber.start()
        
    def stop(self):
        """Stop the analysis."""
        self.listening = False
        self.transcriber.stop()

        # Stop face detection thread
        if self.face_detection_running:
            self.face_detection_running = False
            if self.face_detection_thread:
                self.face_detection_thread.join(timeout=2)

        # Stop facial capture if enabled
        if self.facial_analyzer:
            self.facial_analyzer.stop()

        # Mark session as idle
        self.set_active_session('idle')

        # Save conversation to Supabase if available
        if self.supabase and len(self.insights) > 0:
            self.save_conversation_to_supabase()

        # Show summary
        print("\n" + "📊"*35)
        print("CALL SUMMARY")
        print("📊"*35)
        print(f"Total insights generated: {len(self.insights)}")
        print(f"Call duration: ~{len(self.insights) * 10} seconds")
        if self.facial_enabled:
            print(f"Facial analysis: Enabled")
        print("📊"*35 + "\n")
        
    def get_full_analysis(self) -> str:
        """
        Get a complete analysis of the entire call.
        """
        if not self.insights:
            return "No insights available yet."
            
        # Compile all transcripts
        full_transcript = " ".join([i['transcript'] for i in self.insights])
        
        # Get comprehensive analysis
        prompt = f"""You are an expert sales strategist. Provide a comprehensive POST-CALL analysis with SPECIFIC, ACTIONABLE recommendations.

FULL CALL TRANSCRIPT:
{full_transcript}

Provide a detailed report:

📞 EXECUTIVE SUMMARY
- Call duration and outcome
- Overall effectiveness (1-10)
- Key result: [Deal advanced / Stalled / Lost]

🎯 WHAT HAPPENED
- Main topics discussed
- Customer's stated needs
- Sales rep's approach

👤 CUSTOMER PROFILE
Pain Points Discovered:
- [Specific pain point 1 with $ impact if mentioned]
- [Specific pain point 2 with $ impact if mentioned]
- [Specific pain point 3 with $ impact if mentioned]

Authority Level: [Decision maker / Influencer / End user]
Budget Signals: [Specific mentions about budget/money]
Timeline: [When they need solution by]
Competition: [Other solutions mentioned]

📊 SENTIMENT ANALYSIS
Overall: [Very Positive / Positive / Neutral / Negative / Very Negative]
- Beginning: [How they started]
- Middle: [How engagement evolved]  
- End: [How they finished]
Engagement Level: [High / Medium / Low] - [Why]

✅ WHAT WENT WELL
- [Specific thing rep did well]
- [Specific technique that worked]
- [Specific moment that built trust]

❌ MISSED OPPORTUNITIES
- [Specific question that should have been asked]
- [Specific pain point that wasn't explored]
- [Specific objection that wasn't addressed]

💡 WHAT TO DO DIFFERENTLY NEXT TIME
- [Specific improvement 1]
- [Specific improvement 2]
- [Specific improvement 3]

📋 IMMEDIATE NEXT STEPS (Next 24 hours)
1. [Specific action with exact deliverable]
2. [Specific action with exact deliverable]
3. [Specific action with exact deliverable]

📅 FOLLOW-UP STRATEGY (This Week)
- [Specific action item 1]
- [Specific action item 2]
- [Specific action item 3]

🎯 DEAL ASSESSMENT
Probability to Close: [X%]
Reasoning:
- [Factor increasing probability]
- [Factor decreasing probability]

Biggest Risk: [Specific risk]
How to Mitigate: [Specific action]

Biggest Opportunity: [Specific opportunity]
How to Capitalize: [Specific action]

🔑 KEY TALKING POINTS FOR NEXT CALL
- [Specific point 1]
- [Specific point 2]
- [Specific point 3]

Be ULTRA-SPECIFIC. Use exact quotes from the call. Give concrete actions, not generic advice."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    def extract_customer_profile(self, transcript: str) -> dict:
        """
        Extract structured customer profile from transcript using Gemini.

        Args:
            transcript: Full conversation transcript

        Returns:
            Dictionary with name, personal_details, professional_details, sales_context
        """
        try:
            prompt = f"""You are a customer intelligence analyst. Extract key information from this sales call transcript and structure it into a clean customer profile.

TRANSCRIPT:
{transcript}

Extract information and format as JSON with this EXACT structure:

{{
  "name": "Customer name if mentioned, or null",
  "personal_details": [
    "Single line bullet point about personal life",
    "Another personal detail"
  ],
  "professional_details": [
    "Single line bullet point about work/career",
    "Another professional detail"
  ],
  "sales_context": [
    "Current provider: [Provider name]",
    "Pain point: [Specific issue]",
    "Another sales-relevant detail"
  ]
}}

RULES:
1. Each bullet must be ONE LINE only - concise and specific
2. Only include information EXPLICITLY mentioned in the transcript
3. If a category has no information, use an empty array []
4. Be specific - include exact details (provider names, dollar amounts, features mentioned)
5. Focus on facts, not interpretations
6. Format sales_context bullets as "Topic: Detail" for easy scanning
7. Return ONLY valid JSON, no markdown formatting or explanation.

JSON OUTPUT:"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Clean the response (remove markdown if present)
            response_text = response.text.strip()
            if response_text.startswith("```"):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            profile = json.loads(response_text)
            return profile

        except Exception as e:
            print(f"❌ Error extracting customer profile: {e}")
            return {
                "name": None,
                "personal_details": [],
                "professional_details": [],
                "sales_context": []
            }

    def save_customer_profile(self, profile: dict):
        """
        Save or update customer profile in Supabase with merge logic.
        New information is appended and reordered by recency (newest first).

        Args:
            profile: Extracted profile dictionary
        """
        if not self.supabase or not self.customer_id:
            print("⚠️  Cannot save customer profile (missing Supabase or customer_id)")
            return

        try:
            # Check if customer already exists
            existing = self.supabase.table('customers').select('*').eq('customer_id', self.customer_id).execute()

            if existing.data and len(existing.data) > 0:
                # MERGE with existing profile
                existing_profile = existing.data[0]

                # Merge arrays: new items first (recency), then deduplicate
                def merge_bullets(new_bullets, old_bullets):
                    # Start with new bullets
                    merged = list(new_bullets)
                    # Add old bullets that aren't duplicates
                    for old_bullet in old_bullets:
                        if old_bullet not in merged:
                            merged.append(old_bullet)
                    return merged

                merged_profile = {
                    "customer_id": self.customer_id,
                    "name": profile.get('name') or existing_profile.get('name'),
                    "personal_details": merge_bullets(
                        profile.get('personal_details', []),
                        existing_profile.get('personal_details', [])
                    ),
                    "professional_details": merge_bullets(
                        profile.get('professional_details', []),
                        existing_profile.get('professional_details', [])
                    ),
                    "sales_context": merge_bullets(
                        profile.get('sales_context', []),
                        existing_profile.get('sales_context', [])
                    )
                }

                # Update existing record
                self.supabase.table('customers').update(merged_profile).eq('customer_id', self.customer_id).execute()
                print(f"✅ Customer profile updated (merged with existing data)")

            else:
                # CREATE new profile
                new_profile = {
                    "customer_id": self.customer_id,
                    "name": profile.get('name'),
                    "personal_details": profile.get('personal_details', []),
                    "professional_details": profile.get('professional_details', []),
                    "sales_context": profile.get('sales_context', [])
                }

                self.supabase.table('customers').insert(new_profile).execute()
                print(f"✅ New customer profile created")

        except Exception as e:
            print(f"❌ Error saving customer profile: {e}")

    def save_conversation_to_supabase(self):
        """
        Save the complete conversation transcript and insights to Supabase.
        Also extracts and saves/updates customer profile.
        """
        if not self.supabase:
            print("⚠️  Supabase not configured, skipping save")
            return

        try:
            # Compile full transcript
            full_transcript = " ".join([i['transcript'] for i in self.insights])

            # Prepare conversation data
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": len(self.insights) * 10,
                "full_transcript": full_transcript,
                "insights_count": len(self.insights),
                "facial_analysis_enabled": self.facial_enabled,
                "customer_id": self.customer_id,  # Link to face recognition
                "insights": [
                    {
                        "timestamp": insight['timestamp'].isoformat(),
                        "transcript": insight['transcript'],
                        "emotion_data": insight.get('emotion_data'),
                        "insights": insight['insights']
                    }
                    for insight in self.insights
                ]
            }

            # Insert into Supabase
            print("\n💾 Saving conversation to Supabase...")
            result = self.supabase.table('conversations').insert(conversation_data).execute()
            print(f"✅ Conversation saved to Supabase (ID: {result.data[0]['id']})")

            # Extract and save customer profile
            if self.customer_id:
                print("\n🧠 Extracting customer profile with Gemini...")
                profile = self.extract_customer_profile(full_transcript)

                if profile:
                    print(f"\n📋 Extracted Profile:")
                    print(f"   Name: {profile.get('name') or 'Not mentioned'}")
                    print(f"   Personal: {len(profile.get('personal_details', []))} details")
                    print(f"   Professional: {len(profile.get('professional_details', []))} details")
                    print(f"   Sales Context: {len(profile.get('sales_context', []))} details")

                    print("\n💾 Saving customer profile...")
                    self.save_customer_profile(profile)

        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")


def main():
    """
    Main function to run the sales call analyzer.
    """
    # Get API key from .env file or environment
    api_key = os.getenv("GEMINI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found")
        print("\nTo set it up:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Create a .env file in the project root:")
        print("   cp env_template.txt .env")
        print("3. Edit .env and add your key:")
        print("   GEMINI_API_KEY=your-api-key-here")
        print("\nOr enter it now (or press Enter to skip Gemini integration):")
        api_key = input("API Key: ").strip()

        if not api_key:
            print("\n⚠️  Running in TRANSCRIPTION-ONLY mode (no AI insights)")
            print("Transcripts will be shown but not analyzed.\n")

            # Run without Gemini
            transcriber = LocalVoiceTranscriber(model_size="base")
            try:
                transcriber.start()
                print("🎤 Recording for 60 seconds...")
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n\nStopped by user")
            finally:
                transcriber.stop()
            return

    # Create analyzer with Gemini integration
    analyzer = SalesCallAnalyzer(
        gemini_api_key=api_key,
        model_size="base",  # Change to "tiny" for faster, "small" for more accurate
        camera_index=0,  # Change camera index if needed
        enable_facial=True,  # Set to False to disable facial sentiment
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    try:
        # Start analysis
        analyzer.start()
        
        # Run for 60 seconds (or until interrupted)
        print("📞 Simulating 60-second sales call...")
        print("   (In production, this would run for the entire call)\n")
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        
    finally:
        # Stop recording
        analyzer.stop()
        
        # Just save the transcript and insights - NO post-call analysis
        if len(analyzer.insights) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_insights_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("SALES CALL REAL-TIME INSIGHTS\n")
                f.write("="*70 + "\n\n")
                
                # Write each insight
                for i, insight in enumerate(analyzer.insights, 1):
                    f.write(f"CHUNK {i} - {insight['timestamp']}\n")
                    f.write("-"*70 + "\n")
                    f.write(f"Transcript: {insight['transcript']}\n\n")
                    
                    # Write emotion data if available
                    if insight.get('emotion_data'):
                        emotion = insight['emotion_data']
                        f.write(f"Facial Emotion: {emotion['dominant_emotion'].capitalize()} "
                               f"({emotion['confidence']*100:.0f}%)\n")
                        f.write(f"Trajectory: {emotion['emotion_trajectory'].capitalize()}\n\n")
                    
                    f.write(f"Insights:\n{insight['insights']}\n\n")
                    f.write("="*70 + "\n\n")
                
            print(f"\n💾 Call insights saved to: {filename}")


if __name__ == "__main__":
    main()

