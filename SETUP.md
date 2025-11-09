# 🚀 Face Recognition System - Setup Guide

## 📁 Clean Project Structure

```
HackUTD/
├── backend/                      # All Python backend code
│   ├── app.py                   # Flask API (WEB VERSION)
│   ├── main.py                  # Terminal version with voice
│   ├── recognize.py             # Recognition module
│   ├── register.py              # Registration module
│   ├── requirements.txt         # Python dependencies
│   ├── face_database/           # Face images (auto-created)
│   ├── face_encodings.pkl       # Face data (auto-created)
│   └── venv/                    # Virtual environment (create this)
│
├── frontend/                     # React web interface
│   ├── src/
│   │   ├── App.js              # Main component
│   │   ├── App.css             # Styles
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── node_modules/            # (auto-created by npm install)
│
├── .gitignore                    # Git ignore rules
├── start_frontend.sh            # Auto-start script
└── README_NEW.md                # Main documentation
```

## ⚡ Quick Start Commands

### Option 1: Automatic (Easiest)
```bash
./start_frontend.sh
```

### Option 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors opencv-python deepface numpy tensorflow
python3 app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

## 🎯 Access the App

Open **http://localhost:3000** in your browser

- Backend API: http://localhost:5001
- Frontend UI: http://localhost:3000

## 📝 What Got Organized

### Moved to `backend/`:
- ✅ `main.py` - Terminal version
- ✅ `recognize.py` - Recognition logic
- ✅ `register.py` - Registration logic
- ✅ `face_database/` - Face images
- ✅ `face_encodings.pkl` - Face data

### Cleaned Up:
- ✅ Removed root `venv/` (each backend creates its own)
- ✅ Moved old `requirements.txt` to `backend/old_requirements.txt`
- ✅ Added `.gitignore` to exclude venv, node_modules, face data
- ✅ Updated all paths in `app.py`

### Documentation:
- ✅ `README_NEW.md` - Clean main README
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `FRONTEND_SETUP.md` - Detailed setup
- ✅ `SETUP.md` - This file

## 🔧 Different Versions

### Web Version (Recommended)
```bash
cd backend
source venv/bin/activate
python3 app.py
```
Then open http://localhost:3000 for the React UI

### Terminal Version (Original)
```bash
cd backend
source venv/bin/activate
python3 main.py
```
Includes voice recognition and terminal output

### Simple Recognition Only
```bash
cd backend
source venv/bin/activate
python3 recognize.py
```

### Simple Registration Only
```bash
cd backend
source venv/bin/activate
python3 register.py
```

## 🛑 Stop All Servers

```bash
# Kill all ports
lsof -ti:3000 | xargs kill -9
lsof -ti:5001 | xargs kill -9
```

Or just press `Ctrl+C` in each terminal

## ✨ Next Steps

1. Run the quick start commands above
2. Allow camera permissions when prompted
3. Stand in front of camera to register
4. Click edit icon to rename yourself
5. Enjoy the web interface!
