#!/usr/bin/env python3
"""Test which cameras are available on the system."""

import cv2

print("Testing available cameras...\n")

available_cameras = []

for i in range(5):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    
    if ret and frame is not None:
        height, width = frame.shape[:2]
        print(f"✓ Camera {i}: Available ({width}x{height})")
        available_cameras.append(i)
    else:
        print(f"✗ Camera {i}: Not available")
    
    cap.release()

print(f"\n{'='*50}")
if available_cameras:
    print(f"Found {len(available_cameras)} working camera(s): {available_cameras}")
    print(f"\nTry running with: python facial_sentiment_analyzer.py --camera {available_cameras[0]}")
else:
    print("No working cameras found!")
    print("\n⚠️  Common issues on macOS:")
    print("  1. Grant camera permissions: System Preferences > Security & Privacy > Camera")
    print("  2. Close other apps using the camera (Zoom, Skype, etc.)")
    print("  3. Restart Terminal to apply permission changes")
print('='*50)

