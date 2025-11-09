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
    
    // Auto-start speech recognition after a short delay
    const startTimer = setTimeout(() => {
      startListening();
    }, 1000);
    
    const interval = setInterval(() => {
      fetchFaces();
      fetchStats();
    }, 3000);
    
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


  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <Camera size={32} />
            <h1>Face Recognition System</h1>
          </div>
          <div className="stats">
            <div className="stat-item">
              <Users size={20} />
              <span>{stats.total_faces} Faces</span>
            </div>
            <div className="stat-item">
              <span className="model-badge">{stats.model}</span>
            </div>
          </div>
        </div>
      </header>

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
          
          <div className="transcription-section">
            <div className="transcription-header">
              <h3>Live Transcription</h3>
              <div className={`mic-status ${isListening ? 'active' : ''}`}>
                <Mic size={20} />
                <span>{isListening ? 'Listening...' : 'Starting...'}</span>
              </div>
            </div>
            <div className="transcription-content">
              {transcriptions.length === 0 ? (
                <div className="transcription-empty">
                  <Mic size={32} />
                  <p>{isListening ? 'Listening... Speak now!' : 'Click Start to begin transcription'}</p>
                </div>
              ) : (
                <>
                  <div className="current-caption">
                    <div className="caption-text">{transcriptions[0].text}</div>
                  </div>
                  {transcriptions.length > 1 && (
                    <div className="previous-captions">
                      {transcriptions.slice(1).map((item, index) => (
                        <div key={index} className="previous-caption">
                          {item.text}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        <div className="faces-section">
          <div className="section-header">
            <h2>
              <Users size={24} />
              Registered Faces ({faces.length})
            </h2>
            <button className="refresh-btn" onClick={fetchFaces}>
              <RefreshCw size={18} />
              Refresh
            </button>
          </div>

          <div className="faces-grid">
            {faces.length === 0 ? (
              <div className="empty-state">
                <Users size={48} />
                <p>No faces registered yet</p>
                <p className="empty-subtitle">Stand in front of the camera to register</p>
              </div>
            ) : (
              faces.map((face) => (
                <div key={face.name} className="face-card">
                  <div className="face-image-container">
                    {face.image ? (
                      <img 
                        src={`data:image/jpeg;base64,${face.image}`} 
                        alt={face.name}
                        className="face-image"
                      />
                    ) : (
                      <div className="face-placeholder">
                        <Users size={40} />
                      </div>
                    )}
                  </div>
                  
                  <div className="face-info">
                    {editingId === face.name ? (
                      <div className="edit-form">
                        <input
                          type="text"
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          className="edit-input"
                          placeholder="Enter new name"
                          autoFocus
                        />
                        <div className="edit-actions">
                          <button 
                            className="btn-icon btn-success"
                            onClick={() => handleRename(face.name)}
                            disabled={loading}
                          >
                            <Check size={16} />
                          </button>
                          <button 
                            className="btn-icon btn-cancel"
                            onClick={cancelEdit}
                            disabled={loading}
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h3 className="face-name">{face.name}</h3>
                        <div className="face-actions">
                          <button 
                            className="btn-icon btn-edit"
                            onClick={() => startEdit(face.name)}
                            title="Rename"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button 
                            className="btn-icon btn-delete"
                            onClick={() => handleDelete(face.name)}
                            title="Delete"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
