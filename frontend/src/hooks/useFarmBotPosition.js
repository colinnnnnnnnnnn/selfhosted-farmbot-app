import { useState, useEffect } from 'react';
import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

export const useFarmBotPosition = () => {
  const [position, setPosition] = useState({ x: 0, y: 0, z: 0 });
  const [loading, setLoading] = useState(false);

  const fetchPosition = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/position/`);
      console.log('API Response:', response.data);
      const positionArray = response.data;
      
      if (Array.isArray(positionArray) && positionArray.length >= 3) {
        const newPosition = {
          x: positionArray[0],
          y: positionArray[1],
          z: positionArray[2]
        };
        setPosition(newPosition);
        console.log('Updated position:', newPosition);
      }
    } catch (error) {
      console.error('Error fetching position:', error);
      if (error.response && error.response.status !== 503) {
        alert('Error fetching position: ' + error.message);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPosition();
  }, []);

  return {
    position,
    setPosition,
    loading,
    fetchPosition
  };
};
