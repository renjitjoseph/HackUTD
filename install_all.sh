#!/bin/bash

echo "🚀 Installing ALL dependencies for Sales Call Analyzer..."
echo "=================================================="
echo ""

# Make sure we're in the right directory
cd /Users/harsh/Documents/GitHub/HackUTD

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install all dependencies
echo ""
echo "📦 Installing packages (this may take 2-3 minutes)..."
echo ""

pip install --upgrade pip

pip install pyaudio==0.2.14 \
    SpeechRecognition==3.10.4 \
    openai-whisper==20231117 \
    google-genai \
    python-dotenv==1.0.0 \
    pyttsx3==2.90 \
    fer==22.5.1 \
    tensorflow==2.15.0 \
    keras==2.15.0 \
    opencv-python==4.10.0.84 \
    numpy

echo ""
echo "=================================================="
echo "🧪 Testing installation..."
echo ""

python3 -c "
import sys
try:
    import pyaudio
    print('✅ PyAudio: OK')
except ImportError as e:
    print('❌ PyAudio: FAILED')
    sys.exit(1)

try:
    import speech_recognition
    print('✅ SpeechRecognition: OK')
except ImportError:
    print('❌ SpeechRecognition: FAILED')
    sys.exit(1)

try:
    import whisper
    print('✅ Whisper: OK')
except ImportError:
    print('❌ Whisper: FAILED')
    sys.exit(1)

try:
    from google import genai
    print('✅ Google Genai: OK')
except ImportError:
    print('❌ Google Genai: FAILED')
    sys.exit(1)

try:
    import pyttsx3
    print('✅ PyTTSx3: OK')
except ImportError:
    print('❌ PyTTSx3: FAILED')
    sys.exit(1)

try:
    import fer
    print('✅ FER: OK')
except ImportError:
    print('❌ FER: FAILED')
    sys.exit(1)

try:
    import tensorflow
    print('✅ TensorFlow: OK')
except ImportError:
    print('❌ TensorFlow: FAILED')
    sys.exit(1)

try:
    import cv2
    print('✅ OpenCV: OK')
except ImportError:
    print('❌ OpenCV: FAILED')
    sys.exit(1)

print('')
print('🎉 ALL PACKAGES INSTALLED SUCCESSFULLY!')
print('')
print('Next steps:')
print('1. Make sure .env file has your GEMINI_API_KEY')
print('2. Run: cd backend && python3 sales_call_analyzer.py')
"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "=================================================="
    echo "✅ Installation complete! You're ready to go."
    echo "=================================================="
else
    echo ""
    echo "=================================================="
    echo "❌ Installation had some issues."
    echo "Check the error messages above."
    echo "=================================================="
fi

exit $EXIT_CODE

