import React from 'react';

const MoveRelativeForm = ({ moveRelForm, handleRelInputChange, handleMoveRelative, loading }) => {
  return (
    <form onSubmit={handleMoveRelative}>
      <h3>Move Relative</h3>
      <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <label style={{ fontSize: '12px', marginBottom: 2 }}>X</label>
          <input 
            type="text" 
            name="dx" 
            value={moveRelForm.dx} 
            onChange={handleRelInputChange} 
            style={{ width: '50px', height: '25px' }} 
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <label style={{ fontSize: '12px', marginBottom: 2 }}>Y</label>
          <input 
            type="text" 
            name="dy" 
            value={moveRelForm.dy} 
            onChange={handleRelInputChange} 
            style={{ width: '50px', height: '25px' }} 
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <label style={{ fontSize: '12px', marginBottom: 2 }}>Z</label>
          <input 
            type="text" 
            name="dz" 
            value={moveRelForm.dz} 
            onChange={handleRelInputChange} 
            style={{ width: '50px', height: '25px' }} 
          />
        </div>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block' }}>Speed (%):</label>
        <input 
          type="number" 
          name="speed" 
          value={moveRelForm.speed} 
          onChange={handleRelInputChange} 
          style={{ width: '100px' }} 
          min="1" 
          max="100" 
        />
      </div>
      <button className="stone-button" type="submit" disabled={loading}>Move</button>
    </form>
  );
};

export default MoveRelativeForm;
