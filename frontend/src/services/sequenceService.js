import axios from '../utils/axiosConfig';
import { API_BASE } from '../utils/axiosConfig';

/**
 * Get all sequences for the current user
 */
export const getSequences = async () => {
  const response = await axios.get(`${API_BASE}/sequences/`);
  return response.data;
};

/**
 * Get a single sequence by ID
 */
export const getSequence = async (id) => {
  const response = await axios.get(`${API_BASE}/sequences/${id}/`);
  return response.data;
};

/**
 * Create a new sequence
 */
export const createSequence = async (sequenceData) => {
  const response = await axios.post(`${API_BASE}/sequences/`, sequenceData);
  return response.data;
};

/**
 * Update an existing sequence
 */
export const updateSequence = async (id, sequenceData) => {
  const response = await axios.put(`${API_BASE}/sequences/${id}/`, sequenceData);
  return response.data;
};

/**
 * Delete a sequence
 */
export const deleteSequence = async (id) => {
  await axios.delete(`${API_BASE}/sequences/${id}/`);
};

/**
 * Execute a sequence
 */
export const executeSequence = async (id) => {
  const response = await axios.post(`${API_BASE}/sequences/${id}/execute/`);
  return response.data;
};

/**
 * Available commands for sequence steps
 */
export const AVAILABLE_COMMANDS = [
  { 
    value: 'move_absolute', 
    label: 'Move Absolute', 
    params: [
      { name: 'x', type: 'number', label: 'X (mm)', default: 0 },
      { name: 'y', type: 'number', label: 'Y (mm)', default: 0 },
      { name: 'z', type: 'number', label: 'Z (mm)', default: 0 },
      { name: 'speed', type: 'number', label: 'Speed (%)', default: 100 },
    ]
  },
  { 
    value: 'move_relative', 
    label: 'Move Relative', 
    params: [
      { name: 'x', type: 'number', label: 'X (mm)', default: 0 },
      { name: 'y', type: 'number', label: 'Y (mm)', default: 0 },
      { name: 'z', type: 'number', label: 'Z (mm)', default: 0 },
      { name: 'speed', type: 'number', label: 'Speed (%)', default: 100 },
    ]
  },
  { 
    value: 'water_plant', 
    label: 'Water Plant', 
    params: []
  },
  { 
    value: 'take_photo', 
    label: 'Take Photo', 
    params: []
  },
  { 
    value: 'mount_tool', 
    label: 'Mount Tool', 
    params: [
      { name: 'tool_name', type: 'select', label: 'Tool', default: 'watering_nozzle', options: [
        { value: 'watering_nozzle', label: 'Watering Nozzle' },
        { value: 'seed_injector', label: 'Seed Injector' },
        { value: 'weeder', label: 'Weeder' },
        { value: 'soil_sensor', label: 'Soil Sensor' },
        { value: 'rotary_tool', label: 'Rotary Tool' },
      ]}
    ]
  },
  { 
    value: 'dismount_tool', 
    label: 'Dismount Tool', 
    params: []
  },
  { 
    value: 'find_home', 
    label: 'Find Home', 
    params: []
  },
  { 
    value: 'go_to_home', 
    label: 'Go To Home', 
    params: []
  },
  { 
    value: 'emergency_lock', 
    label: 'Emergency Lock', 
    params: []
  },
  { 
    value: 'emergency_unlock', 
    label: 'Emergency Unlock', 
    params: []
  },
  { 
    value: 'dispense', 
    label: 'Dispense', 
    params: [
      { name: 'volume', type: 'number', label: 'Volume (mL)', default: 100 },
    ]
  },
  { 
    value: 'send_message', 
    label: 'Send Message', 
    params: [
      { name: 'message', type: 'text', label: 'Message', default: '' },
    ]
  },
];
