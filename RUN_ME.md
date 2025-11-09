# 🚀 Quick Start - Sales Call Analyzer with Facial Sentiment

## ✅ All packages are already installed!

The FER import issue has been fixed. You're ready to go!

## 🎯 To Run:

```bash
cd /Users/harsh/Documents/GitHub/HackUTD
source venv/bin/activate
cd backend
python3 sales_call_analyzer.py
```

## 🎥 What It Does:

Every 10 seconds:
- 🎤 **Records & transcribes** what the customer says (Whisper)
- 😊 **Captures facial emotions** (FER: happy, sad, confused, etc.)
- 🤖 **Sends both to Gemini** for smart recommendations
- 🔊 **Speaks the status** out loud (TTS)
- ⌨️  **Press ENTER** anytime to hear the latest recommendation

## 🛑 To Stop:

Press `Ctrl+C` (it's normal to see a KeyboardInterrupt message)

## ⚙️ Optional: Disable Camera

If you want audio-only (no facial analysis), edit `sales_call_analyzer.py` line 430:

```python
enable_facial=False  # Set to False to disable camera
```

## 🎯 Example Output:

```
STATUS: Engaged & Curious

REASON: Customer asking questions and face shows interest (happy 75%)

SAY THIS: "What's your biggest challenge right now?"

SCORE: 7/10
```

You'll **hear**: "Engaged and Curious"

Press **ENTER** to hear: "What's your biggest challenge right now?"

---

## 📋 Quick Troubleshooting:

**Camera permissions issue?**
- Go to: System Preferences > Security & Privacy > Camera
- Enable for Terminal/Python

**Microphone permissions issue?**
- Go to: System Preferences > Security & Privacy > Microphone
- Enable for Terminal/Python

**API Key issue?**
- Make sure `.env` file exists in project root
- Contains: `GEMINI_API_KEY=your-actual-key`
- Get key from: https://aistudio.google.com/apikey

---

That's it! Just run the command above and start talking! 🎤

