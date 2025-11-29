import React from 'react';

const ActionButtons = ({
  handleWaterPlant,
  handleWeeding,
  handleInjectSeed,
  handleReadSoilSensor,
  handleRotaryTool
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center' }}>
      <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>Actions</h3>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
        <button className="stone-button" onClick={handleWaterPlant}>Water</button>
        <button className="stone-button" onClick={handleWeeding}>Weed here</button>
        <button className="stone-button" onClick={handleInjectSeed}>Inject seed here</button>
        <button className="stone-button" onClick={handleReadSoilSensor}>Read Soil</button>
        <button className="stone-button" onClick={handleRotaryTool}>Rotary Tool</button>
      </div>
    </div>
  );
};

export default ActionButtons;
