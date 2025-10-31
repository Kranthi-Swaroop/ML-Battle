/**
 * Authentication Utilities
 */

/**
 * Store authentication tokens
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 */
export const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

/**
 * Get access token
 * @returns {string|null} Access token
 */
export const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Get refresh token
 * @returns {string|null} Refresh token
 */
export const getRefreshToken = () => {
  return localStorage.getItem('refresh_token');
};

/**
 * Remove authentication tokens
 */
export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

/**
 * Check if user is authenticated
 * @returns {boolean} Authentication status
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

/**
 * Store current user data
 * @param {Object} user - User object
 */
export const setCurrentUser = (user) => {
  localStorage.setItem('current_user', JSON.stringify(user));
};

/**
 * Get current user data
 * @returns {Object|null} User object
 */
export const getCurrentUser = () => {
  const user = localStorage.getItem('current_user');
  return user ? JSON.parse(user) : null;
};

/**
 * Remove current user data
 */
export const clearCurrentUser = () => {
  localStorage.removeItem('current_user');
};

/**
 * Logout user
 */
export const logout = () => {
  clearTokens();
  clearCurrentUser();
  window.location.href = '/login';
};

/**
 * Parse JWT token
 * @param {string} token - JWT token
 * @returns {Object|null} Decoded token payload
 */
export const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

/**
 * Check if token is expired
 * @param {string} token - JWT token
 * @returns {boolean} Expiration status
 */
export const isTokenExpired = (token) => {
  const decoded = parseJwt(token);
  if (!decoded || !decoded.exp) return true;
  
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
};
