import React from 'react';

const AVAILABLE_TOOLS = [
  { value: 'seed_injector', label: 'Seed Injector' },
  { value: 'watering_nozzle', label: 'Watering Nozzle' },
  { value: 'weeder', label: 'Weeder' },
  { value: 'soil_sensor', label: 'Soil Sensor' },
  { value: 'rotary_tool', label: 'Rotary Tool' },
];

const ActionButtons = ({
  handleWaterPlant,
  handleWeeding,
  handleInjectSeed,
  handleReadSoilSensor,
  handleRotaryTool,
  selectedTool,
  setSelectedTool,
  handleMountTool,
  handleDismountTool
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center' }}>
      <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>Actions</h3>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
        <button className="stone-button" onClick={handleWaterPlant}>Water</button>
        <button className="stone-button" onClick={handleWeeding}>Weed here</button>
        <button className="stone-button" onClick={handleInjectSeed}>Inject seed</button>
        <button className="stone-button" onClick={handleReadSoilSensor}>Read Soil</button>
        <button className="stone-button" onClick={handleRotaryTool}>Rotary Tool</button>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 5 }}>
        <select
          value={selectedTool}
          onChange={(e) => setSelectedTool(e.target.value)}
          style={{
            padding: '6px 10px',
            borderRadius: '5px',
            border: '2px solid #666',
            backgroundColor: '#3a3a3a',
            color: 'white',
            fontFamily: 'inherit',
            fontSize: '12px',
            cursor: 'pointer'
          }}
        >
          <option value="">Select Tool...</option>
          {AVAILABLE_TOOLS.map(tool => (
            <option key={tool.value} value={tool.value}>
              {tool.label}
            </option>
          ))}
        </select>
        <button className="stone-button" onClick={handleMountTool} style={{ fontSize: '12px', padding: '6px 10px' }}>Mount</button>
        <button className="stone-button" onClick={handleDismountTool} style={{ fontSize: '12px', padding: '6px 10px' }}>Dismount</button>
      </div>
    </div>
  );
};

export default ActionButtons;
