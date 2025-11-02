import React from 'react';

const ManualJogPad = ({ startNudge, stopNudge }) => {
  return (
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
        >
          Z+
        </button>
        <button
          className="stone-button"
          onMouseDown={() => startNudge(0, 0, -5)}
          onMouseUp={stopNudge}
          onMouseLeave={stopNudge}
          onTouchStart={() => startNudge(0, 0, -5)}
          onTouchEnd={stopNudge}
        >
          Z-
        </button>
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
          >
            ↑
          </button>
          <div />

          <button
            className="stone-button"
            onMouseDown={() => startNudge(-5, 0, 0)}
            onMouseUp={stopNudge}
            onMouseLeave={stopNudge}
            onTouchStart={() => startNudge(-5, 0, 0)}
            onTouchEnd={stopNudge}
          >
            ←
          </button>
          <div />
          <button
            className="stone-button"
            onMouseDown={() => startNudge(5, 0, 0)}
            onMouseUp={stopNudge}
            onMouseLeave={stopNudge}
            onTouchStart={() => startNudge(5, 0, 0)}
            onTouchEnd={stopNudge}
          >
            →
          </button>

          <div />
          <button
            className="stone-button"
            onMouseDown={() => startNudge(0, 5, 0)}
            onMouseUp={stopNudge}
            onMouseLeave={stopNudge}
            onTouchStart={() => startNudge(0, 5, 0)}
            onTouchEnd={stopNudge}
          >
            ↓
          </button>
          <div />
        </div>
      </div>
    </div>
  );
};

export default ManualJogPad;
