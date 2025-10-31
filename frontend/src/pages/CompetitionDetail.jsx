import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { competitionsAPI } from '../services/api';
import useLeaderboard from '../hooks/useLeaderboard';
import { useAuth } from '../hooks/useAuth';
import Leaderboard from '../components/Leaderboard';
import { formatDate, getTimeRemaining } from '../utils/helpers';
import './CompetitionDetail.css';

const CompetitionDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [competition, setCompetition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [registering, setRegistering] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [syncing, setSyncing] = useState(false);

  const { 
    leaderboard, 
    loading: leaderboardLoading, 
    error: leaderboardError, 
    isConnected 
  } = useLeaderboard(id);

  useEffect(() => {
    fetchCompetition();
  }, [id]);

  const fetchCompetition = async () => {
    try {
      setLoading(true);
      const response = await competitionsAPI.getById(id);
      setCompetition(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching competition:', err);
      setError('Failed to load competition details');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    try {
      setRegistering(true);
      await competitionsAPI.register(id);
      alert('Successfully registered for competition!');
      fetchCompetition(); // Refresh to update registration status
    } catch (err) {
      console.error('Error registering:', err);
      alert('Failed to register for competition');
    } finally {
      setRegistering(false);
    }
  };

  const handleSyncLeaderboard = async () => {
    if (!window.confirm('Fetch latest leaderboard from Kaggle? This will replace all existing entries.')) {
      return;
    }

    try {
      setSyncing(true);
      const response = await competitionsAPI.fetchKaggleLeaderboard(id);
      alert(`Successfully synced ${response.data.entries_created} leaderboard entries from Kaggle!`);
      // The leaderboard will update automatically via WebSocket
    } catch (err) {
      console.error('Error syncing leaderboard:', err);
      alert(err.response?.data?.error || 'Failed to sync leaderboard from Kaggle');
    } finally {
      setSyncing(false);
    }
  };

  // Removed: handleSyncSubmissions - Using leaderboard sync instead
  // The leaderboard sync downloads complete CSV with all entries

  const isAdmin = () => {
    return user?.is_staff || user?.is_superuser;
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading competition...</p>
        </div>
      </div>
    );
  }

  if (error || !competition) {
    return (
      <div className="page-container">
        <div className="alert alert-error">{error || 'Competition not found'}</div>
        <Link to="/competitions" className="btn btn-primary">
          Back to Competitions
        </Link>
      </div>
    );
  }

  const isActive = competition.status === 'ongoing';
  const isUpcoming = competition.status === 'upcoming';
  const isCompleted = competition.status === 'completed';
  const timeRemaining = getTimeRemaining(competition.end_date);

  const getStatusBadge = () => {
    if (isActive) {
      return <span className="badge badge-success">Active</span>;
    } else if (isUpcoming) {
      return <span className="badge badge-warning">Upcoming</span>;
    } else {
      return <span className="badge badge-danger">Completed</span>;
    }
  };

  return (
    <div className="competition-detail-page">
      <div className="page-container">
        {/* Header */}
        <div className="competition-header">
          <div className="competition-header-content">
            <div className="breadcrumb">
              <Link to="/competitions">Competitions</Link>
              <span className="breadcrumb-separator">/</span>
              <span>{competition.title}</span>
            </div>

            <div className="competition-title-section">
              <h1 className="competition-title">{competition.title}</h1>
              <div className="competition-badges">
                {getStatusBadge()}
                <span className={`badge badge-${
                  competition.difficulty === 'beginner' ? 'success' :
                  competition.difficulty === 'intermediate' ? 'warning' : 'danger'
                }`}>
                  {competition.difficulty?.charAt(0).toUpperCase() + competition.difficulty?.slice(1)}
                </span>
              </div>
            </div>

            <p className="competition-description">{competition.description}</p>
          </div>

          <div className="competition-header-actions">
            {isActive && timeRemaining && (
              <div className="countdown-card">
                <span className="countdown-label">Time Remaining</span>
                <span className="countdown-value">
                  {timeRemaining.days > 0 
                    ? `${timeRemaining.days}d ${timeRemaining.hours}h`
                    : `${timeRemaining.hours}h ${timeRemaining.minutes}m`
                  }
                </span>
              </div>
            )}
            
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

            {!isCompleted && (
              <button 
                className="btn btn-primary"
                onClick={handleRegister}
                disabled={registering}
              >
                {registering ? 'Registering...' : 'Register for Competition'}
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">👥</span>
            <div className="stat-content">
              <span className="stat-label">Participants</span>
              <span className="stat-value">{competition.participants_count || 0}</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <span className="stat-label">Submissions</span>
              <span className="stat-value">{competition.submissions_count || 0}</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">🏆</span>
            <div className="stat-content">
              <span className="stat-label">Prize Pool</span>
              <span className="stat-value">${competition.prize_pool || 0}</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📅</span>
            <div className="stat-content">
              <span className="stat-label">Duration</span>
              <span className="stat-value">{competition.duration_days || 0} days</span>
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
                className={`tab-button ${activeTab === 'leaderboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('leaderboard')}
              >
                Leaderboard
              </button>
            </li>
            <li>
              <button
                className={`tab-button ${activeTab === 'rules' ? 'active' : ''}`}
                onClick={() => setActiveTab('rules')}
              >
                Rules
              </button>
            </li>
          </ul>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-content">
              <div className="content-section">
                <h2>About This Competition</h2>
                <p>{competition.description}</p>
                
                <h3>Competition Dates</h3>
                <div className="date-info">
                  <div className="date-item">
                    <strong>Start:</strong> {formatDate(competition.start_date)}
                  </div>
                  <div className="date-item">
                    <strong>End:</strong> {formatDate(competition.end_date)}
                  </div>
                  <div className="date-item">
                    <strong>Duration:</strong> {competition.duration_days} days
                  </div>
                </div>

                <h3>Prize Pool</h3>
                <p className="prize-amount">${competition.prize_pool || 0}</p>

                <h3>Difficulty Level</h3>
                <p>{competition.difficulty?.charAt(0).toUpperCase() + competition.difficulty?.slice(1)}</p>
              </div>

              {competition.rules && (
                <div className="content-section">
                  <h2>Quick Rules</h2>
                  <p>{competition.rules}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'leaderboard' && (
            <div className="leaderboard-content">
              {isAdmin() && competition.kaggle_competition_id && (
                <div className="leaderboard-actions">
                  <div className="action-buttons">
                    <button
                      className="btn btn-primary"
                      onClick={handleSyncLeaderboard}
                      disabled={syncing}
                    >
                      {syncing ? 'Syncing...' : '🔄 Sync Leaderboard'}
                    </button>
                  </div>
                  <p className="sync-info">
                    📊 Downloads complete leaderboard from Kaggle (all 1000+ entries) and updates ranks
                    <br />
                    ⚡ Auto-syncs every 5 minutes via Celery task
                  </p>
                </div>
              )}
              <Leaderboard 
                entries={leaderboard}
                loading={leaderboardLoading}
                error={leaderboardError}
                isConnected={isConnected}
              />
            </div>
          )}

          {activeTab === 'rules' && (
            <div className="rules-content">
              <div className="content-section">
                <h2>Competition Rules</h2>
                {competition.rules ? (
                  <div className="rules-text">
                    {competition.rules}
                  </div>
                ) : (
                  <p>Rules will be announced soon.</p>
                )}

                <h3>Submission Guidelines</h3>
                <ul>
                  <li>All submissions must be made through Kaggle</li>
                  <li>You can make up to 5 submissions per day</li>
                  <li>Your best submission will be used for the leaderboard</li>
                  <li>Private leaderboard will be revealed after competition ends</li>
                </ul>

                <h3>Evaluation Metric</h3>
                <p>Submissions are evaluated based on the specified metric on Kaggle.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompetitionDetail;
