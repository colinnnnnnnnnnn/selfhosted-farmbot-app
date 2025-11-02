import React from 'react';

const ControlButtons = ({ 
  handleGet, 
  handleUnlock, 
  handleWaterPlant, 
  handleWeeding,
  handleHome, 
  handleTakePhoto, 
  handleClearPhotos,
  handleLogout,
  loading, 
  photoLoading, 
  photoCount 
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20, alignItems: 'center' }}>
      <div style={{ display: 'flex', gap: 20 }}>
        <button className="stone-button" onClick={handleGet} disabled={loading}>
          Get Current Position
        </button>
        <button className="stone-button" onClick={handleUnlock}>Unlock</button>
        <button className="stone-button" onClick={handleWaterPlant}>Water</button>
        <button className="stone-button" onClick={handleWeeding}>Weed here</button>
        <button className="stone-button" onClick={handleHome}>Home</button>
      </div>
      <div style={{ display: 'flex', gap: 20 }}>
        <button className="stone-button" onClick={handleTakePhoto} disabled={photoLoading}>
          {photoLoading ? 'Taking Photo...' : 'Take Photo'}
        </button>
        <button className="stone-button" onClick={handleClearPhotos}>
          Clear Photos ({photoCount})
        </button>
      </div>
    </div>
  );
};

export default ControlButtons;
