"""
Facial Sentiment Analysis using Camera
Detects faces and analyzes emotions in real-time
"""

import cv2
from fer.fer import FER
import numpy as np


class FacialSentimentAnalyzer:
    def __init__(self, use_mtcnn=False):
        """Initialize the facial sentiment analyzer"""
        print("Initializing Facial Sentiment Analyzer...")
        print(f"Face detector: {'MTCNN (accurate, slower)' if use_mtcnn else 'OpenCV (fast)'}")
        self.detector = FER(mtcnn=use_mtcnn)  # MTCNN is accurate but slow, OpenCV is fast
        self.cap = None
        self.emotions = []
        
        # Define colors for different emotions
        self.emotion_colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (255, 0, 0),        # Blue
            'angry': (0, 0, 255),      # Red
            'neutral': (255, 255, 0),  # Cyan
            'surprise': (0, 255, 255), # Yellow
            'fear': (128, 0, 128),     # Purple
            'disgust': (0, 165, 255)   # Orange
        }
    
    def start_camera(self, camera_index=0):
        """Start the camera capture"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        print(f"Camera {camera_index} opened successfully")
    
    def analyze_frame(self, frame):
        """Analyze a single frame and detect emotions"""
        result = self.detector.detect_emotions(frame)
        return result
    
    def draw_results(self, frame, emotions_data):
        """Draw bounding boxes and emotion labels on the frame"""
        for face_data in emotions_data:
            box = face_data['box']
            x, y, w, h = box
            
            emotions = face_data['emotions']
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion]
            
            color = self.emotion_colors.get(dominant_emotion, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw emotion label
            label = f"{dominant_emotion}: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw top 3 emotions
            y_offset = y + h + 20
            for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]:
                bar_length = int(score * 200)
                emotion_color = self.emotion_colors.get(emotion, (255, 255, 255))
                cv2.rectangle(frame, (x, y_offset), (x + bar_length, y_offset + 15), 
                            emotion_color, -1)
                cv2.putText(frame, f"{emotion}: {score:.2f}", (x + bar_length + 5, y_offset + 12),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, emotion_color, 1)
                y_offset += 20
        
        return frame
    
    def run(self, camera_index=0):
        """Main loop to capture and analyze video"""
        print("Starting facial sentiment analysis...")
        print("Press 'q' to quit, 's' to save screenshot")
        
        try:
            self.start_camera(camera_index)
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break
                
                emotions_data = self.analyze_frame(frame)
                frame_with_results = self.draw_results(frame, emotions_data)
                
                cv2.putText(frame_with_results, "Press 'q' to quit, 's' to save", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Facial Sentiment Analysis', frame_with_results)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"sentiment_capture_{len(self.emotions)}.jpg"
                    cv2.imwrite(filename, frame_with_results)
                    print(f"Screenshot saved as {filename}")
                
                if emotions_data:
                    self.emotions.append(emotions_data)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Camera released and windows closed")
    
    def get_emotion_summary(self):
        """Get a summary of detected emotions"""
        if not self.emotions:
            return "No emotions detected"
        
        emotion_counts = {
            'happy': 0, 'sad': 0, 'angry': 0, 'neutral': 0,
            'surprise': 0, 'fear': 0, 'disgust': 0
        }
        
        for frame_emotions in self.emotions:
            for face_data in frame_emotions:
                emotions = face_data['emotions']
                dominant = max(emotions, key=emotions.get)
                emotion_counts[dominant] += 1
        
        return emotion_counts


def main():
    """Main function to run the facial sentiment analyzer"""
    import sys
    
    camera_index = 0
    use_mtcnn = False
    
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            print(f"Using camera index: {camera_index}")
        except ValueError:
            if sys.argv[1] == '--accurate':
                use_mtcnn = True
                print("Using accurate (slower) MTCNN face detector")
            else:
                print("Invalid camera index. Using default camera 0.")
    
    if len(sys.argv) > 2 and sys.argv[2] == '--accurate':
        use_mtcnn = True
        print("Using accurate (slower) MTCNN face detector")
    
    print("\n🚀 Starting Facial Sentiment Analyzer...")
    print("⏱️  First run may take 10-20 seconds to load models...")
    
    analyzer = FacialSentimentAnalyzer(use_mtcnn=use_mtcnn)
    
    try:
        analyzer.run(camera_index)
        
        print("\n=== Emotion Summary ===")
        summary = analyzer.get_emotion_summary()
        if isinstance(summary, dict):
            for emotion, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"{emotion.capitalize()}: {count} frames")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()


