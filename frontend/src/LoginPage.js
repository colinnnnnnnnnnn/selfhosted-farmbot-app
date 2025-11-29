import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE } from './utils/axiosConfig';
import './App.css';

function LoginPage({ onLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE}/auth/login/`, formData);
      const { token } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('authToken', token);
      
      // Notify parent component
      onLogin(token);
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE}/auth/register/`, formData);
      const { token } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('authToken', token);
      
      // Notify parent component
      onLogin(token);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialAuth = (provider) => {
    const popup = window.open(
      `${API_BASE}/auth/${provider}/login/`,
      'socialAuth',
      'width=500,height=600,scrollbars=yes,resizable=yes'
    );

    // Listen for messages from the popup
    const messageListener = (event) => {
      if (event.data.type === 'SOCIAL_AUTH_SUCCESS') {
        const { token } = event.data;
        localStorage.setItem('authToken', token);
        onLogin(token);
        popup.close();
        window.removeEventListener('message', messageListener);
      }
    };

    window.addEventListener('message', messageListener);

    // Check if popup is closed manually
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        window.removeEventListener('message', messageListener);
      }
    }, 1000);
  };

  return (
    <div className="App">
      {/* Main title */}
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <h1 style={{ color: 'white', fontSize: '48px', margin: 0, textShadow: '2px 2px 4px rgba(0,0,0,0.5)' }}>Farmbot</h1>
      </div>

      {/* Login form */}
      <div className="dirt-background" style={{ maxWidth: '400px', margin: '0 auto', padding: '30px' }}>
        <h2 style={{ color: 'white', textAlign: 'center', marginBottom: 30 }}>Login</h2>
        
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 20 }}>
            <label style={{ color: 'white', display: 'block', marginBottom: 8 }}>Username or Email:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '4px',
                border: '1px solid #ccc',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              required
            />
          </div>

          <div style={{ marginBottom: 30 }}>
            <label style={{ color: 'white', display: 'block', marginBottom: 8 }}>Password:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '4px',
                border: '1px solid #ccc',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              required
            />
          </div>

          {error && (
            <div style={{ color: '#ff6b6b', marginBottom: 20, textAlign: 'center' }}>
              {error}
            </div>
          )}

          <div style={{ display: 'flex', gap: 15, justifyContent: 'center' }}>
            <button
              type="submit"
              className="stone-button"
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
            <button
              type="button"
              className="stone-button"
              onClick={handleRegister}
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? 'Registering...' : 'Register'}
            </button>
          </div>

          {/* Social Authentication */}
          <div style={{ marginTop: 30, textAlign: 'center' }}>
            <div style={{ color: 'white', marginBottom: 15, fontSize: '14px' }}>Or continue with:</div>
            <div style={{ display: 'flex', gap: 15, justifyContent: 'center' }}>
              <button
                type="button"
                className="stone-button"
                onClick={() => handleSocialAuth('google')}
                disabled={loading}
                style={{ 
                  backgroundColor: '#4285f4',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 20px'
                }}
              >
                <span style={{ fontSize: '18px' }}>🔍</span>
                Google
              </button>
              <button
                type="button"
                className="stone-button"
                onClick={() => handleSocialAuth('github')}
                disabled={loading}
                style={{ 
                  backgroundColor: '#333',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 20px'
                }}
              >
                <span style={{ fontSize: '18px' }}>🐙</span>
                GitHub
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
