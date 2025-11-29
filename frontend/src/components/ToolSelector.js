import React from 'react';

const AVAILABLE_TOOLS = [
  { value: 'seed_injector', label: 'Seed Injector' },
  { value: 'watering_nozzle', label: 'Watering Nozzle' },
  { value: 'weeder', label: 'Weeder' },
  { value: 'soil_sensor', label: 'Soil Sensor' },
  { value: 'rotary_tool', label: 'Rotary Tool' },
];

const ToolSelector = ({ 
  selectedTool, 
  setSelectedTool, 
  handleMountTool, 
  handleDismountTool 
}) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <select
        value={selectedTool}
        onChange={(e) => setSelectedTool(e.target.value)}
        style={{
          padding: '8px 12px',
          borderRadius: '5px',
          border: '2px solid #666',
          backgroundColor: '#3a3a3a',
          color: 'white',
          fontFamily: 'inherit',
          fontSize: '14px',
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
      <button className="stone-button" onClick={handleMountTool}>
        Mount Tool
      </button>
      <button className="stone-button" onClick={handleDismountTool}>
        Dismount
      </button>
    </div>
  );
};

export default ToolSelector;
