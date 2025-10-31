import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { usersAPI, submissionsAPI } from '../services/api';
import { getRatingTier } from '../utils/constants';
import RatingChart from '../components/RatingChart';
import SubmissionHistory from '../components/SubmissionHistory';
import './Profile.css';

const Profile = () => {
  const { user } = useAuth();
  const [ratingHistory, setRatingHistory] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user) {
      fetchUserData();
    }
  }, [user]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const [ratingResponse, submissionsResponse] = await Promise.all([
        usersAPI.getRatingHistory(user.id),
        usersAPI.getSubmissions(user.id)
      ]);

      setRatingHistory(ratingResponse.data.results || ratingResponse.data);
      setSubmissions(submissionsResponse.data.results || submissionsResponse.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="page-container">
        <div className="alert alert-info">Please log in to view your profile.</div>
      </div>
    );
  }

  const currentTier = getRatingTier(user.elo_rating || 1500);
  const ratingChange = user.elo_rating - 1500;

  return (
    <div className="profile-page">
      <div className="page-container">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar-section">
            <div className="profile-avatar-large" style={{ background: `linear-gradient(135deg, ${currentTier.color}, ${currentTier.color}dd)` }}>
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <h1 className="profile-username">{user.username}</h1>
              <div className="profile-meta">
                <span className="profile-email">{user.email}</span>
                {user.kaggle_username && (
                  <span className="profile-kaggle">
                    Kaggle: <a href={`https://www.kaggle.com/${user.kaggle_username}`} target="_blank" rel="noopener noreferrer">
                      {user.kaggle_username}
                    </a>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="profile-stats-cards">
            <div className="profile-stat-card" style={{ borderColor: currentTier.color }}>
              <span className="stat-icon">⭐</span>
              <div className="stat-content">
                <span className="stat-label">Current Rating</span>
                <span className="stat-value" style={{ color: currentTier.color }}>
                  {user.elo_rating || 1500}
                </span>
                <span className={`stat-change ${ratingChange >= 0 ? 'positive' : 'negative'}`}>
                  {ratingChange > 0 ? '+' : ''}{ratingChange} from start
                </span>
              </div>
              <div className="tier-badge-large" style={{ backgroundColor: `${currentTier.color}20`, color: currentTier.color }}>
                {currentTier.name}
              </div>
            </div>

            <div className="profile-stat-card">
              <span className="stat-icon">🏆</span>
              <div className="stat-content">
                <span className="stat-label">Highest Rating</span>
                <span className="stat-value">
                  {user.highest_rating || user.elo_rating || 1500}
                </span>
              </div>
            </div>

            <div className="profile-stat-card">
              <span className="stat-icon">🎯</span>
              <div className="stat-content">
                <span className="stat-label">Competitions</span>
                <span className="stat-value">
                  {user.competitions_participated || 0}
                </span>
              </div>
            </div>

            <div className="profile-stat-card">
              <span className="stat-icon">📊</span>
              <div className="stat-content">
                <span className="stat-label">Submissions</span>
                <span className="stat-value">
                  {submissions.length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs">
          <ul className="tabs-list">
            <li>
              <button
                className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
            </li>
            <li>
              <button
                className={`tab-button ${activeTab === 'rating' ? 'active' : ''}`}
                onClick={() => setActiveTab('rating')}
              >
                Rating History
              </button>
            </li>
            <li>
              <button
                className={`tab-button ${activeTab === 'submissions' ? 'active' : ''}`}
                onClick={() => setActiveTab('submissions')}
              >
                Submissions
              </button>
            </li>
          </ul>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-content">
              <div className="overview-grid">
                <div className="overview-section">
                  <h2>Performance Summary</h2>
                  <div className="performance-stats">
                    <div className="performance-item">
                      <span className="perf-label">Current Rank</span>
                      <span className="perf-value">{currentTier.name}</span>
                    </div>
                    <div className="performance-item">
                      <span className="perf-label">Rating Progress</span>
                      <span className={`perf-value ${ratingChange >= 0 ? 'positive' : 'negative'}`}>
                        {ratingChange > 0 ? '+' : ''}{ratingChange}
                      </span>
                    </div>
                    <div className="performance-item">
                      <span className="perf-label">Total Competitions</span>
                      <span className="perf-value">{user.competitions_participated || 0}</span>
                    </div>
                    <div className="performance-item">
                      <span className="perf-label">Total Submissions</span>
                      <span className="perf-value">{submissions.length}</span>
                    </div>
                  </div>
                </div>

                <div className="overview-section">
                  <h2>Quick Stats</h2>
                  <div className="quick-stats">
                    <div className="quick-stat-item">
                      <div className="quick-stat-icon">📈</div>
                      <div className="quick-stat-content">
                        <span className="quick-stat-label">Best Performance</span>
                        <span className="quick-stat-value">
                          {user.highest_rating || user.elo_rating || 1500} ELO
                        </span>
                      </div>
                    </div>
                    <div className="quick-stat-item">
                      <div className="quick-stat-icon">🎯</div>
                      <div className="quick-stat-content">
                        <span className="quick-stat-label">Active Since</span>
                        <span className="quick-stat-value">
                          {new Date(user.date_joined).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {ratingHistory.length > 0 && (
                <div className="overview-chart-section">
                  <RatingChart ratingHistory={ratingHistory} loading={false} />
                </div>
              )}
            </div>
          )}

          {activeTab === 'rating' && (
            <div className="rating-content">
              <RatingChart 
                ratingHistory={ratingHistory} 
                loading={loading}
                error={error}
              />
            </div>
          )}

          {activeTab === 'submissions' && (
            <div className="submissions-content">
              <SubmissionHistory 
                submissions={submissions}
                loading={loading}
                error={error}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
