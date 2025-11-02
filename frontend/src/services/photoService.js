import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

/**
 * Take a photo with the FarmBot camera
 */
export const takePhoto = async (position, photoData, setPhotoData, savePhotos, setMoveStatus) => {
  try {
    const response = await axios.get(`${API_BASE}/take-photo/`);
    const photoResponse = response.data;
    
    console.log('Photo response:', photoResponse);
    console.log('Photo URL:', photoResponse.url);
    
    const newPhoto = {
      id: photoResponse.id || Date.now(),
      url: photoResponse.url,
      farmbot_id: photoResponse.farmbot_id,
      position: photoResponse.coordinates || { ...position },
      timestamp: photoResponse.created_at || new Date().toISOString()
    };
    
    console.log('New photo object:', newPhoto);
    
    const updatedPhotos = [...photoData, newPhoto];
    setPhotoData(updatedPhotos);
    savePhotos(updatedPhotos);
    
    setMoveStatus(`Photo taken successfully (${updatedPhotos.length} photos)`);
    return newPhoto;
  } catch (error) {
    console.error('Error taking photo:', error);
    setMoveStatus('Photo failed');
    throw error;
  }
};

/**
 * Clear all photos
 */
export const clearAllPhotos = async (photoData, clearPhotos, setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/clear-photos/`);
    
    // Clean up object URLs to prevent memory leaks
    photoData.forEach(photo => {
      if (photo.url) {
        URL.revokeObjectURL(photo.url);
      }
    });
    
    clearPhotos();
    setMoveStatus('All photos cleared');
  } catch (error) {
    console.error('Error clearing photos:', error);
    setMoveStatus('Error clearing photos');
    throw error;
  }
};
