import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Camera, Users, Edit2, Trash2, Check, X, RefreshCw, Mic, MicOff } from 'lucide-react';
import './App.css';

function App() {
  const [faces, setFaces] = useState([]);
  const [stats, setStats] = useState({ total_faces: 0, model: '', threshold: 0 });
  const [editingId, setEditingId] = useState(null);
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(false);
  const [transcriptions, setTranscriptions] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const eventSourceRef = useRef(null);
  const [selectedFace, setSelectedFace] = useState(null);
  const [currentData, setCurrentData] = useState({ person: null, confidence: 0, emotion: null, emotion_confidence: 0 });

  const API_URL = 'http://localhost:5001';

  const startListening = async () => {
    try {
      await axios.post(`${API_URL}/api/speech/start`);
      setIsListening(true);
      
      // Connect to SSE stream
      eventSourceRef.current = new EventSource(`${API_URL}/api/speech/stream`);
      
      eventSourceRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.text) {
          setTranscriptions(prev => [
            { text: data.text, timestamp: data.timestamp },
            ...prev.slice(0, 9) // Keep last 10 transcriptions
          ]);
        }
      };
      
      eventSourceRef.current.onerror = (error) => {
        console.error('SSE Error:', error);
      };
    } catch (error) {
      console.error('Error starting speech recognition:', error);
    }
  };

  const stopListening = async () => {
    try {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      await axios.post(`${API_URL}/api/speech/stop`);
      setIsListening(false);
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
  };

  useEffect(() => {
    fetchFaces();
    fetchStats();
    fetchCurrentData();
    
    // Auto-start speech recognition after a short delay
    const startTimer = setTimeout(() => {
      startListening();
    }, 1000);
    
    const interval = setInterval(() => {
      fetchFaces();
      fetchStats();
      fetchCurrentData();
    }, 500); // Update more frequently for real-time data
    
    return () => {
      clearTimeout(startTimer);
      clearInterval(interval);
      stopListening();
    };
  }, []);

  const fetchFaces = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/faces`);
      setFaces(response.data.faces);
    } catch (error) {
      console.error('Error fetching faces:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchCurrentData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/current`);
      setCurrentData(response.data);
    } catch (error) {
      console.error('Error fetching current data:', error);
    }
  };

  const handleRename = async (oldName) => {
    if (!newName.trim()) {
      alert('Please enter a valid name');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/rename`, {
        old_name: oldName,
        new_name: newName.trim()
      });

      if (response.data.success) {
        await fetchFaces();
        setEditingId(null);
        setNewName('');
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error renaming face:', error);
      alert('Error renaming face');
    }
    setLoading(false);
  };

  const handleDelete = async (name) => {
    if (!window.confirm(`Are you sure you want to delete ${name}?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/delete`, {
        name: name
      });

      if (response.data.success) {
        await fetchFaces();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error deleting face:', error);
      alert('Error deleting face');
    }
    setLoading(false);
  };

  const startEdit = (name) => {
    setEditingId(name);
    setNewName(name);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setNewName('');
  };

  const openFaceModal = (face) => {
    setSelectedFace(face);
    setNewName(face.name);
  };

  const closeFaceModal = () => {
    setSelectedFace(null);
    setNewName('');
  };

  const handleModalRename = async () => {
    if (!newName.trim() || !selectedFace) return;
    await handleRename(selectedFace.name);
    closeFaceModal();
  };

  const handleModalDelete = async () => {
    if (!selectedFace) return;
    await handleDelete(selectedFace.name);
    closeFaceModal();
  };


  return (
    <div className="App">
      <main className="main-content">
        <div className="video-section">
          <div className="video-container">
            <img 
              src={`${API_URL}/video_feed`} 
              alt="Live Video Feed" 
              className="video-feed"
            />
            <div className="video-overlay">
              <div className="live-indicator">
                <span className="pulse"></span>
                LIVE
              </div>
            </div>
          </div>
        </div>
        
        <div className="video-section">
          <div className="video-container">
            <img 
              src={`${API_URL}/emotion_feed`} 
              alt="Emotion Detection Feed" 
              className="video-feed"
            />
            <div className="video-overlay">
              <div className="live-indicator emotion-indicator">
                <span className="pulse"></span>
                EMOTION
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <div className="right-side-container">
        <div className="right-side-content">
          <h3>Current Detection</h3>
          
          {currentData.person ? (
            <div className="detection-info">
              <div className="detection-item">
                <div className="detection-label">Person</div>
                <div className="detection-value person-name">{currentData.person}</div>
              </div>
              
              <div className="detection-item">
                <div className="detection-label">Recognition Confidence</div>
                <div className="detection-value">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${currentData.confidence}%` }}
                    ></div>
                  </div>
                  <span className="confidence-text">{currentData.confidence.toFixed(1)}%</span>
                </div>
              </div>
              
              {currentData.emotion && (
                <>
                  <div className="detection-item">
                    <div className="detection-label">Emotion</div>
                    <div className="detection-value emotion-name">{currentData.emotion}</div>
                  </div>
                  
                  <div className="detection-item">
                    <div className="detection-label">Emotion Confidence</div>
                    <div className="detection-value">
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill emotion-fill" 
                          style={{ width: `${currentData.emotion_confidence}%` }}
                        ></div>
                      </div>
                      <span className="confidence-text">{currentData.emotion_confidence.toFixed(1)}%</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="no-detection">
              <Users size={64} />
              <p>No person detected</p>
            </div>
          )}
        </div>
      </div>
      
      <div className="bottom-left-box">
        <div className="faces-grid-compact">
          {faces.length === 0 ? (
            <div className="empty-state-compact">
              <Users size={32} />
              <p>No faces registered</p>
            </div>
          ) : (
            faces.map((face) => (
              <div key={face.name} className="face-card-compact">
                <div className="face-image-container-compact" onClick={() => openFaceModal(face)}>
                  {face.image ? (
                    <img 
                      src={`data:image/jpeg;base64,${face.image}`} 
                      alt={face.name}
                      className="face-image-compact"
                    />
                  ) : (
                    <div className="face-placeholder-compact">
                      <Users size={24} />
                    </div>
                  )}
                </div>
                <div className="face-name-compact">{face.name}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {selectedFace && (
        <div className="modal-overlay" onClick={closeFaceModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Face</h2>
              <button className="modal-close" onClick={closeFaceModal}>
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="modal-face-preview">
                {selectedFace.image ? (
                  <img 
                    src={`data:image/jpeg;base64,${selectedFace.image}`} 
                    alt={selectedFace.name}
                    className="modal-face-image"
                  />
                ) : (
                  <div className="modal-face-placeholder">
                    <Users size={48} />
                  </div>
                )}
              </div>
              
              <div className="modal-input-group">
                <label>Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="modal-input"
                  placeholder="Enter name"
                />
              </div>
            </div>
            
            <div className="modal-actions">
              <button 
                className="modal-btn modal-btn-delete"
                onClick={handleModalDelete}
                disabled={loading}
              >
                <Trash2 size={18} />
                Delete
              </button>
              <button 
                className="modal-btn modal-btn-save"
                onClick={handleModalRename}
                disabled={loading}
              >
                <Check size={18} />
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
