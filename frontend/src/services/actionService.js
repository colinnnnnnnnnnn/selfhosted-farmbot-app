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

/**
 * Weeder action - uses the weeder tool at a specific location.
 * Keep it simple: caller provides x, y, z (required) and optional working_depth, speed.
 */
export const weed = async (
  { x, y, z, working_depth = -20, speed = 100 },
  setMoveStatus = () => {}
) => {
  try {
    setMoveStatus('Weeding');
    await axios.post(`${API_BASE}/weeder/`, {
      x,
      y,
      z,
      working_depth,
      speed,
    });
    setMoveStatus('Weeding complete');
  } catch (error) {
    console.log('Error weeding:', error);
    setMoveStatus('Weeding failed');
    throw error;
  }
};
