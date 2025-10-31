import React from 'react';
import { Link } from 'react-router-dom';
import { getRatingTier } from '../utils/constants';
import { formatDate, getTimeRemaining } from '../utils/helpers';
import './CompetitionCard.css';

const CompetitionCard = ({ competition }) => {
  const timeRemaining = getTimeRemaining(competition.end_date);
  const isActive = competition.status === 'ongoing';
  const isUpcoming = competition.status === 'upcoming';
  const isCompleted = competition.status === 'completed';

  const getStatusBadge = () => {
    if (isActive) {
      return <span className="badge badge-success">Active</span>;
    } else if (isUpcoming) {
      return <span className="badge badge-warning">Upcoming</span>;
    } else {
      return <span className="badge badge-danger">Completed</span>;
    }
  };

  const getDifficultyBadge = () => {
    const colors = {
      beginner: 'success',
      intermediate: 'warning',
      advanced: 'danger'
    };
    return (
      <span className={`badge badge-${colors[competition.difficulty] || 'primary'}`}>
        {competition.difficulty?.charAt(0).toUpperCase() + competition.difficulty?.slice(1)}
      </span>
    );
  };

  return (
    <div className="competition-card">
      <div className="competition-card-header">
        <div className="competition-card-badges">
          {getStatusBadge()}
          {getDifficultyBadge()}
        </div>
        <h3 className="competition-card-title">
          <Link to={`/competitions/${competition.id}`}>
            {competition.title}
          </Link>
        </h3>
        <p className="competition-card-description">
          {competition.description}
        </p>
      </div>

      <div className="competition-card-body">
        <div className="competition-card-stats">
          <div className="stat-item">
            <span className="stat-icon">👥</span>
            <div className="stat-content">
              <span className="stat-label">Participants</span>
              <span className="stat-value">{competition.participants_count || 0}</span>
            </div>
          </div>

          <div className="stat-item">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <span className="stat-label">Submissions</span>
              <span className="stat-value">{competition.submissions_count || 0}</span>
            </div>
          </div>

          <div className="stat-item">
            <span className="stat-icon">🏆</span>
            <div className="stat-content">
              <span className="stat-label">Prize Pool</span>
              <span className="stat-value">${competition.prize_pool || 0}</span>
            </div>
          </div>
        </div>

        <div className="competition-card-dates">
          <div className="date-item">
            <span className="date-label">Start:</span>
            <span className="date-value">{formatDate(competition.start_date)}</span>
          </div>
          <div className="date-item">
            <span className="date-label">End:</span>
            <span className="date-value">{formatDate(competition.end_date)}</span>
          </div>
        </div>

        {isActive && timeRemaining && (
          <div className="competition-card-countdown">
            <span className="countdown-icon">⏰</span>
            <span className="countdown-text">
              {timeRemaining.days > 0 
                ? `${timeRemaining.days} day${timeRemaining.days > 1 ? 's' : ''} remaining`
                : `${timeRemaining.hours} hour${timeRemaining.hours > 1 ? 's' : ''} remaining`
              }
            </span>
          </div>
        )}

        {isUpcoming && (
          <div className="competition-card-countdown upcoming">
            <span className="countdown-icon">📅</span>
            <span className="countdown-text">Starting soon</span>
          </div>
        )}
      </div>

      <div className="competition-card-footer">
        <Link 
          to={`/competitions/${competition.id}`} 
          className="btn btn-primary"
        >
          {isCompleted ? 'View Results' : 'View Competition'}
        </Link>
        {competition.kaggle_competition_id && (
          <a 
            href={`https://www.kaggle.com/c/${competition.kaggle_competition_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
          >
            View on Kaggle
          </a>
        )}
      </div>
    </div>
  );
};

export default CompetitionCard;
