import React from 'react';

const StatusDisplay = ({ position, targetPosition, moveStatus }) => {
  return (
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
  );
};

export default StatusDisplay;
