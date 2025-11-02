import React, { useState } from 'react';
import { createPortal } from 'react-dom';

const modalBackdrop = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: 'rgba(0,0,0,0.5)',
  zIndex: 2000,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const modalContent = {
  background: '#222',
  borderRadius: '10px',
  padding: '24px',
  minWidth: '350px',
  minHeight: '250px',
  maxWidth: '90vw',
  maxHeight: '80vh',
  overflow: 'auto',
  color: 'white',
  boxShadow: '0 4px 32px rgba(0,0,0,0.7)',
};

const gridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
  gap: '12px',
  marginTop: '10px',
};

const thumbStyle = {
  width: '100%',
  height: '80px',
  objectFit: 'cover',
  borderRadius: '6px',
  cursor: 'pointer',
  border: '2px solid #444',
  transition: 'border 0.2s',
};

const enlargedStyle = {
  maxWidth: '80vw',
  maxHeight: '60vh',
  borderRadius: '10px',
  marginBottom: '12px',
  border: '3px solid #13a73f',
  boxShadow: '0 2px 16px rgba(0,0,0,0.7)',
};

function PhotoGallery({ photos, open, onClose }) {
  const [selected, setSelected] = useState(null);

  if (!open) return null;

  const handleBackdrop = (e) => {
    if (e.target === e.currentTarget) {
      setSelected(null);
      onClose();
    }
  };

  const modal = (
    <div style={modalBackdrop} onClick={handleBackdrop}>
      <div style={modalContent}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>Photo Gallery</h2>
          <button onClick={() => { setSelected(null); onClose(); }} style={{ background: '#444', color: 'white', border: 'none', borderRadius: 4, padding: '4px 12px', cursor: 'pointer', fontSize: 14 }}>Close</button>
        </div>
        {selected ? (
          <div style={{ textAlign: 'center' }}>
            <img src={selected.url} alt="enlarged" style={enlargedStyle} />
            <div style={{ marginBottom: 8 }}>
              <strong>Filename:</strong> {selected.filename || selected.url.split('/').pop()}
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong>Date:</strong> {selected.timestamp ? new Date(selected.timestamp).toLocaleString() : 'N/A'}
            </div>
            <button onClick={() => setSelected(null)} style={{ background: '#13a73f', color: 'white', border: 'none', borderRadius: 4, padding: '6px 18px', cursor: 'pointer', fontSize: 15 }}>Back to Gallery</button>
          </div>
        ) : (
          <div style={gridStyle}>
            {photos && photos.length > 0 ? photos.map((photo, idx) => (
              <img
                key={photo.url || idx}
                src={photo.url}
                alt={`photo-${idx}`}
                style={thumbStyle}
                onClick={() => setSelected(photo)}
                title={photo.filename || photo.url.split('/').pop()}
              />
            )) : <div style={{ color: '#aaa', gridColumn: '1/-1' }}>No photos available.</div>}
          </div>
        )}
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

export default PhotoGallery;
