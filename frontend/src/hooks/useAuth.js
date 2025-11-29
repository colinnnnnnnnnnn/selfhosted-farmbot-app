import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);

  useEffect(() => {
    // Check for token in URL (from OAuth callback redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('auth_token');
    
    if (tokenFromUrl) {
      // Store the token and clear the URL
      localStorage.setItem('authToken', tokenFromUrl);
      setAuthToken(tokenFromUrl);
      setIsAuthenticated(true);
      // Clean up the URL without reloading
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    // Check for existing token in localStorage
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (token) => {
    setAuthToken(token);
    setIsAuthenticated(true);
    localStorage.setItem('authToken', token);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('authToken');
  };

  return {
    isAuthenticated,
    authToken,
    handleLogin,
    handleLogout
  };
};
