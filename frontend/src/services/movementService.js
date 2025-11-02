import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

/**
 * Get current position from the FarmBot
 */
export const getCurrentPosition = async () => {
  const response = await axios.get(`${API_BASE}/position/`);
  return response.data;
};

/**
 * Move FarmBot to absolute position
 */
export const moveAbsolute = async (target, setPosition, setTargetPosition, setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/emergency-unlock/`);
    console.log('Bot unlocked');

    setTargetPosition(target);
    setMoveStatus('Moving...');
    
    await axios.post(`${API_BASE}/move-absolute/`, target);
    console.log('Move command sent:', target);
    
    // Poll position until target is reached
    let checks = 0;
    const maxChecks = 10;
    const checkPosition = async () => {
      try {
        const res = await axios.get(`${API_BASE}/position/`);
        const arr = res.data;
        if (Array.isArray(arr) && arr.length >= 2) {
          const current = { x: arr[0], y: arr[1] };
          setPosition(current);
          const dx = Math.abs(current.x - target.x);
          const dy = Math.abs(current.y - target.y);
          const distance = Math.sqrt(dx*dx + dy*dy);
          if (distance < 0.5) {
            setMoveStatus('Reached target position');
            return;
          }
        }
      } catch {}
      checks++;
      if (checks < maxChecks) {
        setTimeout(checkPosition, 1000);
      } else {
        setMoveStatus('Warning: Final position may not be exact');
      }
    };
    setTimeout(checkPosition, 2000);
  } catch (error) {
    console.error('Error moving bot:', error);
    setMoveStatus('Error: ' + error.message);
    throw error;
  }
};

/**
 * Move FarmBot relative to current position
 */
export const moveRelative = async (delta, position, setPosition, setTargetPosition, setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/emergency-unlock/`);
    const expected = { x: position.x + delta.x, y: position.y + delta.y };
    setTargetPosition(expected);
    setMoveStatus('Moving (relative)...');
    await axios.post(`${API_BASE}/move-relative/`, delta);

    let checks = 0;
    const maxChecks = 10;
    const checkPosition = async () => {
      try {
        const res = await axios.get(`${API_BASE}/position/`);
        const arr = res.data;
        if (Array.isArray(arr) && arr.length >= 2) {
          const current = { x: arr[0], y: arr[1] };
          setPosition(current);
          const dx = Math.abs(current.x - expected.x);
          const dy = Math.abs(current.y - expected.y);
          const distance = Math.sqrt(dx*dx + dy*dy);
          if (distance < 0.5) { 
            setMoveStatus('Reached target position'); 
            return; 
          }
        }
      } catch {}
      checks++;
      if (checks < maxChecks) setTimeout(checkPosition, 1000);
      else setMoveStatus('Warning: Final position may not be exact');
    };
    setTimeout(checkPosition, 2000);
  } catch (err) {
    setMoveStatus('Error: ' + err.message);
    throw err;
  }
};

/**
 * Nudge FarmBot in a specific direction
 */
export const nudge = async (step, speed, position, setPosition, setTargetPosition, setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/move-relative/`, { ...step, speed });
    
    const expected = { x: position.x + step.x, y: position.y + step.y };
    setTargetPosition(expected);
    
    let checks = 0;
    const maxChecks = 8;
    const checkPosition = async () => {
      try {
        const res = await axios.get(`${API_BASE}/position/`);
        const arr = res.data;
        if (Array.isArray(arr) && arr.length >= 2) {
          const current = { x: arr[0], y: arr[1] };
          setPosition(current);
          const dx = Math.abs(current.x - expected.x);
          const dy = Math.abs(current.y - expected.y);
          const distance = Math.sqrt(dx*dx + dy*dy);
          if (distance < 0.5) {
            setMoveStatus('Nudge complete');
            return;
          }
        }
      } catch {}
      checks++;
      if (checks < maxChecks) {
        setTimeout(checkPosition, 1000);
      } else {
        setMoveStatus('Nudge timeout');
      }
    };
    setTimeout(checkPosition, 500);
  } catch (e) {
    setMoveStatus('Nudge failed');
    throw e;
  }
};

/**
 * Move FarmBot to home position
 */
export const goHome = async (setPosition, setTargetPosition, setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/find-home/`);
    const target = { x: 0, y: 0 };
    setTargetPosition(target);
    setMoveStatus('Homing...');

    let checks = 0;
    const maxChecks = 20;
    const checkHome = async () => {
      try {
        const res = await axios.get(`${API_BASE}/position/`);
        const arr = res.data;
        if (Array.isArray(arr) && arr.length >= 2) {
          const current = { x: arr[0], y: arr[1] };
          setPosition(current);
          const dx = Math.abs(current.x - 0);
          const dy = Math.abs(current.y - 0);
          const distance = Math.sqrt(dx*dx + dy*dy);
          if (distance < 0.5) {
            setMoveStatus('Reached home');
            return;
          }
        }
      } catch {}
      checks++;
      if (checks < maxChecks) {
        setTimeout(checkHome, 1000);
      } else {
        setMoveStatus('Warning: Did not reach home exactly');
      }
    };
    setTimeout(checkHome, 2000);
  } catch (e) {
    setMoveStatus('Home failed');
    throw e;
  }
};

/**
 * Emergency unlock the FarmBot
 */
export const unlock = async (setMoveStatus) => {
  try {
    await axios.post(`${API_BASE}/emergency-unlock/`);
    setMoveStatus('Unlocked');
  } catch (e) {
    setMoveStatus('Unlock failed');
    throw e;
  }
};
