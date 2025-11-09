# 🚀 Quick Start - React Frontend

## Option 1: Automatic Start (Recommended)

Run both backend and frontend with one command:

```bash
./start_frontend.sh
```

This will:
- Start the Flask backend on port 5001
- Start the React frontend on port 3000
- Automatically open your browser to http://localhost:3000

**Note:** Port 5001 is used instead of 5000 to avoid conflicts with macOS AirPlay Receiver.

## Option 2: Manual Start

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Create venv first if needed: python3 -m venv venv
pip install -r requirements.txt
python app.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install  # Only needed first time
npm start
```

## 🎯 What You'll See

1. **Live Video Feed** - Real-time webcam with face detection boxes
2. **Registered Faces** - Grid of all people in the database
3. **Auto-Registration** - New faces automatically get added with random names
4. **Edit/Delete** - Rename or remove people from the database

## 🎨 Features

- ✅ Live face recognition
- ✅ Auto-register new faces
- ✅ Rename people
- ✅ Delete people
- ✅ Beautiful modern UI
- ✅ Real-time updates

## 📱 Usage

1. Allow camera access when prompted
2. Stand in front of camera to be registered
3. Click edit icon to rename yourself
4. System automatically recognizes you next time!

## 🛑 Stop Servers

Press `Ctrl+C` in each terminal window

## 📚 Full Documentation

See [FRONTEND_SETUP.md](FRONTEND_SETUP.md) for detailed documentation.
