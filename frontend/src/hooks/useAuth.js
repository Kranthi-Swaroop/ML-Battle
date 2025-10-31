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

  const demoLogin = () => {
    // Demo user data
    const demoUser = {
      id: 1,
      username: 'demo_user',
      email: 'demo@mlbattle.com',
      first_name: 'Demo',
      last_name: 'User',
      elo_rating: 1842,
      highest_rating: 1956,
      competitions_participated: 12,
      submissions_count: 45,
      tier: 'Expert',
      bio: 'Passionate ML enthusiast exploring cutting-edge algorithms!',
      github_username: 'demo_user',
      linkedin_url: 'https://linkedin.com/in/demo',
      kaggle_username: 'demouser',
      date_joined: '2024-06-15T10:30:00Z',
      avatar_url: null
    };

    // Set demo tokens (these won't work with real API but allow navigation)
    auth.setTokens('demo-access-token', 'demo-refresh-token');
    auth.setCurrentUser(demoUser);
    setUser(demoUser);
    setIsAuthenticated(true);

    return { success: true };
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
    demoLogin,
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
