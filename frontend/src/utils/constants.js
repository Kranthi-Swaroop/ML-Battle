/**
 * Application Constants
 */

// API URLs
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

// Competition Status
export const COMPETITION_STATUS = {
  UPCOMING: 'upcoming',
  ONGOING: 'ongoing',
  COMPLETED: 'completed',
};

// Rating Tiers
export const RATING_TIERS = {
  GRANDMASTER: { min: 2400, name: 'Grandmaster', color: '#FF0000' },
  INTERNATIONAL_MASTER: { min: 2200, name: 'International Master', color: '#FFA500' },
  MASTER: { min: 2000, name: 'Master', color: '#FFD700' },
  EXPERT: { min: 1800, name: 'Expert', color: '#800080' },
  ADVANCED: { min: 1600, name: 'Advanced', color: '#0000FF' },
  INTERMEDIATE: { min: 1400, name: 'Intermediate', color: '#008000' },
  BEGINNER: { min: 1200, name: 'Beginner', color: '#808080' },
  NEWBIE: { min: 0, name: 'Newbie', color: '#808080' },
};

/**
 * Get rating tier for a given rating
 * @param {number} rating - ELO rating
 * @returns {Object} Rating tier object
 */
export const getRatingTier = (rating) => {
  if (rating >= 2400) return RATING_TIERS.GRANDMASTER;
  if (rating >= 2200) return RATING_TIERS.INTERNATIONAL_MASTER;
  if (rating >= 2000) return RATING_TIERS.MASTER;
  if (rating >= 1800) return RATING_TIERS.EXPERT;
  if (rating >= 1600) return RATING_TIERS.ADVANCED;
  if (rating >= 1400) return RATING_TIERS.INTERMEDIATE;
  if (rating >= 1200) return RATING_TIERS.BEGINNER;
  return RATING_TIERS.NEWBIE;
};

// Date and Time Formats
export const DATE_FORMAT = 'YYYY-MM-DD';
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm';
export const TIME_FORMAT = 'HH:mm';

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// WebSocket Events
export const WS_EVENTS = {
  LEADERBOARD_INIT: 'leaderboard_init',
  LEADERBOARD_UPDATE: 'leaderboard_update',
  REFRESH: 'refresh',
};

// Navigation Routes
export const ROUTES = {
  HOME: '/',
  COMPETITIONS: '/competitions',
  COMPETITION_DETAIL: '/competitions/:id',
  LEADERBOARD: '/leaderboard',
  PROFILE: '/profile/:id',
  MY_PROFILE: '/profile',
  LOGIN: '/login',
  REGISTER: '/register',
};
