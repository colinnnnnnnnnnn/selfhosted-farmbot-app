import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

/**
 * Water plant at current or specified position
 */
export const waterPlant = async (setMoveStatus) => {
  try {
    setMoveStatus('Watering');
    await axios.post(`${API_BASE}/water-plant/`);
    setMoveStatus('Watering complete');
  } catch (error) {
    console.log('Error watering:', error);
    setMoveStatus('Watering failed');
    throw error;
  }
};
