import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, demoLogin, loading } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.username || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    const result = await login(formData.username, formData.password);
    
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      console.error('Login error:', result.error);
      setError(result.error?.detail || 'Invalid username or password');
    }
  };

  const handleDemoLogin = () => {
    setError('');
    demoLogin();
    navigate(from, { replace: true });
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">
              <span className="logo-icon">🏆</span>
              <span className="logo-text">MLBattle</span>
            </div>
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Log in to your account to continue</p>
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your username"
                disabled={loading}
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>

          <div className="demo-login-section">
            <div className="divider">
              <span>OR</span>
            </div>
            <button 
              type="button"
              onClick={handleDemoLogin}
              className="btn btn-demo btn-block"
            >
              🎮 Try Demo Account
            </button>
          </div>

          <div className="auth-footer">
            <p className="auth-footer-text">
              Don't have an account?{' '}
              <Link to="/register" className="auth-link">
                Sign up
              </Link>
            </p>
          </div>
        </div>

        <div className="auth-side">
          <div className="auth-side-content">
            <h2 className="side-title">Join the Competition</h2>
            <p className="side-description">
              Compete in machine learning challenges, track your progress, 
              and climb the global leaderboard with MLBattle.
            </p>
            <div className="side-features">
              <div className="side-feature">
                <span className="feature-icon">🔗</span>
                <span className="feature-text">Kaggle Integration</span>
              </div>
              <div className="side-feature">
                <span className="feature-icon">📊</span>
                <span className="feature-text">Real-time Leaderboards</span>
              </div>
              <div className="side-feature">
                <span className="feature-icon">🎮</span>
                <span className="feature-text">ELO Rating System</span>
              </div>
              <div className="side-feature">
                <span className="feature-icon">📈</span>
                <span className="feature-text">Progress Analytics</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
