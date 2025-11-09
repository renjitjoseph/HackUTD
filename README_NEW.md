# Face Recognition System

A modern web-based face recognition system with automatic registration and real-time detection.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ 
- Node.js 16+
- Webcam

### Installation & Run

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-cors opencv-python deepface numpy tensorflow
python3 app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

Then open **http://localhost:3000** in your browser!

## 📁 Project Structure

```
HackUTD/
├── backend/                    # Flask API server
│   ├── app.py                 # Main Flask application
│   ├── main.py                # Unified system (terminal version)
│   ├── recognize.py           # Face recognition module
│   ├── register.py            # Face registration module
│   ├── requirements.txt       # Python dependencies
│   ├── face_database/         # Stored face images
│   └── face_encodings.pkl     # Face embeddings
│
├── frontend/                   # React web interface
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # Styles
│   ├── public/
│   └── package.json          # Node dependencies
│
├── .gitignore
└── README.md
```

## ✨ Features

- **Live Video Feed** - Real-time face detection and recognition
- **Auto-Registration** - Automatically registers new faces
- **Web Interface** - Beautiful React UI instead of terminal
- **Face Management** - Rename and delete faces via web UI
- **REST API** - Full API for face operations

## 🎯 How It Works

1. **Detection**: System detects faces using OpenCV Haar Cascades
2. **Recognition**: Uses DeepFace with Facenet model for face embeddings
3. **Auto-Register**: Unknown faces get assigned random names (e.g., "Person_ABC123")
4. **Management**: Rename or delete faces through the web interface

## 🔧 API Endpoints

- `GET /video_feed` - Live video stream with face recognition
- `GET /api/faces` - Get all registered faces
- `GET /api/stats` - System statistics
- `POST /api/rename` - Rename a person
- `POST /api/delete` - Delete a person

## 📝 Notes

- Backend runs on port **5001** (not 5000 due to macOS AirPlay)
- Frontend runs on port **3000**
- Face data stored in `backend/face_database/`
- Requires good lighting for best results

## 🛠️ Technologies

**Backend:**
- Flask - Web framework
- DeepFace - Face recognition
- OpenCV - Computer vision
- TensorFlow - Deep learning

**Frontend:**
- React - UI framework
- Axios - HTTP client
- Lucide React - Icons

## 📄 License

MIT License
