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

/**
 * Seed injector - plants seeds at current position.
 * seeds_count: number of seeds (default 1)
 * dispense_time: seconds per seed (default 1.0)
 */
export const injectSeed = async (
  { seeds_count = 1, dispense_time = 1.0 } = {},
  setMoveStatus = () => {}
) => {
  try {
    setMoveStatus('Injecting seed');
    await axios.post(`${API_BASE}/seed-injector/`, {
      seeds_count,
      dispense_time,
    });
    setMoveStatus('Seed injected');
  } catch (error) {
    console.log('Error injecting seed:', error);
    setMoveStatus('Seed injection failed');
    throw error;
  }
};

/**
 * Mount a specific tool.
 * tool_name: name of the tool to mount (e.g., 'seed_injector', 'watering_nozzle', 'weeder', 'soil_sensor', 'rotary_tool')
 */
export const mountTool = async (tool_name, setMoveStatus = () => {}) => {
  try {
    setMoveStatus(`Mounting ${tool_name}`);
    await axios.post(`${API_BASE}/mount-tool/`, { tool_name });
    setMoveStatus(`${tool_name} mounted`);
  } catch (error) {
    console.log('Error mounting tool:', error);
    setMoveStatus('Mount failed');
    throw error;
  }
};

/**
 * Dismount the currently mounted tool.
 */
export const dismountTool = async (setMoveStatus = () => {}) => {
  try {
    setMoveStatus('Dismounting tool');
    await axios.post(`${API_BASE}/dismount-tool/`);
    setMoveStatus('Tool dismounted');
  } catch (error) {
    console.log('Error dismounting tool:', error);
    setMoveStatus('Dismount failed');
    throw error;
  }
};
