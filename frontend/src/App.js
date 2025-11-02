import React, { useState } from 'react';
import axios from './utils/axiosConfig';
import { API_BASE } from './utils/axiosConfig';
import './App.css';
import LoginPage from './LoginPage';
import { useAuth } from './hooks/useAuth';
import { useFarmBotPosition } from './hooks/useFarmBotPosition';
import { usePhotos } from './hooks/usePhotos';
import ControlButtons from './components/ControlButtons';
import StatusDisplay from './components/StatusDisplay';
import MoveAbsoluteForm from './components/MoveAbsoluteForm';
import MoveRelativeForm from './components/MoveRelativeForm';
import ManualJogPad from './components/ManualJogPad';
import FarmBotMap from './components/FarmBotMap';
import BotVisibilityToggle from './components/BotVisibilityToggle';

function App() {
  // Authentication
  const { isAuthenticated, handleLogin, handleLogout: authLogout } = useAuth();
  
  // Position management
  const { position, setPosition, loading, fetchPosition } = useFarmBotPosition();
  
  // Photo management
  const { photoData, setPhotoData, savePhotos, clearPhotos } = usePhotos();
  
  // Movement state
  const [moveForm, setMoveForm] = useState({ x: 0, y: 0, z: 0, speed: 100 });
  const [moveRelForm, setMoveRelForm] = useState({ dx: 0, dy: 0, dz: 0, speed: 100 });
  const [nudgeIntervalId, setNudgeIntervalId] = useState(null);
  const [targetPosition, setTargetPosition] = useState(null);
  const [moveStatus, setMoveStatus] = useState('');
  
  // UI state
  const [photoLoading, setPhotoLoading] = useState(false);
  const [botVisible, setBotVisible] = useState(true);

  // Handlers
  const handleLogout = () => {
    authLogout();
    setPhotoData([]);
    setPosition({ x: 0, y: 0, z: 0 });
    setTargetPosition(null);
    setMoveStatus('');
  };

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

      await axios.post(`${API_BASE}/emergency-unlock/`);
      console.log('Bot unlocked');

      setTargetPosition(target);
      setMoveStatus('Moving...');
      
      await axios.post(`${API_BASE}/move-absolute/`, target);
      console.log('Move command sent:', target);
      
      let checks = 0;
      const maxChecks = 10;
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

  const handleMoveRelative = async (e) => {
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
  };

  const startNudge = (dx, dy, dz = 0) => {
    if (nudgeIntervalId) return;
    const step = { x: dx, y: dy, z: dz };
    const speed = Number(moveRelForm.speed) || 100;
    setMoveStatus('Nudging...');
    
    const performNudge = async () => {
      try {
        await axios.post(`${API_BASE}/move-relative/`, { ...step, speed });
        
        const expected = { x: position.x + step.x, y: position.y + step.y };
        setTargetPosition(expected);
        
        let checks = 0;
        const maxChecks = 8;
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
    try { 
      await axios.post(`${API_BASE}/emergency-unlock/`); 
      setMoveStatus('Unlocked'); 
    }
    catch (e) { 
      setMoveStatus('Unlock failed'); 
    }
  };

  const handleWaterPlant = async () => {
    try {
      setMoveStatus('Watering');
      await axios.post(`${API_BASE}/water-plant/`);
      setMoveStatus('Watering complete');
    } catch (error) {
      console.log('Error watering:', error);
      setMoveStatus('Watering failed');
    }
  };

  const handleTakePhoto = async () => {
    setPhotoLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/take-photo/`);
      const photoResponse = response.data;
      
      console.log('Photo response:', photoResponse);
      console.log('Photo URL:', photoResponse.url);
      
      const newPhoto = {
        id: photoResponse.id || Date.now(),
        url: photoResponse.url,
        farmbot_id: photoResponse.farmbot_id,
        position: photoResponse.coordinates || { ...position },
        timestamp: photoResponse.created_at || new Date().toISOString()
      };
      
      console.log('New photo object:', newPhoto);
      
      const updatedPhotos = [...photoData, newPhoto];
      setPhotoData(updatedPhotos);
      savePhotos(updatedPhotos);
      
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
      await axios.post(`${API_BASE}/clear-photos/`);
      
      photoData.forEach(photo => {
        if (photo.url) {
          URL.revokeObjectURL(photo.url);
        }
      });
      
      clearPhotos();
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

      let checks = 0;
      const maxChecks = 20;
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

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="App" style={{ padding: 40 }}>
      {/* Main title */}
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <h1 style={{ color: 'white', fontSize: '48px', margin: 0, textShadow: '2px 2px 4px rgba(0,0,0,0.5)' }}>
          Farmbot
        </h1>
      </div>

      {/* Top section with controls and move forms */}
      <div className="dirt-background" style={{ display: 'flex', gap: 40, marginBottom: 20, padding: '15px 20px' }}>
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <ControlButtons
            handleGet={handleGet}
            handleUnlock={handleUnlock}
            handleWaterPlant={handleWaterPlant}
            handleHome={handleHome}
            handleTakePhoto={handleTakePhoto}
            handleClearPhotos={handleClearPhotos}
            handleLogout={handleLogout}
            loading={loading}
            photoLoading={photoLoading}
            photoCount={photoData.length}
          />

          <StatusDisplay
            position={position}
            targetPosition={targetPosition}
            moveStatus={moveStatus}
          />
        </div>

        {/* Move sections */}
        <div style={{ flex: '1', display: 'flex', gap: 40 }}>
          <MoveAbsoluteForm
            moveForm={moveForm}
            handleInputChange={handleInputChange}
            handleMove={handleMove}
            loading={loading}
          />

          <MoveRelativeForm
            moveRelForm={moveRelForm}
            handleRelInputChange={handleRelInputChange}
            handleMoveRelative={handleMoveRelative}
            loading={loading}
          />
        </div>

        {/* D-pad section */}
        <ManualJogPad
          startNudge={startNudge}
          stopNudge={stopNudge}
        />
      </div>

      {/* Main content area with centered grid */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', position: 'relative' }}>
        <BotVisibilityToggle botVisible={botVisible} setBotVisible={setBotVisible} />
        <FarmBotMap position={position} photoData={photoData} botVisible={botVisible} />
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
