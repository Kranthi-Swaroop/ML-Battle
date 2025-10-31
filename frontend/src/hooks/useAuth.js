/**
 * useAuth Hook - Authentication state management
 */
import { useState, useEffect, createContext, useContext } from 'react';
import { authAPI } from '../services/api';
import * as auth from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is authenticated on mount
    const initAuth = async () => {
      if (auth.isAuthenticated()) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          auth.logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const { access, refresh } = response.data.tokens;
      const userData = response.data.user;

      auth.setTokens(access, refresh);
      auth.setCurrentUser(userData);
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { access, refresh } = response.data.tokens;
      const user = response.data.user;

      auth.setTokens(access, refresh);
      auth.setCurrentUser(user);
      setUser(user);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  };

  const logout = () => {
    auth.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser(userData);
    auth.setCurrentUser(userData);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default useAuth;
