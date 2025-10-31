/* eslint-disable react/no-unknown-property */
import React from 'react';
import './FluidGlass.css';

// Simple CSS-based fluid glass component
// Works without 3D models - uses pure CSS animations
export default function FluidGlass({ children, className = '' }) {
  return (
    <div className={`fluid-glass-container ${className}`}>
      <div className="fluid-glass-effect">
        <div className="glass-blob blob-1"></div>
        <div className="glass-blob blob-2"></div>
        <div className="glass-blob blob-3"></div>
      </div>
      <div className="fluid-glass-content">
        {children}
      </div>
    </div>
  );
}
