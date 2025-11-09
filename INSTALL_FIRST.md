# 📦 INSTALL EVERYTHING FIRST - Run Before Testing

Run these commands **in order** before running the sales call analyzer:

## Step 1: Activate Virtual Environment

```bash
cd /Users/harsh/Documents/GitHub/HackUTD
source venv/bin/activate
```

## Step 2: Install All Dependencies

### Core Audio Dependencies (Required)
```bash
pip install pyaudio==0.2.14
pip install SpeechRecognition==3.10.4
pip install openai-whisper==20231117
```

### Gemini AI (Required)
```bash
pip install google-genai
pip install python-dotenv==1.0.0
```

### Text-to-Speech (Required)
```bash
pip install pyttsx3==2.90
```

### Facial Sentiment Analysis (Required for facial features)
```bash
pip install fer==22.5.1
pip install tensorflow==2.15.0
pip install keras==2.15.0
pip install opencv-python==4.10.0.84
```

## Step 3: ONE-COMMAND Install (Alternative)

Or just run this ONE command to install everything:

```bash
cd /Users/harsh/Documents/GitHub/HackUTD
source venv/bin/activate
pip install pyaudio==0.2.14 SpeechRecognition==3.10.4 openai-whisper==20231117 google-genai python-dotenv==1.0.0 pyttsx3==2.90 fer==22.5.1 tensorflow==2.15.0 keras==2.15.0 opencv-python==4.10.0.84
```

## Step 4: Verify Installation

Test that everything is installed:

```bash
python3 -c "import pyaudio; import speech_recognition; import whisper; import fer; import cv2; from google import genai; import pyttsx3; print('✅ All packages installed successfully!')"
```

If you see `✅ All packages installed successfully!`, you're ready to run the system!

## Step 5: Set API Key

Create `.env` file in project root:

```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

Replace `your-api-key-here` with your actual key from: https://aistudio.google.com/apikey

## Step 6: Run the System

```bash
cd backend
python3 sales_call_analyzer.py
```

---

## 🚨 If You Get Errors

### PyAudio Error (Mac)
```bash
brew install portaudio
pip install pyaudio
```

### TensorFlow Error
```bash
pip install --upgrade tensorflow
```

### Camera Permissions (Mac)
Go to: **System Preferences > Security & Privacy > Camera**
- Enable camera access for Terminal or Python

### Audio Permissions (Mac)
Go to: **System Preferences > Security & Privacy > Microphone**
- Enable microphone access for Terminal or Python

---

## 📋 Quick Copy-Paste Version

```bash
cd /Users/harsh/Documents/GitHub/HackUTD
source venv/bin/activate
pip install pyaudio==0.2.14 SpeechRecognition==3.10.4 openai-whisper==20231117 google-genai python-dotenv==1.0.0 pyttsx3==2.90 fer==22.5.1 tensorflow==2.15.0 keras==2.15.0 opencv-python==4.10.0.84
python3 -c "import pyaudio; import speech_recognition; import whisper; import fer; import cv2; from google import genai; import pyttsx3; print('✅ All installed!')"
```

Done? Now run:
```bash
cd backend
python3 sales_call_analyzer.py
```

