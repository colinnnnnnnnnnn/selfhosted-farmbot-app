import React from 'react';

const MoveAbsoluteForm = ({ moveForm, handleInputChange, handleMove, loading }) => {
  return (
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
  );
};

export default MoveAbsoluteForm;
