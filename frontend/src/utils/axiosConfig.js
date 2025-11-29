import axios from 'axios';

// Get API base URL from environment variable, fallback to localhost for development
export const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Set up Axios to include the authorization token in headers
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axios;
