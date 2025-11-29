import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

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

function PhotoGallery({ photos: localPhotos, open, onClose }) {
  const [selected, setSelected] = useState(null);
  const [photos, setPhotos] = useState([]);
  const [nextCursor, setNextCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  // Fetch photos from paginated API
  const fetchPhotos = async (cursor = null) => {
    setLoading(true);
    try {
      const url = cursor 
        ? `${API_BASE}/photos/?cursor=${cursor}` 
        : `${API_BASE}/photos/`;
      const response = await axios.get(url);
      
      if (cursor) {
        // Append to existing photos
        setPhotos(prev => [...prev, ...response.data.results]);
      } else {
        // Initial load - replace photos
        setPhotos(response.data.results || []);
      }
      
      // Extract cursor from next URL
      if (response.data.next) {
        const nextUrl = new URL(response.data.next);
        setNextCursor(nextUrl.searchParams.get('cursor'));
      } else {
        setNextCursor(null);
      }
    } catch (error) {
      console.error('Failed to fetch photos:', error);
      // Fallback to local photoData if API fails
      setPhotos(localPhotos || []);
      setNextCursor(null);
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  };

  // Load photos when gallery opens
  useEffect(() => {
    if (open && initialLoad) {
      fetchPhotos();
    }
  }, [open, initialLoad]);

  // Reset when gallery closes
  useEffect(() => {
    if (!open) {
      setSelected(null);
      setInitialLoad(true);
      setPhotos([]);
      setNextCursor(null);
    }
  }, [open]);

  const handleLoadMore = () => {
    if (nextCursor && !loading) {
      fetchPhotos(nextCursor);
    }
  };

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
              <strong>Filename:</strong> {selected.farmbot_id || selected.url.split('/').pop()}
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong>Date:</strong> {selected.created_at ? new Date(selected.created_at).toLocaleString() : 'N/A'}
            </div>
            {selected.coordinates && (
              <div style={{ marginBottom: 8 }}>
                <strong>Position:</strong> X: {selected.coordinates.x}, Y: {selected.coordinates.y}, Z: {selected.coordinates.z}
              </div>
            )}
            <button onClick={() => setSelected(null)} style={{ background: '#13a73f', color: 'white', border: 'none', borderRadius: 4, padding: '6px 18px', cursor: 'pointer', fontSize: 15 }}>Back to Gallery</button>
          </div>
        ) : (
          <>
            {initialLoad && loading ? (
              <div style={{ color: '#aaa', textAlign: 'center', padding: '40px' }}>Loading photos...</div>
            ) : photos && photos.length > 0 ? (
              <>
                <div style={gridStyle}>
                  {photos.map((photo, idx) => (
                    <img
                      key={photo.id || photo.url || idx}
                      src={photo.url}
                      alt={`photo-${idx}`}
                      style={thumbStyle}
                      onClick={() => setSelected(photo)}
                      title={photo.farmbot_id || photo.url.split('/').pop()}
                    />
                  ))}
                </div>
                
                {/* Load More Button */}
                {nextCursor && (
                  <div style={{ textAlign: 'center', marginTop: '16px' }}>
                    <button
                      onClick={handleLoadMore}
                      disabled={loading}
                      style={{
                        background: loading ? '#666' : '#13a73f',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        padding: '8px 24px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: 14,
                      }}
                    >
                      {loading ? 'Loading...' : 'Load More Photos'}
                    </button>
                  </div>
                )}
                
                <div style={{ color: '#888', textAlign: 'center', marginTop: '10px', fontSize: '12px' }}>
                  Showing {photos.length} photos
                </div>
              </>
            ) : (
              <div style={{ color: '#aaa', gridColumn: '1/-1', textAlign: 'center', padding: '40px' }}>No photos available.</div>
            )}
          </>
        )}
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

export default PhotoGallery;
