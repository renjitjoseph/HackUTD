# Facial Recognition System with DeepFace

Real-time facial recognition system that identifies people from webcam feed and **automatically registers new faces**.

## Features
- **Automatic face registration** - New faces are captured and stored automatically
- **Voice-based name assignment** - Say "This is John" to rename people
- Real-time face detection and recognition
- Random name generation for unknown faces (e.g., "Person_A1B2C3")
- Terminal output showing recognized names
- Continuous operation - all scripts run simultaneously
- Uses DeepFace with Facenet model for high accuracy

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **First run will download model files** (this may take a few minutes)

## Usage

### Quick Start (Recommended)
Run the unified system that handles everything automatically:
```bash
python main.py
```

**What it does:**
- Continuously monitors webcam for faces
- **Recognizes known faces** and displays their names (green box)
- **Automatically captures new faces** and assigns random names (orange box)
- **Listens to conversations** and updates names when you say:
  - "This is [Name]"
  - "His/Her name is [Name]"
  - "Meet [Name]"
  - "Call him/her [Name]"
- Stores all faces in the database for future recognition
- Press 'q' to quit

### Manual Registration (Optional)
If you want to register faces with specific names:
```bash
python register.py
```
- Select option 1 to register a new face
- Enter the person's name
- Position your face in the webcam frame
- Press SPACE to capture

### Recognition Only (Optional)
To only recognize without auto-registration:
```bash
python recognize.py
```
- Shows recognized faces in green, unknown in red
- Press 'q' to quit

## How It Works
1. **Face Detection**: Uses OpenCV Haar Cascades to detect faces in frames
2. **Face Encoding**: DeepFace Facenet model creates 128-dimensional embeddings
3. **Face Matching**: Compares embeddings using Euclidean distance
4. **Recognition**: Displays name if distance is below threshold (10.0)
5. **Voice Recognition**: Listens for name patterns in conversation via microphone
6. **Auto-Rename**: Updates most recent "Person_XXX" to the detected real name

## Adjusting Settings

In `main.py`:
- `recognition_threshold = 10.0` - Lower for stricter matching, higher for looser
- `process_every_n_frames = 15` - Process fewer frames for better performance
- `cooldown_duration = 5` - Seconds before re-capturing same unknown face
- `model_name = "Facenet"` - Can use VGG-Face, ArcFace, etc.

## Color Coding
- **Green box**: Known/recognized face
- **Orange box**: Newly registered face
- **Red box**: Unknown face (processing)
- **Gray box**: Face detected but not yet processed

## Voice Command Examples

When a new face is detected (shows as "Person_ABC123"), simply say:
- "This is Sarah"
- "Her name is Michael"
- "Meet David"
- "Call him Alex"

The system will automatically rename the most recent "Person_XXX" to the name you mentioned!

## Troubleshooting

**Webcam not opening:**
- Check camera permissions
- Try changing `cv2.VideoCapture(0)` to `(1)` or `(2)`

**Microphone not working:**
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- On Mac: `brew install portaudio` then `pip install pyaudio`

**Slow performance:**
- Increase `process_every_n_frames` value
- Use a lighter model

**Poor recognition:**
- Register multiple photos of same person
- Adjust threshold value
- Ensure good lighting when registering

**Voice commands not working:**
- Speak clearly and at normal volume
- Ensure internet connection (uses Google Speech Recognition)
- Check terminal for "[HEARD]:" messages to see what's being detected

## License
MIT License - Free for personal and commercial use
