#!/bin/bash

# Setup script for voice transcription on Mac
# This installs all dependencies needed for FREE local transcription

echo "=================================================="
echo "Voice Transcription Setup for Mac"
echo "=================================================="
echo ""

# Check if we're on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Not in a virtual environment. Activating venv..."
    
    # Check if venv exists
    if [[ ! -d "venv" ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

echo ""
echo "=================================================="
echo "Installing Dependencies"
echo "=================================================="
echo ""

# Install system dependencies for PyAudio
echo "📦 Installing system dependencies (portaudio)..."
echo "   This is needed for PyAudio to access your microphone"

if command -v brew &> /dev/null; then
    echo "   Using Homebrew to install portaudio..."
    brew install portaudio
else
    echo "⚠️  Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install portaudio
fi

echo ""
echo "📦 Installing Python packages..."

# Upgrade pip
pip install --upgrade pip

# Install packages one by one for better error handling
echo ""
echo "📦 Installing PyAudio (microphone access)..."
pip install pyaudio

echo ""
echo "📦 Installing NumPy (audio processing)..."
pip install numpy

echo ""
echo "📦 Installing OpenAI Whisper (FREE local transcription)..."
echo "   Note: First run will download ~140MB model (one-time only)"
pip install openai-whisper

echo ""
echo "📦 Installing SpeechRecognition (alternative transcription)..."
pip install SpeechRecognition

echo ""
echo "📦 Installing Google Generative AI (for Gemini API)..."
pip install google-generativeai

echo ""
echo "📦 Installing python-dotenv (for .env file support)..."
pip install python-dotenv

echo ""
echo "=================================================="
echo "Testing Microphone Access"
echo "=================================================="
echo ""

# Test microphone access
python3 << 'EOF'
import pyaudio
print("🎤 Testing microphone access...")
try:
    p = pyaudio.PyAudio()
    
    # List available input devices
    print("\n📋 Available audio input devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"   [{i}] {info['name']}")
    
    # Try to open default input
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )
    stream.close()
    p.terminate()
    
    print("\n✅ Microphone access working!")
except Exception as e:
    print(f"\n❌ Microphone test failed: {e}")
    print("\n⚠️  You may need to grant microphone permissions:")
    print("   System Settings > Privacy & Security > Microphone")
    print("   Make sure Terminal/iTerm has permission")
EOF

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "🎉 All dependencies installed successfully!"
echo ""
echo "=================================================="
echo "Next Step: Setup API Key"
echo "=================================================="
echo ""
echo "1. Get your FREE Gemini API key:"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo "2. Create .env file:"
echo "   cp env_template.txt .env"
echo ""
echo "3. Edit .env and add your key:"
echo "   GEMINI_API_KEY=your-api-key-here"
echo ""
echo "Then run:"
echo "   cd backend"
echo "   python3 sales_call_analyzer.py"
echo ""
echo "Or test transcription only (no API key needed):"
echo "   python3 voice_transcription_local.py"
echo ""
echo "=================================================="

