import { useState, useEffect } from 'react';

export const usePhotos = () => {
  const [photoData, setPhotoData] = useState([]);

  useEffect(() => {
    const savedPhotos = localStorage.getItem('farmbot-photos');
    if (savedPhotos) {
      try {
        const parsedPhotos = JSON.parse(savedPhotos);
        setPhotoData(parsedPhotos);
      } catch (error) {
        console.error('Error loading saved photos:', error);
      }
    }
  }, []);

  const savePhotos = (photos) => {
    localStorage.setItem('farmbot-photos', JSON.stringify(photos));
  };

  const clearPhotos = () => {
    setPhotoData([]);
    localStorage.removeItem('farmbot-photos');
  };

  return {
    photoData,
    setPhotoData,
    savePhotos,
    clearPhotos
  };
};
