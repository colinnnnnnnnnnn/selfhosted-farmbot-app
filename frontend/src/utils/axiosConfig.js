import axios from 'axios';

export const API_BASE = 'http://localhost:8000/api';

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
