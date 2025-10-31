import React from 'react';
import { getRatingTier } from '../utils/constants';
import './Leaderboard.css';

const Leaderboard = ({ entries, loading, error, isConnected }) => {
  if (loading) {
    return (
      <div className="leaderboard-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="leaderboard-container">
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="leaderboard-container">
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <h3 className="empty-state-title">No Submissions Yet</h3>
          <p className="empty-state-description">
            Be the first to submit and climb the leaderboard!
          </p>
        </div>
      </div>
    );
  }

  const getRankClass = (rank) => {
    if (rank === 1) return 'rank-gold';
    if (rank === 2) return 'rank-silver';
    if (rank === 3) return 'rank-bronze';
    return '';
  };

  const getRankMedal = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  const getTierBadge = (rating) => {
    const tier = getRatingTier(rating);
    return (
      <span 
        className="tier-badge" 
        style={{ 
          backgroundColor: `${tier.color}20`,
          color: tier.color,
          borderColor: tier.color
        }}
      >
        {tier.name}
      </span>
    );
  };

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h2 className="leaderboard-title">
          <span className="leaderboard-icon">🏆</span>
          Leaderboard
        </h2>
        {isConnected && (
          <div className="live-indicator">
            <span className="live-dot"></span>
            <span className="live-text">Live</span>
          </div>
        )}
      </div>

      <div className="leaderboard-table-container">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="rank-column">Rank</th>
              <th className="user-column">User</th>
              <th className="rating-column">Rating</th>
              <th className="score-column">Score</th>
              <th className="submissions-column">Submissions</th>
              <th className="updated-column">Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr 
                key={entry.id} 
                className={`leaderboard-row ${getRankClass(entry.rank)}`}
              >
                <td className="rank-column">
                  <span className="rank-value">
                    {getRankMedal(entry.rank)}
                  </span>
                </td>
                <td className="user-column">
                  <div className="user-info">
                    <div className="user-avatar">
                      {entry.user_username?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div className="user-details">
                      <span className="user-name">{entry.user_username || 'Unknown'}</span>
                      {entry.user_elo_rating && getTierBadge(entry.user_elo_rating)}
                    </div>
                  </div>
                </td>
                <td className="rating-column">
                  <span className="rating-value">
                    {entry.user_elo_rating || 1500}
                  </span>
                </td>
                <td className="score-column">
                  <span className="score-value">
                    {entry.score ? parseFloat(entry.score).toFixed(4) : 'N/A'}
                  </span>
                </td>
                <td className="submissions-column">
                  <span className="submissions-value">
                    {entry.submissions_count || 0}
                  </span>
                </td>
                <td className="updated-column">
                  <span className="updated-value">
                    {entry.last_submission_date 
                      ? new Date(entry.last_submission_date).toLocaleDateString()
                      : 'N/A'
                    }
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leaderboard;
