"""
Headless Facial Sentiment Analysis Module
Captures facial emotions in background without GUI for integration with sales call analyzer.
"""

import cv2
import threading
import time
from collections import deque, Counter
from datetime import datetime
import numpy as np

try:
    from fer.fer import FER
    FER_AVAILABLE = True
except ImportError as e:
    FER_AVAILABLE = False
    FER = None
    # Silent import - error will be shown in sales_call_analyzer.py


class HeadlessFacialSentiment:
    """
    Background facial emotion capture without GUI.
    Continuously captures emotions and aggregates them over time windows.
    """
    
    def __init__(self, camera_index=0, use_mtcnn=False, sample_interval=1.0):
        """
        Initialize headless facial sentiment analyzer.
        
        Args:
            camera_index: Camera device index (default: 0)
            use_mtcnn: Use MTCNN detector for accuracy vs OpenCV for speed
            sample_interval: Seconds between emotion samples (default: 1.0)
        """
        if not FER_AVAILABLE or FER is None:
            raise ImportError("FER library not found in current Python environment")
        
        self.camera_index = camera_index
        self.use_mtcnn = use_mtcnn
        self.sample_interval = sample_interval
        
        # Initialize FER detector
        print(f"🎥 Initializing facial emotion detector...")
        self.detector = FER(mtcnn=use_mtcnn)
        
        # Camera and capture state
        self.cap = None
        self.running = False
        self.capture_thread = None
        
        # Store emotion samples with timestamps
        # Each sample: {'timestamp': datetime, 'emotion': str, 'confidence': float, 'all_emotions': dict}
        self.emotion_samples = deque(maxlen=60)  # Keep last 60 samples (60 seconds at 1/sec)
        
        # Lock for thread-safe access to emotion samples
        self.lock = threading.Lock()
        
        # Error tracking
        self.last_error = None
        self.consecutive_failures = 0
    
    def start_capture(self):
        """Start capturing emotions in background thread."""
        if self.running:
            print("⚠️  Facial capture already running")
            return False
        
        # Open camera
        print(f"📹 Opening camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            self.last_error = f"Could not open camera {self.camera_index}"
            print(f"❌ {self.last_error}")
            return False
        
        # Test camera
        time.sleep(1.0)
        for _ in range(5):
            self.cap.read()
        
        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            self.last_error = "Camera opened but cannot read frames (check permissions)"
            print(f"❌ {self.last_error}")
            self.cap.release()
            return False
        
        print(f"✅ Camera started successfully")
        
        # Start background capture thread
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        print(f"✅ Facial emotion capture started (sampling every {self.sample_interval}s)")
        return True
    
    def _capture_loop(self):
        """Background loop that captures emotions continuously."""
        while self.running:
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= 10:
                        self.last_error = "Too many consecutive frame capture failures"
                        print(f"❌ {self.last_error}")
                        break
                    time.sleep(0.1)
                    continue
                
                # Reset failure counter
                self.consecutive_failures = 0
                
                # Detect emotions
                emotions_data = self.detector.detect_emotions(frame)
                
                if emotions_data and len(emotions_data) > 0:
                    # Get first face (assuming single customer)
                    face_data = emotions_data[0]
                    emotions = face_data['emotions']
                    
                    # Get dominant emotion
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                    emotion_name = dominant_emotion[0]
                    confidence = dominant_emotion[1]
                    
                    # Store sample
                    sample = {
                        'timestamp': datetime.now(),
                        'emotion': emotion_name,
                        'confidence': confidence,
                        'all_emotions': emotions.copy()
                    }
                    
                    with self.lock:
                        self.emotion_samples.append(sample)
                
                # Wait for next sample
                time.sleep(self.sample_interval)
            
            except Exception as e:
                self.last_error = f"Error in capture loop: {e}"
                print(f"⚠️  {self.last_error}")
                time.sleep(1.0)
    
    def get_emotion_summary(self, duration_seconds=10):
        """
        Get aggregated emotion summary over recent time window.
        
        Args:
            duration_seconds: Look back this many seconds (default: 10)
            
        Returns:
            dict with emotion statistics or None if no data available
        """
        with self.lock:
            if not self.emotion_samples:
                return None
            
            # Filter samples within time window
            now = datetime.now()
            cutoff = now.timestamp() - duration_seconds
            
            recent_samples = [
                s for s in self.emotion_samples 
                if s['timestamp'].timestamp() >= cutoff
            ]
            
            if not recent_samples:
                return None
            
            # Calculate dominant emotion (most frequent)
            emotion_counts = Counter([s['emotion'] for s in recent_samples])
            dominant_emotion = emotion_counts.most_common(1)[0][0]
            
            # Calculate average confidence for each emotion across all samples
            emotion_sums = {}
            for sample in recent_samples:
                for emotion, score in sample['all_emotions'].items():
                    if emotion not in emotion_sums:
                        emotion_sums[emotion] = []
                    emotion_sums[emotion].append(score)
            
            emotion_averages = {
                emotion: np.mean(scores) 
                for emotion, scores in emotion_sums.items()
            }
            
            # Calculate emotion trajectory (improving/declining/stable)
            trajectory = self._calculate_trajectory(recent_samples)
            
            # Get average confidence for dominant emotion
            dominant_confidences = [
                s['confidence'] for s in recent_samples 
                if s['emotion'] == dominant_emotion
            ]
            avg_confidence = np.mean(dominant_confidences) if dominant_confidences else 0.0
            
            return {
                'dominant_emotion': dominant_emotion,
                'confidence': avg_confidence,
                'emotion_breakdown': emotion_averages,
                'samples_count': len(recent_samples),
                'emotion_trajectory': trajectory,
                'emotion_counts': dict(emotion_counts)
            }
    
    def _calculate_trajectory(self, samples):
        """
        Calculate if emotions are improving, declining, or stable.
        Uses positive emotions (happy, surprise) vs negative (sad, angry, fear, disgust).
        """
        if len(samples) < 3:
            return 'stable'
        
        positive_emotions = {'happy', 'surprise'}
        negative_emotions = {'sad', 'angry', 'fear', 'disgust'}
        
        # Split samples into first half and second half
        mid = len(samples) // 2
        first_half = samples[:mid]
        second_half = samples[mid:]
        
        def get_positivity_score(sample_list):
            positive_count = sum(1 for s in sample_list if s['emotion'] in positive_emotions)
            negative_count = sum(1 for s in sample_list if s['emotion'] in negative_emotions)
            total = len(sample_list)
            return (positive_count - negative_count) / total if total > 0 else 0
        
        first_score = get_positivity_score(first_half)
        second_score = get_positivity_score(second_half)
        
        diff = second_score - first_score
        
        if diff > 0.2:
            return 'improving'
        elif diff < -0.2:
            return 'declining'
        else:
            return 'stable'
    
    def get_latest_emotion(self):
        """Get the most recent emotion sample."""
        with self.lock:
            if not self.emotion_samples:
                return None
            return self.emotion_samples[-1]
    
    def stop(self):
        """Stop capturing emotions and release resources."""
        print("\n🛑 Stopping facial emotion capture...")
        
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        
        print("✅ Facial capture stopped")
    
    def get_status(self):
        """Get current status of the capture system."""
        with self.lock:
            sample_count = len(self.emotion_samples)
            latest = self.emotion_samples[-1] if self.emotion_samples else None
        
        return {
            'running': self.running,
            'total_samples': sample_count,
            'latest_emotion': latest['emotion'] if latest else None,
            'last_error': self.last_error
        }


def test_headless_capture():
    """Test function for headless capture."""
    print("="*60)
    print("TESTING HEADLESS FACIAL SENTIMENT CAPTURE")
    print("="*60)
    
    analyzer = HeadlessFacialSentiment(camera_index=0, sample_interval=1.0)
    
    if not analyzer.start_capture():
        print("Failed to start capture")
        return
    
    try:
        # Capture for 15 seconds
        for i in range(15):
            time.sleep(1)
            
            status = analyzer.get_status()
            print(f"\n[{i+1}s] Status: {status['total_samples']} samples, "
                  f"Latest: {status['latest_emotion']}")
            
            if i >= 9:  # After 10 seconds, start showing summaries
                summary = analyzer.get_emotion_summary(duration_seconds=10)
                if summary:
                    print(f"  📊 10s Summary:")
                    print(f"     Dominant: {summary['dominant_emotion']} "
                          f"({summary['confidence']:.1%})")
                    print(f"     Trajectory: {summary['emotion_trajectory']}")
                    print(f"     Samples: {summary['samples_count']}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        analyzer.stop()
        print("\n✅ Test complete")


if __name__ == "__main__":
    test_headless_capture()

