import React from 'react';
import { CANVAS_WIDTH, CANVAS_HEIGHT } from '../utils/constants';
import { PhotoOverlay, FarmBotOverlay } from './MapOverlays';

const FarmBotMap = ({ position, photoData, botVisible }) => {
  return (
    <div className="map-background" style={{ position: 'relative', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, overflow: 'hidden' }}>
      <svg width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{ border: '1px solid #ccc', background: 'transparent' }}>
        {/* Draw grid lines */}
        {[...Array(30)].map((_, i) => (
          <line key={i} x1={i * (CANVAS_WIDTH / 29)} y1={0} x2={i * (CANVAS_WIDTH / 29)} y2={CANVAS_HEIGHT} stroke="#eee" />
        ))}
        {[...Array(13)].map((_, i) => (
          <line key={i} x1={0} y1={i * (CANVAS_HEIGHT / 12)} x2={CANVAS_WIDTH} y2={i * (CANVAS_HEIGHT / 12)} stroke="#eee" />
        ))}
      </svg>
      
      {/* FarmBot overlay */}
      <FarmBotOverlay position={position} visible={botVisible} />
      
      {/* Display photos as overlays at captured positions */}
      {photoData.map((photo, index) => (
        <PhotoOverlay key={photo.id} photo={photo} index={index} />
      ))}
    </div>
  );
};

export default FarmBotMap;
