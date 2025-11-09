# 🎭 Real-time Facial Sentiment Analysis

Real-time emotion detection from webcam using Python, OpenCV, and Deep Learning.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python facial_sentiment_analyzer.py
```

## 🎮 Controls

- Press **Q** to quit
- Press **S** to save screenshot

## 📖 Usage

```bash
# Basic usage (default camera, fast mode)
python facial_sentiment_analyzer.py

# Use different camera
python facial_sentiment_analyzer.py --camera 1

# Use accurate mode (MTCNN detector)
python facial_sentiment_analyzer.py --accurate
```

## 🎨 Detected Emotions

- 🟢 **Happy** (Green)
- 🔵 **Sad** (Blue)  
- 🔴 **Angry** (Red)
- 🔵 **Neutral** (Cyan)
- 🟡 **Surprise** (Yellow)
- 🟣 **Fear** (Purple)
- 🟠 **Disgust** (Orange)

## ✨ Features

- Real-time face detection
- 7 emotion categories
- Color-coded bounding boxes
- Confidence scores and bars
- Screenshot capability
- Session summary statistics

## 🔧 Requirements

- Python 3.8+
- Webcam
- ~500MB disk space for models

## 📸 Screenshots

Screenshots are saved to `screenshots/` folder with timestamps.

## 🛠️ Troubleshooting

**Camera not working?**
- macOS: Grant camera permissions in System Preferences > Security & Privacy > Camera
- Try different camera index: `--camera 1`

**Import errors?**
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

---

**Made with ❤️ using Python, OpenCV, and Deep Learning**

