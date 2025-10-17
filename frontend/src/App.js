import React from 'react';
import axios from 'axios';
import { useState, useEffect } from 'react';
import './App.css';
import botImage from './assets/images/bot.png';
import LoginPage from './LoginPage';

// Set up Axios to include the authorization token in headers
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken'); // Retrieve token from localStorage
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

function App() {
  // API endpoints
  const API_BASE = 'http://localhost:8000/api';

  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);

  // FarmBot position state
  const [position, setPosition] = useState({ x: 0, y: 0, z: 0 });
  const [loading, setLoading] = useState(false);
  const [moveForm, setMoveForm] = useState({ x: 0, y: 0, z: 0, speed: 100 });
  const [moveRelForm, setMoveRelForm] = useState({ dx: 0, dy: 0, dz: 0, speed: 100 });
  const [nudgeIntervalId, setNudgeIntervalId] = useState(null);
  const [targetPosition, setTargetPosition] = useState(null);
  const [moveStatus, setMoveStatus] = useState('');
  const [photoData, setPhotoData] = useState([]);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [botVisible, setBotVisible] = useState(true);

  // Authentication functions
  const handleLogin = (token) => {
    setAuthToken(token);
    setIsAuthenticated(true);
    localStorage.setItem('authToken', token);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('authToken');
    // Clear any other user-specific data
    setPhotoData([]);
    setPosition({ x: 0, y: 0, z: 0 });
    setTargetPosition(null);
    setMoveStatus('');
  };

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
    }
  }, []);

  // Fetch position from API
  const fetchPosition = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/position/`);
      console.log('API Response:', response.data);
      const positionArray = response.data;
      
      if (Array.isArray(positionArray) && positionArray.length >= 3) {
        const newPosition = {
          x: positionArray[0],
          y: positionArray[1],
          z: positionArray[2]
        };
        setPosition(newPosition);
        console.log('Updated position:', newPosition);
      }
    } catch (error) {
      console.error('Error fetching position:', error);
      if (error.response && error.response.status === 503) {
        // Bot not connected; keep last known position and show a soft message
        setMoveStatus('Bot not connected');
      } else {
        alert('Error fetching position: ' + error.message);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPosition();
    // Load photos from localStorage on page refresh
    const savedPhotos = localStorage.getItem('farmbot-photos');
    if (savedPhotos) {
      try {
        const parsedPhotos = JSON.parse(savedPhotos);
        // Load the latest photo for all saved photos
        const loadLatestPhoto = async () => {
          try {
            const response = await axios.get(`${API_BASE}/get-latest-photo/`, {
              responseType: 'blob'
            });
            const imageUrl = URL.createObjectURL(response.data);
            
            // Update all photos with the latest image
            const photosWithImages = parsedPhotos.map(photo => ({
              ...photo,
              url: imageUrl
            }));
            setPhotoData(photosWithImages);
          } catch (error) {
            console.error('Error loading latest photo:', error);
            setPhotoData(parsedPhotos);
          }
        };
        loadLatestPhoto();
      } catch (error) {
        console.error('Error loading saved photos:', error);
      }
    }
    // Optionally, poll every few seconds:
    // const interval = setInterval(fetchPosition, 5000);
    // return () => clearInterval(interval);
  }, []);

  const handleGet = async () => {
    try {
      const response = await axios.get(`${API_BASE}/position/`);
      const positionArray = response.data;
      alert('GET response: ' + JSON.stringify(positionArray));
      
      if (Array.isArray(positionArray) && positionArray.length >= 3) {
        const newPosition = {
          x: positionArray[0],
          y: positionArray[1],
          z: positionArray[2]
        };
        setPosition(newPosition);
        console.log('Setting new position:', newPosition);
      }
    } catch (error) {
      console.error('Error in handleGet:', error);
      alert('GET error: ' + error.message);
    }
  };

    const handleMove = async (e) => {
    e.preventDefault();
    setMoveStatus('');
    try {
      const target = {
        x: Number(moveForm.x),
        y: Number(moveForm.y),
        z: Number(moveForm.z),
        speed: Number(moveForm.speed)
      };

      // First unlock the bot
      await axios.post(`${API_BASE}/emergency-unlock/`);
      console.log('Bot unlocked');

      // Then move to position
      setTargetPosition(target);
      setMoveStatus('Moving...');
      
      await axios.post(`${API_BASE}/move-absolute/`, target);
      console.log('Move command sent:', target);
      
      // Start checking position using fresh API reads (avoid stale state)
      let checks = 0;
      const maxChecks = 10; // Check for up to 10 seconds
      const checkPosition = async () => {
        try {
          const res = await axios.get(`${API_BASE}/position/`);
          const arr = res.data;
          if (Array.isArray(arr) && arr.length >= 2) {
            const current = { x: arr[0], y: arr[1] };
            setPosition(current);
            const dx = Math.abs(current.x - target.x);
            const dy = Math.abs(current.y - target.y);
            const distance = Math.sqrt(dx*dx + dy*dy);
            if (distance < 0.5) {
              setMoveStatus('Reached target position');
              return;
            }
          }
        } catch {}
        checks++;
        if (checks < maxChecks) {
          setTimeout(checkPosition, 1000);
        } else {
          setMoveStatus('Warning: Final position may not be exact');
        }
      };
      setTimeout(checkPosition, 2000);
    } catch (error) {
      console.error('Error moving bot:', error);
      setMoveStatus('Error: ' + error.message);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setMoveForm(prev => ({
      ...prev,
      [name]: Number(value)
    }));
  };
  const handleRelInputChange = (e) => {
    const { name, value } = e.target;
    setMoveRelForm(prev => ({
      ...prev,
      [name]: Number(value)
    }));
  };

  // Continuous nudge (D-pad) - single move + polling like manual moves
  const startNudge = (dx, dy, dz = 0) => {
    if (nudgeIntervalId) return;
    const step = { x: dx, y: dy, z: dz };
    const speed = Number(moveRelForm.speed) || 100;
    setMoveStatus('Nudging...');
    
    const performNudge = async () => {
      try {
        // Send single move command
        await axios.post(`${API_BASE}/move-relative/`, { ...step, speed });
        
        // Calculate expected position
        const expected = { x: position.x + step.x, y: position.y + step.y };
        setTargetPosition(expected);
        
        // Poll position until close to expected or timeout
        let checks = 0;
        const maxChecks = 8; // ~8 seconds
        const checkPosition = async () => {
          try {
            const res = await axios.get(`${API_BASE}/position/`);
            const arr = res.data;
            if (Array.isArray(arr) && arr.length >= 2) {
              const current = { x: arr[0], y: arr[1] };
              setPosition(current);
              const dx = Math.abs(current.x - expected.x);
              const dy = Math.abs(current.y - expected.y);
              const distance = Math.sqrt(dx*dx + dy*dy);
              if (distance < 0.5) {
                setMoveStatus('Nudge complete');
                return;
              }
            }
          } catch {}
          checks++;
          if (checks < maxChecks) {
            setTimeout(checkPosition, 1000);
          } else {
            setMoveStatus('Nudge timeout');
          }
        };
        setTimeout(checkPosition, 500);
      } catch (e) {
        setMoveStatus('Nudge failed');
      }
    };
    
    performNudge();
  };
  const stopNudge = () => {
    if (nudgeIntervalId) {
      clearInterval(nudgeIntervalId);
      setNudgeIntervalId(null);
      setMoveStatus('');
    }
  };

  const handleUnlock = async () => {
    try { await axios.post(`${API_BASE}/emergency-unlock/`); setMoveStatus('Unlocked'); }
    catch (e) { setMoveStatus('Unlock failed'); }
  };

  const handleWaterPlant = async () => {
    try {
      setMoveStatus('Watering')
      const response = await axios.post(`${API_BASE}/water-plant/`);
      setMoveStatus('Watering complete');
    } catch (error) {
      console.log('Error watering:', error);
      setMoveStatus('Watering failed');
    }
  };

  const handleTakePhoto = async () => {
    setPhotoLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/take-photo/`, {
        responseType: 'blob'
      });
      
      // Create object URL from blob
      const imageUrl = URL.createObjectURL(response.data);
      const newPhoto = {
        id: Date.now(), // Unique ID for React key
        url: imageUrl,
        position: { ...position }, // Capture current position
        timestamp: new Date().toISOString()
      };
      
      // Add new photo to the array (stacking/overlapping)
      const updatedPhotos = [...photoData, newPhoto];
      setPhotoData(updatedPhotos);
      
      // Save to localStorage (with filename for persistence)
      const photosToSave = updatedPhotos.map(photo => ({
        ...photo,
        url: photo.url ? 'latest' : null // Use 'latest' to indicate we should load the latest photo
      }));
      localStorage.setItem('farmbot-photos', JSON.stringify(photosToSave));
      
      setMoveStatus(`Photo taken successfully (${updatedPhotos.length} photos)`);
    } catch (error) {
      console.error('Error taking photo:', error);
      setMoveStatus('Photo failed');
    } finally {
      setPhotoLoading(false);
    }
  };

  const handleClearPhotos = async () => {
    try {
      // Call backend to delete photos from folder
      await axios.post(`${API_BASE}/clear-photos/`);
      
      // Clean up object URLs to prevent memory leaks
      photoData.forEach(photo => {
        if (photo.url) {
          URL.revokeObjectURL(photo.url);
        }
      });
      
      // Clear from state and localStorage
      setPhotoData([]);
      localStorage.removeItem('farmbot-photos');
      setMoveStatus('All photos cleared');
    } catch (error) {
      console.error('Error clearing photos:', error);
      setMoveStatus('Error clearing photos');
    }
  };

  const handleHome = async () => {
    try {
      await axios.post(`${API_BASE}/find-home/`);
      const target = { x: 0, y: 0 };
      setTargetPosition(target);
      setMoveStatus('Homing...');

      // Poll position until we are near (0,0), similar to move flow
      let checks = 0;
      const maxChecks = 20; // up to 20s
      const checkHome = async () => {
        try {
          const res = await axios.get(`${API_BASE}/position/`);
          const arr = res.data;
          if (Array.isArray(arr) && arr.length >= 2) {
            const current = { x: arr[0], y: arr[1] };
            setPosition(current);
            const dx = Math.abs(current.x - 0);
            const dy = Math.abs(current.y - 0);
            const distance = Math.sqrt(dx*dx + dy*dy);
            if (distance < 0.5) {
              setMoveStatus('Reached home');
              return;
            }
          }
        } catch {}
        checks++;
        if (checks < maxChecks) {
          setTimeout(checkHome, 1000);
        } else {
          setMoveStatus('Warning: Did not reach home exactly');
        }
      };
      setTimeout(checkHome, 2000);
    } catch (e) {
      setMoveStatus('Home failed');
    }
  };


  // Map/grid constants
  const GRID_WIDTH = 2900;
  const GRID_HEIGHT = 1200;
  const CANVAS_WIDTH = 870; // px (scale: 3px per unit) - increased from 580
  const CANVAS_HEIGHT = 360; // px - increased from 240
  const SCALE_X = CANVAS_WIDTH / GRID_WIDTH;
  const SCALE_Y = CANVAS_HEIGHT / GRID_HEIGHT;
  
    // Image overlay constants - 500x300 units on the grid
  const IMAGE_WIDTH_UNITS = 500;
  const IMAGE_HEIGHT_UNITS = 300;
  
  // Calculate image size in pixels based on grid units
  const IMAGE_WIDTH_PX = IMAGE_WIDTH_UNITS * SCALE_X;
  const IMAGE_HEIGHT_PX = IMAGE_HEIGHT_UNITS * SCALE_Y;

  // Calculate FarmBot position on canvas
  const botX = position.x * SCALE_X;
  const botY = position.y * SCALE_Y;

  // Render grid and bot
  const renderMap = () => (
    <div className="map-background" style={{ position: 'relative', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, overflow: 'hidden' }}>
      <svg width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{ border: '1px solid #ccc', background: 'transparent' }}>
        {/* Draw grid lines */}
        {[...Array(30)].map((_, i) => (
          <line key={i} x1={i * (CANVAS_WIDTH / 29)} y1={0} x2={i * (CANVAS_WIDTH / 29)} y2={CANVAS_HEIGHT} stroke="#eee" />
        ))}
        {[...Array(13)].map((_, i) => (
          <line key={i} x1={0} y1={i * (CANVAS_HEIGHT / 12)} x2={CANVAS_WIDTH} y2={i * (CANVAS_HEIGHT / 12)} stroke="#eee" />
        ))}
      </svg>
      
      {/* FarmBot overlay - positioned above photos */}
      {botVisible && (
        <div
          style={{
            position: 'absolute',
            left: botX - 40,
            top: botY - 40,
            width: 80,
            height: 80,
            zIndex: 1000,
            pointerEvents: 'none'
          }}
        >
          <img
            src={botImage}
            alt="FarmBot"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain'
            }}
          />
        </div>
      )}
      
      {/* Display photos as overlays at captured positions */}
      {photoData.map((photo, index) => (
        <div
          key={photo.id}
          style={{
            position: 'absolute',
            left: photo.position.x * SCALE_X - IMAGE_WIDTH_PX / 2,
            top: photo.position.y * SCALE_Y - IMAGE_HEIGHT_PX / 2,
            width: IMAGE_WIDTH_PX,
            height: IMAGE_HEIGHT_PX,
            overflow: 'hidden',
            zIndex: 10 + index // Stack photos with increasing z-index
          }}
        >
          {photo.url ? (
            <img
              src={photo.url}
              alt={`FarmBot Photo ${index + 1}`}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
          ) : (
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: 'rgba(0,0,0,0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '14px'
              }}
            >
              Photo {index + 1}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="App" style={{ padding: 40 }}>
      {/* Main title */}
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <h1 style={{ color: 'white', fontSize: '48px', margin: 0, textShadow: '2px 2px 4px rgba(0,0,0,0.5)' }}>Farmbot</h1>
      </div>

      {/* Top section with title, controls, and move forms */}
      <div className="dirt-background" style={{ display: 'flex', gap: 40, marginBottom: 20, padding: '15px 20px' }}>
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          {/* Controls row */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20, alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 20 }}>
              <button className="stone-button" onClick={handleGet} disabled={loading}>Get Current Position</button>
              <button className="stone-button" onClick={handleUnlock}>Unlock</button>
              <button className="stone-button" onClick={handleWaterPlant}>Water</button>
              <button className="stone-button" onClick={handleHome}>Home</button>
            </div>
            <div style={{ display: 'flex', gap: 20 }}>
              <button className="stone-button" onClick={handleTakePhoto} disabled={photoLoading}>
                {photoLoading ? 'Taking Photo...' : 'Take Photo'}
              </button>
              <button className="stone-button" onClick={handleClearPhotos}>
                Clear Photos ({photoData.length})
              </button>
              <button className="stone-button" onClick={handleLogout} style={{ backgroundColor: '#dc3545' }}>
                Logout
              </button>
            </div>
          </div>

          {/* Status row */}
          <div style={{ display: 'flex', gap: 40, marginBottom: 20, alignItems: 'center' }}>
            <div>
              <strong>Current Position:</strong><br />
              X: {position.x?.toFixed(1)} &nbsp; Y: {position.y?.toFixed(1)} &nbsp; Z: {position.z?.toFixed(1)}
            </div>

            {targetPosition && (
              <div>
                <strong>Target Position:</strong><br />
                X: {targetPosition.x} &nbsp; Y: {targetPosition.y}
              </div>
            )}

            {moveStatus && (
              <div style={{ color: 'white' }}>
                <strong>Status:</strong><br />
                {moveStatus}
              </div>
            )}
          </div>
        </div>

        {/* Move sections */}
        <div style={{ flex: '1', display: 'flex', gap: 40 }}>
          <form onSubmit={handleMove}>
            <h3>Move Absolute</h3>
            <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>X</label>
                <input
                  type="text"
                  name="x"
                  value={moveForm.x}
                  onChange={handleInputChange}
                  style={{ width: '50px', height: '25px' }}
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>Y</label>
                <input
                  type="text"
                  name="y"
                  value={moveForm.y}
                  onChange={handleInputChange}
                  style={{ width: '50px', height: '25px' }}
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>Z</label>
                <input
                  type="text"
                  name="z"
                  value={moveForm.z}
                  onChange={handleInputChange}
                  style={{ width: '50px', height: '25px' }}
                />
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ display: 'block' }}>Speed (%):</label>
              <input
                type="number"
                name="speed"
                value={moveForm.speed}
                onChange={handleInputChange}
                style={{ width: '100px' }}
                min="1"
                max="100"
              />
            </div>
            <button className="stone-button" type="submit" disabled={loading}>Move</button>
          </form>

          <form onSubmit={async (e) => {
            e.preventDefault();
            setMoveStatus('');
            try {
              const delta = {
                x: Number(moveRelForm.dx),
                y: Number(moveRelForm.dy),
                z: Number(moveRelForm.dz),
                speed: Number(moveRelForm.speed)
              };
              await axios.post(`${API_BASE}/emergency-unlock/`);
              const expected = { x: position.x + delta.x, y: position.y + delta.y };
              setTargetPosition(expected);
              setMoveStatus('Moving (relative)...');
              await axios.post(`${API_BASE}/move-relative/`, delta);

              let checks = 0;
              const maxChecks = 10;
              const checkPosition = async () => {
                try {
                  const res = await axios.get(`${API_BASE}/position/`);
                  const arr = res.data;
                  if (Array.isArray(arr) && arr.length >= 2) {
                    const current = { x: arr[0], y: arr[1] };
                    setPosition(current);
                    const dx = Math.abs(current.x - expected.x);
                    const dy = Math.abs(current.y - expected.y);
                    const distance = Math.sqrt(dx*dx + dy*dy);
                    if (distance < 0.5) { setMoveStatus('Reached target position'); return; }
                  }
                } catch {}
                checks++;
                if (checks < maxChecks) setTimeout(checkPosition, 1000);
                else setMoveStatus('Warning: Final position may not be exact');
              };
              setTimeout(checkPosition, 2000);
            } catch (err) {
              setMoveStatus('Error: ' + err.message);
            }
          }}>
            <h3>Move Relative</h3>
            <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>X</label>
                <input type="text" name="dx" value={moveRelForm.dx} onChange={handleRelInputChange} style={{ width: '50px', height: '25px' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>Y</label>
                <input type="text" name="dy" value={moveRelForm.dy} onChange={handleRelInputChange} style={{ width: '50px', height: '25px' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <label style={{ fontSize: '12px', marginBottom: 2 }}>Z</label>
                <input type="text" name="dz" value={moveRelForm.dz} onChange={handleRelInputChange} style={{ width: '50px', height: '25px' }} />
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ display: 'block' }}>Speed (%):</label>
              <input type="number" name="speed" value={moveRelForm.speed} onChange={handleRelInputChange} style={{ width: '100px' }} min="1" max="100" />
            </div>
            <button className="stone-button" type="submit" disabled={loading}>Move</button>
          </form>
        </div>

        {/* D-pad section */}
        <div style={{ flex: '0 0 auto', display: 'flex', gap: 20 }}>
          {/* Z buttons - vertical */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center', justifyContent: 'center' }}>
            <button
              className="stone-button"
              onMouseDown={() => startNudge(0, 0, 5)}
              onMouseUp={stopNudge}
              onMouseLeave={stopNudge}
              onTouchStart={() => startNudge(0, 0, 5)}
              onTouchEnd={stopNudge}
            >Z+</button>
            <button
              className="stone-button"
              onMouseDown={() => startNudge(0, 0, -5)}
              onMouseUp={stopNudge}
              onMouseLeave={stopNudge}
              onTouchStart={() => startNudge(0, 0, -5)}
              onTouchEnd={stopNudge}
            >Z-</button>
          </div>

          {/* Main D-pad */}
          <div>
            <h4>Manual Jog (±5 units)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 60px)', gap: 8, alignItems: 'center', justifyContent: 'start' }}>
              <div />
              <button
                className="stone-button"
                onMouseDown={() => startNudge(0, -5, 0)}
                onMouseUp={stopNudge}
                onMouseLeave={stopNudge}
                onTouchStart={() => startNudge(0, -5, 0)}
                onTouchEnd={stopNudge}
              >↑</button>
              <div />

              <button
                className="stone-button"
                onMouseDown={() => startNudge(-5, 0, 0)}
                onMouseUp={stopNudge}
                onMouseLeave={stopNudge}
                onTouchStart={() => startNudge(-5, 0, 0)}
                onTouchEnd={stopNudge}
              >←</button>
              <div />
              <button
                className="stone-button"
                onMouseDown={() => startNudge(5, 0, 0)}
                onMouseUp={stopNudge}
                onMouseLeave={stopNudge}
                onTouchStart={() => startNudge(5, 0, 0)}
                onTouchEnd={stopNudge}
              >→</button>

              <div />
              <button
                className="stone-button"
                onMouseDown={() => startNudge(0, 5, 0)}
                onMouseUp={stopNudge}
                onMouseLeave={stopNudge}
                onTouchStart={() => startNudge(0, 5, 0)}
                onTouchEnd={stopNudge}
              >↓</button>
              <div />
            </div>
          </div>
        </div>
      </div>

      {/* Main content area with centered grid */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', position: 'relative' }}>
        {/* Bot visibility toggle - positioned in top left of map area */}
        <div className="dirt-background" style={{ position: 'absolute', top: 0, left: 130, display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center', padding: '15px', zIndex: 1000 }}>
          <div style={{ color: 'white', fontSize: '14px' }}>Toggle Bot</div>
          <div 
            onClick={() => setBotVisible(!botVisible)}
            style={{
              width: '30px',
              height: '60px',
              backgroundColor: botVisible ? '#13a73f' : '#666',
              borderRadius: '15px',
              position: 'relative',
              cursor: 'pointer',
              transition: 'background-color 0.3s ease',
              border: '2px solid #fff'
            }}
          >
            <div
              style={{
                width: '26px',
                height: '26px',
                backgroundColor: 'white',
                borderRadius: '50%',
                position: 'absolute',
                top: botVisible ? '2px' : '30px',
                left: '2px',
                transition: 'top 0.3s ease',
                boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}
            />
          </div>
        </div>

        {/* Grid - centered on the page */}
        <div>
          {renderMap()}
        </div>
      </div>

      {/* Logout button in bottom right corner */}
      <button 
        className="stone-button" 
        onClick={handleLogout} 
        style={{ 
          position: 'fixed', 
          bottom: 20, 
          right: 20, 
          backgroundColor: '#dc3545',
          zIndex: 1000,
          padding: '10px 20px',
          fontSize: '14px'
        }}
      >
        Logout
      </button>
    </div>
  );
}

export default App;
