import React from 'react';
import { getRatingTier } from '../utils/constants';
import './Leaderboard.css';

const Leaderboard = ({ entries, loading, error, isConnected }) => {
  // Ensure entries is an array
  const leaderboardEntries = Array.isArray(entries) ? entries : [];

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

  if (!leaderboardEntries || leaderboardEntries.length === 0) {
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
              <th className="user-column">Name</th>
              <th className="score-column">Score</th>
            </tr>
          </thead>
          <tbody>
            {leaderboardEntries.map((entry) => (
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
                      {(entry.display_name || entry.username || entry.kaggle_team_name || 'Unknown')?.charAt(0).toUpperCase()}
                    </div>
                    <div className="user-details">
                      <span className="user-name">
                        {entry.display_name || entry.username || entry.kaggle_team_name || 'Unknown'}
                      </span>
                      {!entry.user && entry.kaggle_team_name && (
                        <span className="kaggle-badge">Kaggle</span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="score-column">
                  <span className="score-value">
                    {entry.best_score || entry.score ? parseFloat(entry.best_score || entry.score).toFixed(4) : 'N/A'}
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
