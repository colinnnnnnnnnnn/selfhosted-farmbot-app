import React from 'react';

const BotVisibilityToggle = ({ botVisible, setBotVisible }) => {
  return (
    <div 
      className="dirt-background" 
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 130, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 8, 
        alignItems: 'center', 
        padding: '15px', 
        zIndex: 1000 
      }}
    >
      <div style={{ color: 'white', fontSize: '14px' }}>Toggle Bot</div>
      <div 
        onClick={() => setBotVisible(!botVisible)}
        style={{
          width: '30px',
          height: '60px',
          backgroundColor: botVisible ? '#13a73f' : '#666',
          borderRadius: '15px',
          position: 'relative',
          cursor: 'pointer',
          transition: 'background-color 0.3s ease',
          border: '2px solid #fff'
        }}
      >
        <div
          style={{
            width: '26px',
            height: '26px',
            backgroundColor: 'white',
            borderRadius: '50%',
            position: 'absolute',
            top: botVisible ? '2px' : '30px',
            left: '2px',
            transition: 'top 0.3s ease',
            boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}
        />
      </div>
    </div>
  );
};

export default BotVisibilityToggle;
