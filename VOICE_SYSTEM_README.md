# 🎤🎥 Sales Call Voice + Facial Analysis System

Real-time voice transcription + facial sentiment + AI strategic insights for sales calls.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
./setup_voice_transcription.sh
```

### 2. Set API Key
Create `.env` file in project root:
```
GEMINI_API_KEY=your-api-key-here
```

Get key from: https://aistudio.google.com/apikey

### 3. Run It
```bash
cd backend
python3 sales_call_analyzer.py
```

Then speak! System will:
- 🎤 Transcribe every 10 seconds
- 🎥 Capture facial emotions (optional)
- 🤖 Analyze with Gemini AI (voice + face)
- 🔊 Speak status out loud
- ⌨️  Press ENTER for recommendations

## 📁 Main Files

```
backend/
├── sales_call_analyzer.py           ⭐ Main system - RUN THIS
├── voice_transcription_local.py     Transcription engine (FREE)
├── facial_sentiment_headless.py     Facial emotion capture (NEW!)
└── voice_transcription.py           Alternative (Google API)
```

## ⚙️ How It Works

1. Records audio continuously (mic)
2. Captures facial emotions continuously (camera, optional)
3. Every 10 seconds: transcribes with Whisper (local, FREE)
4. Aggregates facial emotions over the 10-second window
5. Sends full conversation context + emotions to Gemini
6. Gets strategic insights based on BOTH words AND facial expressions
7. Speaks status out loud via TTS
8. Press ENTER to hear recommendation again

## 💰 Cost

- **Transcription**: $0 (runs locally with Whisper)
- **Facial Analysis**: $0 (runs locally with FER + TensorFlow)
- **AI Analysis**: ~$0.05/hour (Gemini API)

## 🎯 Output Format

Every 10 seconds you see:

```
STATUS: Engaged & Curious

REASON: Customer asking questions and face shows interest (happy 75%)

SAY THIS: "What's your biggest challenge with your current solution?"

SCORE: 7/10
```

And you **hear**: "Engaged and Curious"

**Note**: Facial data is automatically included when camera is available and enabled.

## 🔧 Configuration

### Disable facial sentiment:
In `sales_call_analyzer.py` line 430:
```python
enable_facial=False  # Set to False to disable camera
```

### Change camera:
In `sales_call_analyzer.py` line 429:
```python
camera_index=0  # Change to 1, 2, etc. for external cameras
```

### Change Whisper speed/accuracy:
In `sales_call_analyzer.py` line 428:
```python
model_size="base"   # Current (balanced)
model_size="tiny"   # Faster, less accurate
model_size="small"  # Slower, more accurate
```

### Change time interval:
In `voice_transcription_local.py` line 32:
```python
CHUNK_DURATION = 10  # Change to 5, 15, etc.
```

## ✅ Features

This system includes:
- ✅ Full conversation context (voice)
- ✅ Facial sentiment analysis (emotions)
- ✅ Real-time insights combining both
- ✅ TTS status updates
- ✅ Manual recommendation recall
- ✅ Saves transcripts + emotions + insights to file
- ✅ Graceful fallback to audio-only if camera unavailable

## 🎥 Facial Sentiment Details

The system captures facial emotions every second and aggregates them over 10-second windows:

**Detected Emotions:**
- Happy, Sad, Angry, Neutral
- Surprise, Fear, Disgust

**Analysis Provided:**
- Dominant emotion with confidence
- Emotion breakdown (% for each)
- Trajectory (improving/declining/stable)

**Camera Permissions:**
On macOS, you'll need to grant camera access to Terminal/Python in:
`System Preferences > Security & Privacy > Camera`

---

**Built for HackUTD - Sales Call AI Analysis**

