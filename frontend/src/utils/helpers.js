/**
 * Helper utility functions
 */

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format datetime to readable string
 * @param {string|Date} datetime - Datetime to format
 * @returns {string} Formatted datetime
 */
export const formatDateTime = (datetime) => {
  if (!datetime) return '';
  const d = new Date(datetime);
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Calculate time remaining until a date
 * @param {string|Date} endDate - End date
 * @returns {string} Time remaining
 */
export const getTimeRemaining = (endDate) => {
  if (!endDate) return '';
  
  const now = new Date();
  const end = new Date(endDate);
  const diff = end - now;
  
  if (diff <= 0) return 'Ended';
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  
  if (days > 0) return `${days} day${days !== 1 ? 's' : ''} ${hours}h`;
  if (hours > 0) {
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  }
  
  const minutes = Math.floor(diff / (1000 * 60));
  return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, length = 100) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '';
  return num.toLocaleString('en-US');
};

/**
 * Format score with precision
 * @param {number} score - Score to format
 * @param {number} precision - Decimal places
 * @returns {string} Formatted score
 */
export const formatScore = (score, precision = 4) => {
  if (score === null || score === undefined) return '';
  return parseFloat(score).toFixed(precision);
};

/**
 * Get competition status badge class
 * @param {string} status - Competition status
 * @returns {string} CSS class name
 */
export const getStatusBadgeClass = (status) => {
  const classes = {
    'upcoming': 'badge-upcoming',
    'ongoing': 'badge-ongoing',
    'completed': 'badge-completed',
  };
  return classes[status] || 'badge-default';
};

/**
 * Get rating change display
 * @param {number} change - Rating change
 * @returns {string} Formatted rating change with sign
 */
export const formatRatingChange = (change) => {
  if (change === null || change === undefined) return '';
  return change >= 0 ? `+${change}` : `${change}`;
};

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Handle API errors
 * @param {Error} error - Error object
 * @returns {string} Error message
 */
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const { data, status } = error.response;
    
    if (status === 400 && data) {
      // Validation errors
      return Object.values(data).flat().join('. ');
    }
    
    if (status === 401) {
      return 'Authentication required. Please login.';
    }
    
    if (status === 403) {
      return 'You do not have permission to perform this action.';
    }
    
    if (status === 404) {
      return 'Resource not found.';
    }
    
    if (status === 500) {
      return 'Server error. Please try again later.';
    }
    
    return data?.message || data?.detail || 'An error occurred.';
  }
  
  if (error.request) {
    // Request made but no response
    return 'No response from server. Please check your connection.';
  }
  
  // Something else happened
  return error.message || 'An unexpected error occurred.';
};
