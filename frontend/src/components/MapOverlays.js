import React from 'react';
import botImage from '../assets/images/bot.png';
import { SCALE_X, SCALE_Y, IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX } from '../utils/constants';

const PhotoOverlay = ({ photo, index }) => {
  return (
    <div
      key={photo.id}
      style={{
        position: 'absolute',
        left: photo.position.x * SCALE_X - IMAGE_WIDTH_PX / 2,
        top: photo.position.y * SCALE_Y - IMAGE_HEIGHT_PX / 2,
        width: IMAGE_WIDTH_PX,
        height: IMAGE_HEIGHT_PX,
        overflow: 'hidden',
        zIndex: 10 + index,
        border: '2px solid #13a73f'
      }}
    >
      {photo.url ? (
        <img
          src={photo.url}
          alt={`FarmBot Photo ${photo.farmbot_id || index + 1}`}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
          onLoad={() => {
            console.log('Image loaded successfully:', photo.url);
          }}
          onError={(e) => {
            console.error('Image failed to load:', photo.url);
            e.target.style.display = 'none';
            e.target.parentElement.innerHTML = `<div style="width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-size: 14px;"><div>📷</div><div>Photo ${photo.farmbot_id || index + 1}</div></div>`;
          }}
        />
      ) : (
        <div
          style={{
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '14px'
          }}
        >
          <div>📷</div>
          <div>Photo {photo.farmbot_id || index + 1}</div>
        </div>
      )}
    </div>
  );
};

const FarmBotOverlay = ({ position, visible }) => {
  if (!visible) return null;

  const botX = position.x * SCALE_X;
  const botY = position.y * SCALE_Y;

  return (
    <div
      style={{
        position: 'absolute',
        left: botX - 40,
        top: botY - 40,
        width: 80,
        height: 80,
        zIndex: 1000,
        pointerEvents: 'none'
      }}
    >
      <img
        src={botImage}
        alt="FarmBot"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain'
        }}
      />
    </div>
  );
};

export { PhotoOverlay, FarmBotOverlay };
