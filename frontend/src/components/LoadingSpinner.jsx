import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Loading...', fullScreen = false }) => {
  const content = (
    <div className="loading-spinner">
      <div className="spinner-animation"></div>
      <p className="loading-message">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="loading-spinner-fullscreen">
        {content}
      </div>
    );
  }

  return content;
};

export default LoadingSpinner;
