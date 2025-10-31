import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" onClick={closeMobileMenu}>
          <span className="navbar-logo">🏆</span>
          <span className="navbar-title">MLBattle</span>
        </Link>

        <button className="navbar-toggle" onClick={toggleMobileMenu}>
          <span className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>

        <div className={`navbar-menu ${mobileMenuOpen ? 'open' : ''}`}>
          <div className="navbar-links">
            <Link to="/" className="navbar-link" onClick={closeMobileMenu}>
              Home
            </Link>
            <Link to="/events" className="navbar-link" onClick={closeMobileMenu}>
              Events
            </Link>
            <Link to="/competitions" className="navbar-link" onClick={closeMobileMenu}>
              Competitions
            </Link>
          </div>

          <div className="navbar-actions">
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="navbar-user" onClick={closeMobileMenu}>
                  <span className="navbar-user-avatar">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                  <span className="navbar-user-info">
                    <span className="navbar-user-name">{user?.username}</span>
                    <span className="navbar-user-rating">
                      {user?.elo_rating || 1500} ELO
                    </span>
                  </span>
                </Link>
                <button className="btn btn-secondary" onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-secondary" onClick={closeMobileMenu}>
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary" onClick={closeMobileMenu}>
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
