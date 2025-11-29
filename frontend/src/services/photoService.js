import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

/**
 * Fetch all photos from the API and load them to the grid
 */
export const loadPhotosFromAPI = async (setPhotoData, savePhotos, setMoveStatus) => {
  try {
    // Fetch all photos from the API (using pagination if needed)
    let allPhotos = [];
    let nextUrl = `${API_BASE}/photos/`;
    
    while (nextUrl) {
      const response = await axios.get(nextUrl);
      const data = response.data;
      
      // Handle paginated response
      const results = data.results || data;
      allPhotos = [...allPhotos, ...results];
      
      // Check for next page
      nextUrl = data.next || null;
    }
    
    // Transform API photos to grid format
    const gridPhotos = allPhotos.map(photo => ({
      id: photo.id,
      url: photo.url,
      farmbot_id: photo.farmbot_id,
      position: photo.coordinates || { x: 0, y: 0, z: 0 },
      timestamp: photo.created_at
    }));
    
    setPhotoData(gridPhotos);
    savePhotos(gridPhotos);
    
    setMoveStatus(`Loaded ${gridPhotos.length} photos from gallery`);
    return gridPhotos;
  } catch (error) {
    console.error('Error loading photos from API:', error);
    setMoveStatus('Error loading photos from gallery');
    throw error;
  }
};

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
