import React, { useState } from 'react';
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
import LogViewer from './components/LogViewer';
import { getCurrentPosition, moveAbsolute, moveRelative, nudge, goHome, unlock } from './services/movementService';
import { takePhoto, clearAllPhotos } from './services/photoService';
import { waterPlant, weed } from './services/actionService';

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
      const positionArray = await getCurrentPosition();
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
    const target = {
      x: Number(moveForm.x),
      y: Number(moveForm.y),
      z: Number(moveForm.z),
      speed: Number(moveForm.speed)
    };
    await moveAbsolute(target, setPosition, setTargetPosition, setMoveStatus);
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
    const delta = {
      x: Number(moveRelForm.dx),
      y: Number(moveRelForm.dy),
      z: Number(moveRelForm.dz),
      speed: Number(moveRelForm.speed)
    };
    await moveRelative(delta, position, setPosition, setTargetPosition, setMoveStatus);
  };

  const startNudge = async (dx, dy, dz = 0) => {
    if (nudgeIntervalId) return;
    const step = { x: dx, y: dy, z: dz };
    const speed = Number(moveRelForm.speed) || 100;
    setMoveStatus('Nudging...');
    await nudge(step, speed, position, setPosition, setTargetPosition, setMoveStatus);
  };

  const stopNudge = () => {
    if (nudgeIntervalId) {
      clearInterval(nudgeIntervalId);
      setNudgeIntervalId(null);
      setMoveStatus('');
    }
  };

  const handleUnlock = async () => {
    await unlock(setMoveStatus);
  };

  const handleWaterPlant = async () => {
    await waterPlant(setMoveStatus);
  };

  const handleWeeding = async () => {
    // Use current position; keep params minimal
    await weed({ x: position.x, y: position.y, z: position.z }, setMoveStatus);
  };

  const handleTakePhoto = async () => {
    setPhotoLoading(true);
    try {
      await takePhoto(position, photoData, setPhotoData, savePhotos, setMoveStatus);
    } finally {
      setPhotoLoading(false);
    }
  };

  const handleClearPhotos = async () => {
    await clearAllPhotos(photoData, clearPhotos, setMoveStatus);
  };

  const handleHome = async () => {
    await goHome(setPosition, setTargetPosition, setMoveStatus);
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
            handleWeeding={handleWeeding}
            handleHome={handleHome}
            handleTakePhoto={handleTakePhoto}
            handleClearPhotos={handleClearPhotos}
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

      {/* Lower section: toggle, grid, and logs in one horizontal flex container */}
      <div style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '24px',
        minHeight: '400px',
        marginTop: '40px'
      }}>
        <BotVisibilityToggle botVisible={botVisible} setBotVisible={setBotVisible} />
        <FarmBotMap position={position} photoData={photoData} botVisible={botVisible} />
        <LogViewer />
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
