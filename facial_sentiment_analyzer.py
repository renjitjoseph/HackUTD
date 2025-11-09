#!/usr/bin/env python3
"""
Real-time Facial Sentiment Analysis Application

This application uses your webcam to detect faces and analyze emotions in real-time.
It supports 7 emotions: happy, sad, angry, neutral, surprise, fear, and disgust.

Author: AI Assistant
Date: 2025
License: MIT
"""

import cv2
import argparse
import sys
import os
import time
from datetime import datetime
from collections import Counter
import numpy as np

try:
    from fer.fer import FER
except ImportError:
    print("ERROR: FER library not found. Please install it using:")
    print("pip install fer")
    sys.exit(1)


class FacialSentimentAnalyzer:
    """
    A class for real-time facial sentiment analysis using webcam.
    
    Attributes:
        camera_index (int): Index of the camera to use
        use_mtcnn (bool): Whether to use MTCNN detector (accurate) or OpenCV (fast)
        detector: FER emotion detector instance
        cap: OpenCV video capture object
        emotion_colors (dict): Mapping of emotions to BGR colors
        emotion_counts (Counter): Counter for emotion statistics
        frame_count (int): Total number of frames processed
    """
    
    # Color coding for emotions (BGR format for OpenCV)
    EMOTION_COLORS = {
        'happy': (0, 255, 0),      # Green
        'sad': (255, 0, 0),        # Blue
        'angry': (0, 0, 255),      # Red
        'neutral': (255, 255, 0),  # Cyan
        'surprise': (0, 255, 255), # Yellow
        'fear': (128, 0, 128),     # Purple
        'disgust': (0, 165, 255)   # Orange
    }
    
    def __init__(self, camera_index=0, use_mtcnn=False):
        """
        Initialize the Facial Sentiment Analyzer.
        
        Args:
            camera_index (int): Index of the camera to use (default: 0)
            use_mtcnn (bool): Use MTCNN detector if True, OpenCV if False (default: False)
        """
        self.camera_index = camera_index
        self.use_mtcnn = use_mtcnn
        self.detector = None
        self.cap = None
        self.emotion_counts = Counter()
        self.frame_count = 0
        
        print("=" * 60)
        print("Facial Sentiment Analysis Application")
        print("=" * 60)
        
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the emotion detector with specified backend."""
        detector_type = "MTCNN (Accurate)" if self.use_mtcnn else "OpenCV (Fast)"
        print(f"\n🔧 Initializing {detector_type} detector...")
        
        try:
            if self.use_mtcnn:
                self.detector = FER(mtcnn=True)
            else:
                self.detector = FER(mtcnn=False)
            
            print(f"✓ {detector_type} detector initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing detector: {e}")
            sys.exit(1)
    
    def start_camera(self):
        """
        Start the video capture from the specified camera.
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        print(f"\n📹 Starting camera (index: {self.camera_index})...")
        
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"✗ Error: Could not open camera {self.camera_index}")
            print("  Try a different camera index (0, 1, 2, etc.)")
            return False
        
        # Give camera time to initialize and test
        time.sleep(1.0)  # Important: Give camera time to fully initialize
        
        # Clear buffer and test read
        for _ in range(5):
            self.cap.read()
        
        ret, test_frame = self.cap.read()
        
        if not ret or test_frame is None:
            print(f"✗ Error: Camera opened but cannot read frames")
            print("  This is usually a permissions issue on macOS")
            print("  Go to: System Preferences > Security & Privacy > Camera")
            print("  Make sure Terminal or Python has camera access")
            self.cap.release()
            return False
        
        height, width = test_frame.shape[:2]
        print(f"✓ Camera started successfully ({width}x{height})")
        return True
    
    def analyze_frame(self, frame):
        """
        Analyze a single frame for emotions.
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            list: List of emotion analysis results for detected faces
        """
        try:
            # Detect emotions in the frame
            result = self.detector.detect_emotions(frame)
            
            # Boost happy emotion score to make it easier to detect
            if result:
                for face_data in result:
                    emotions = face_data['emotions']
                    if 'happy' in emotions:
                        # Multiply happy score by 1.5 (adjust this value: 1.2-2.0)
                        emotions['happy'] *= 1.5
                        
                        # Renormalize so all emotions still sum to 1
                        total = sum(emotions.values())
                        for emotion in emotions:
                            emotions[emotion] /= total
            
            return result if result else []
        except Exception as e:
            print(f"Warning: Error analyzing frame: {e}")
            return []
    
    def draw_emotion_label(self, frame, x, y, emotion, confidence):
        """
        Draw emotion label with confidence score above the face.
        
        Args:
            frame: OpenCV image frame
            x, y: Top-left coordinates
            emotion: Emotion label
            confidence: Confidence score (0-1)
        """
        label = f"{emotion}: {confidence:.1%}"
        
        # Create background for text
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x, y - text_height - 10),
            (x + text_width + 10, y),
            self.EMOTION_COLORS.get(emotion, (255, 255, 255)),
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            label,
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )
    
    def draw_emotion_bars(self, frame, x, y, w, h, emotions):
        """
        Draw confidence bars for top 3 emotions below the face.
        
        Args:
            frame: OpenCV image frame
            x, y, w, h: Face bounding box coordinates
            emotions: Dictionary of emotion scores
        """
        # Sort emotions by confidence
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        bar_height = 15
        bar_spacing = 5
        start_y = y + h + 10
        max_bar_width = w
        
        for idx, (emotion, score) in enumerate(sorted_emotions):
            bar_y = start_y + idx * (bar_height + bar_spacing)
            bar_width = int(max_bar_width * score)
            
            # Draw background bar
            cv2.rectangle(
                frame,
                (x, bar_y),
                (x + max_bar_width, bar_y + bar_height),
                (50, 50, 50),
                -1
            )
            
            # Draw filled bar
            cv2.rectangle(
                frame,
                (x, bar_y),
                (x + bar_width, bar_y + bar_height),
                self.EMOTION_COLORS.get(emotion, (255, 255, 255)),
                -1
            )
            
            # Draw emotion label
            label = f"{emotion}: {score:.1%}"
            cv2.putText(
                frame,
                label,
                (x + 5, bar_y + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )
    
    def draw_results(self, frame, analysis_results):
        """
        Draw all emotion analysis results on the frame.
        
        Args:
            frame: OpenCV image frame
            analysis_results: List of emotion analysis results
        """
        for face_data in analysis_results:
            # Extract face bounding box
            box = face_data['box']
            x, y, w, h = box
            
            # Get emotions
            emotions = face_data['emotions']
            
            # Get dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            emotion_name = dominant_emotion[0]
            confidence = dominant_emotion[1]
            
            # Update emotion statistics
            self.emotion_counts[emotion_name] += 1
            
            # Draw bounding box with emotion color
            color = self.EMOTION_COLORS.get(emotion_name, (255, 255, 255))
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
            
            # Draw emotion label above face
            self.draw_emotion_label(frame, x, y, emotion_name, confidence)
            
            # Draw confidence bars below face (commented out - only showing main emotion)
            # self.draw_emotion_bars(frame, x, y, w, h, emotions)
    
    def save_screenshot(self, frame):
        """
        Save the current frame as a screenshot.
        
        Args:
            frame: OpenCV image frame
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotion_screenshot_{timestamp}.png"
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)
        
        cv2.imwrite(filepath, frame)
        print(f"📸 Screenshot saved: {filepath}")
    
    def display_info_panel(self, frame):
        """
        Display information panel with instructions and statistics.
        
        Args:
            frame: OpenCV image frame
        """
        height, width = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        panel_height = 100
        cv2.rectangle(overlay, (0, 0), (width, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Display instructions
        instructions = [
            "Controls: [Q] Quit  [S] Screenshot",
            f"Detector: {'MTCNN (Accurate)' if self.use_mtcnn else 'OpenCV (Fast)'}",
            f"Frames Processed: {self.frame_count}"
        ]
        
        y_pos = 25
        for text in instructions:
            cv2.putText(
                frame,
                text,
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            y_pos += 25
    
    def show_emotion_summary(self):
        """Display emotion statistics summary at the end of the session."""
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        print(f"\nTotal frames processed: {self.frame_count}")
        print(f"Total emotion detections: {sum(self.emotion_counts.values())}")
        
        if self.emotion_counts:
            print("\n📊 Emotion Distribution:")
            print("-" * 40)
            
            total_detections = sum(self.emotion_counts.values())
            
            # Sort emotions by count
            for emotion, count in self.emotion_counts.most_common():
                percentage = (count / total_detections) * 100
                bar_length = int(percentage / 2)  # Scale bar to 50 chars max
                bar = "█" * bar_length
                
                print(f"{emotion:10s} | {bar:50s} {count:4d} ({percentage:5.1f}%)")
        else:
            print("\n⚠ No emotions detected during this session")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Main loop for real-time emotion detection."""
        if not self.start_camera():
            return
        
        print("\n" + "=" * 60)
        print("STARTING REAL-TIME EMOTION DETECTION")
        print("=" * 60)
        print("\n📝 Controls:")
        print("  • Press 'Q' to quit")
        print("  • Press 'S' to save screenshot")
        print("\n🎬 Processing video stream...")
        print("-" * 60)
        
        try:
            consecutive_failures = 0
            max_failures = 10
            
            while True:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print("✗ Error: Failed to capture frame (too many consecutive failures)")
                        print("  Camera may have been disconnected or lost permissions")
                        break
                    time.sleep(0.1)
                    continue
                
                # Reset failure counter on successful read
                consecutive_failures = 0
                
                self.frame_count += 1
                
                # Analyze frame for emotions
                analysis_results = self.analyze_frame(frame)
                
                # Draw results on frame
                if analysis_results:
                    self.draw_results(frame, analysis_results)
                
                # Display info panel
                self.display_info_panel(frame)
                
                # Display the frame
                cv2.imshow('Facial Sentiment Analysis', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    print("\n🛑 Quit command received")
                    break
                elif key == ord('s') or key == ord('S'):
                    self.save_screenshot(frame)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
        
        except Exception as e:
            print(f"\n✗ Error during execution: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources and clean up."""
        print("\n🧹 Cleaning up resources...")
        
        if self.cap is not None:
            self.cap.release()
            print("✓ Camera released")
        
        cv2.destroyAllWindows()
        print("✓ Windows closed")
        
        # Show emotion summary
        self.show_emotion_summary()


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Real-time Facial Sentiment Analysis Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use default camera (0) with fast detector
  %(prog)s --camera 1         # Use camera 1
  %(prog)s --accurate         # Use accurate MTCNN detector
  %(prog)s --camera 1 --accurate  # Use camera 1 with MTCNN detector

Supported Emotions:
  • Happy (Green)
  • Sad (Blue)
  • Angry (Red)
  • Neutral (Cyan)
  • Surprise (Yellow)
  • Fear (Purple)
  • Disgust (Orange)
        """
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        metavar='INDEX',
        help='Camera index to use (default: 0)'
    )
    
    parser.add_argument(
        '--accurate',
        action='store_true',
        help='Use MTCNN detector for higher accuracy (slower)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create and run the analyzer
    analyzer = FacialSentimentAnalyzer(
        camera_index=args.camera,
        use_mtcnn=args.accurate
    )
    
    analyzer.run()


if __name__ == "__main__":
    main()

