# Face Recognition System - React Frontend Setup

This is a modern React-based web interface for the face recognition system that replaces the terminal-based interface.

## Features

- **Live Video Feed**: Real-time webcam feed with face detection and recognition
- **Face Database**: View all registered faces with their images
- **Rename Faces**: Easily rename any registered person
- **Delete Faces**: Remove faces from the database
- **Auto-Registration**: Automatically registers new faces when detected
- **Modern UI**: Beautiful, responsive design with gradient backgrounds

## Architecture

### Backend (Flask)
- **Port**: 5001 (changed from 5000 to avoid macOS AirPlay conflicts)
- **Video Streaming**: `/video_feed` endpoint streams live video with face recognition
- **REST API**: 
  - `GET /api/faces` - Get all registered faces
  - `GET /api/stats` - Get system statistics
  - `POST /api/rename` - Rename a person
  - `POST /api/delete` - Delete a person

### Frontend (React)
- **Port**: 3000
- **Components**: Single-page application with live video and face management
- **Auto-refresh**: Automatically updates face list every 3 seconds

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5001`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The frontend will automatically open in your browser at `http://localhost:3000`

## Usage

1. **Start Both Servers**:
   - Terminal 1: Run Flask backend (`cd backend && source ../venv/bin/activate && python3 app.py`)
   - Terminal 2: Run React frontend (`cd frontend && npm start`)

2. **Access the Application**:
   - Open your browser to `http://localhost:3000`
   - Allow camera permissions when prompted
   - Backend API runs on `http://localhost:5001`

3. **Register New Faces**:
   - Stand in front of the camera
   - The system will automatically detect and register new faces with random names (e.g., "Person_ABC123")

4. **Rename Faces**:
   - Click the edit icon (pencil) on any face card
   - Enter the new name
   - Click the checkmark to save

5. **Delete Faces**:
   - Click the delete icon (trash) on any face card
   - Confirm the deletion

## Project Structure

```
HackUTD/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   └── package.json        # Node dependencies
├── face_database/          # Stored face images
├── face_encodings.pkl      # Face embeddings database
└── FRONTEND_SETUP.md       # This file
```

## Technologies Used

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **OpenCV**: Computer vision and video processing
- **DeepFace**: Face recognition with Facenet model
- **NumPy**: Numerical computations

### Frontend
- **React**: UI framework
- **Axios**: HTTP client
- **Lucide React**: Icon library
- **CSS3**: Modern styling with gradients and animations

## Troubleshooting

### Camera Not Working
- Make sure no other application is using the camera
- Check browser permissions for camera access
- Restart the Flask backend

### Connection Issues
- Ensure both backend (port 5000) and frontend (port 3000) are running
- Check that CORS is enabled in the Flask app
- Clear browser cache and reload

### Face Recognition Not Working
- Ensure good lighting conditions
- Face the camera directly
- Wait for the system to process (happens every 15 frames)

## API Endpoints

### GET /video_feed
Returns MJPEG stream of video with face recognition overlays

### GET /api/faces
Returns JSON array of all registered faces with base64 encoded images
```json
{
  "faces": [
    {
      "name": "John",
      "image": "base64_encoded_image_data"
    }
  ],
  "count": 1
}
```

### GET /api/stats
Returns system statistics
```json
{
  "total_faces": 5,
  "model": "Facenet",
  "threshold": 10.0
}
```

### POST /api/rename
Rename a person in the database
```json
{
  "old_name": "Person_ABC123",
  "new_name": "John"
}
```

### POST /api/delete
Delete a person from the database
```json
{
  "name": "John"
}
```

## Future Enhancements

- Voice recognition integration for automatic naming
- Face search functionality
- Export/import database
- Multiple camera support
- Face recognition confidence scores
- Dark mode toggle

## Notes

- The system uses the Facenet model for face recognition
- Recognition threshold is set to 10.0 (lower = stricter matching)
- New faces are automatically registered with a 5-second cooldown
- Face images are stored in the `face_database` directory
- Face encodings are stored in `face_encodings.pkl`
