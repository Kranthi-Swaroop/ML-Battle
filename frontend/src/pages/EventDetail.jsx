import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { competitionEventsAPI, competitionsAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import CompetitionCard from '../components/CompetitionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import './EventDetail.css';

const EventDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [event, setEvent] = useState(null);
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showKaggleSearch, setShowKaggleSearch] = useState(false);
  const [kaggleSearchTerm, setKaggleSearchTerm] = useState('');
  const [kaggleResults, setKaggleResults] = useState([]);
  const [kaggleLoading, setKaggleLoading] = useState(false);
  const [importingIds, setImportingIds] = useState(new Set());
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCompetition, setSelectedCompetition] = useState(null);
  const [showScoringForm, setShowScoringForm] = useState(false);
  const [scoringConfig, setScoringConfig] = useState({
    higher_is_better: true,
    metric_min_value: 0.0,
    metric_max_value: 1.0,
    points_for_perfect_score: 100.0
  });
  const [overallLeaderboard, setOverallLeaderboard] = useState([]);
  const [leaderboardLoading, setLeaderboardLoading] = useState(false);

  const fetchEventDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Parallel fetch for better performance
      const [eventRes, competitionsRes] = await Promise.all([
        competitionEventsAPI.getById(slug),
        competitionEventsAPI.getCompetitions(slug)
      ]);
      
      setEvent(eventRes.data);
      setCompetitions(competitionsRes.data);
    } catch (err) {
      console.error('Error fetching event:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to load event details';
      setError(errorMsg);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [slug]);

  const fetchOverallLeaderboard = useCallback(async () => {
    if (!slug) return;
    
    try {
      setLeaderboardLoading(true);
      const response = await competitionEventsAPI.getOverallLeaderboard(slug);
      setOverallLeaderboard(response.data.entries || []);
    } catch (err) {
      console.error('Error fetching overall leaderboard:', err);
      setOverallLeaderboard([]);
    } finally {
      setLeaderboardLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchEventDetails();
    fetchOverallLeaderboard();
  }, [fetchEventDetails, fetchOverallLeaderboard]);

  const searchKaggleCompetitions = useCallback(async () => {
    if (!kaggleSearchTerm.trim()) {
      alert('Please enter a search term');
      return;
    }
    
    setKaggleLoading(true);
    try {
      const response = await competitionsAPI.searchKaggle(kaggleSearchTerm);
      setKaggleResults(response.data.results || []);
    } catch (err) {
      console.error('Error searching Kaggle:', err);
      const errorMsg = err.response?.data?.error || 'Failed to search Kaggle competitions';
      alert(errorMsg);
    } finally {
      setKaggleLoading(false);
    }
  }, [kaggleSearchTerm]);

  const handleImportClick = useCallback((competition) => {
    setSelectedCompetition(competition);
    setShowScoringForm(true);
  }, []);

  const importCompetition = useCallback(async () => {
    if (!event?.id || !selectedCompetition) {
      alert('Event or competition not loaded. Please try again.');
      return;
    }

    const kaggleId = selectedCompetition.id;
    console.log('🚀 Importing competition:', kaggleId, 'to event:', event.id);
    console.log('📊 Scoring config:', scoringConfig);
    setImportingIds(prev => new Set(prev).add(kaggleId));
    
    try {
      const response = await competitionsAPI.importFromKaggle(kaggleId, event.id, scoringConfig);
      console.log('✅ Import successful:', response.data);
      
      // Show success message
      alert(`Competition "${response.data.competition?.title || 'imported'}" added successfully with scoring config!`);
      
      // Mark as imported in search results
      setKaggleResults(prev => 
        prev.map(comp => 
          comp.id === kaggleId ? { ...comp, imported: true } : comp
        )
      );
      
      // Close modals and reset state
      setShowScoringForm(false);
      setSelectedCompetition(null);
      setScoringConfig({
        higher_is_better: true,
        metric_min_value: 0.0,
        metric_max_value: 1.0,
        points_for_perfect_score: 100.0
      });
      
      // Refresh event data with a small delay
      setRefreshing(true);
      setTimeout(() => {
        fetchEventDetails();
        fetchOverallLeaderboard();
      }, 800);
      
    } catch (err) {
      console.error('❌ Error importing competition:', err);
      console.error('Error response:', err.response?.data);
      
      // Extract meaningful error message
      let errorMsg = 'Failed to import competition';
      if (err.response?.data) {
        const data = err.response.data;
        if (data.error) {
          errorMsg = data.error;
          if (data.competition_title) {
            errorMsg += `\n\nCompetition: "${data.competition_title}"`;
          }
        } else if (data.detail) {
          errorMsg = data.detail;
        }
      } else if (err.message) {
        errorMsg = `Network error: ${err.message}`;
      }
      
      alert(errorMsg);
    } finally {
      setImportingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(selectedCompetition?.id);
        return newSet;
      });
    }
  }, [event, selectedCompetition, scoringConfig, fetchEventDetails]);

  if (loading) {
    return <LoadingSpinner message="Loading event details..." fullScreen />;
  }

  if (error || !event) {
    return (
      <div className="page-container">
        <div className="alert alert-error">{error || 'Event not found'}</div>
        <button className="btn btn-secondary" onClick={() => navigate('/events')}>
          Back to Events
        </button>
      </div>
    );
  }

  return (
    <div className="event-detail-page">
      <div className="page-container">
        {/* Event Header */}
        {event.banner_image && (
          <div className="event-banner-large">
            <img src={event.banner_image} alt={event.title} />
            <div className="event-banner-overlay"></div>
          </div>
        )}

        <div className="event-detail-header">
          <button className="btn btn-secondary btn-back" onClick={() => navigate('/events')}>
            ← Back to Events
          </button>
          
          <div className="event-title-section">
            <h1>{event.title}</h1>
            <span className={`status-badge status-${event.status}`}>
              {event.status}
            </span>
          </div>

          <p className="event-description-full">{event.description}</p>

          <div className="event-info-grid">
            {event.organizer && (
              <div className="info-item">
                <span className="info-label">👥 Organizer</span>
                <span className="info-value">{event.organizer}</span>
              </div>
            )}
            {event.total_prize_pool && (
              <div className="info-item">
                <span className="info-label">🏆 Prize Pool</span>
                <span className="info-value">{event.total_prize_pool}</span>
              </div>
            )}
            <div className="info-item">
              <span className="info-label">📅 Start Date</span>
              <span className="info-value">{new Date(event.start_date).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <span className="info-label">📅 End Date</span>
              <span className="info-value">{new Date(event.end_date).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <span className="info-label">📊 Competitions</span>
              <span className="info-value">{competitions.length}</span>
            </div>
          </div>

          {isAdmin() && (
            <button 
              className="btn btn-primary"
              onClick={() => setShowKaggleSearch(true)}
            >
              + Import Kaggle Competition
            </button>
          )}
        </div>

        {/* Overall Event Leaderboard */}
        {competitions.length > 0 && (
          <div className="event-overall-leaderboard-section">
            <div className="section-header">
              <h2>
                <span className="section-icon">🏆</span>
                Overall Event Leaderboard
              </h2>
              <p className="section-description">
                Aggregated scores from all {competitions.length} competitions in this event
              </p>
            </div>

            {leaderboardLoading ? (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading overall leaderboard...</p>
              </div>
            ) : overallLeaderboard.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <h3>No Leaderboard Data Yet</h3>
                <p>Sync competition leaderboards to see overall rankings</p>
              </div>
            ) : (
              <div className="overall-leaderboard-table-container">
                <table className="overall-leaderboard-table">
                  <thead>
                    <tr>
                      <th className="rank-column">Rank</th>
                      <th className="team-column">Team Name</th>
                      <th className="participated-column">Participated</th>
                      <th className="average-score-column">Avg Score</th>
                      <th className="total-score-column">Total Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {overallLeaderboard.map((entry) => (
                      <tr 
                        key={entry.rank} 
                        className={`leaderboard-row ${
                          entry.rank === 1 ? 'rank-gold' : 
                          entry.rank === 2 ? 'rank-silver' : 
                          entry.rank === 3 ? 'rank-bronze' : ''
                        }`}
                        title={`Participated in ${entry.competitions_participated}/${competitions.length} competitions${entry.missing_competitions > 0 ? ` (Missing ${entry.missing_competitions})` : ''}`}
                      >
                        <td className="rank-column">
                          <span className="rank-value">
                            {entry.rank === 1 ? '🥇' : 
                             entry.rank === 2 ? '🥈' : 
                             entry.rank === 3 ? '🥉' : 
                             entry.rank}
                          </span>
                        </td>
                        <td className="team-column">
                          <div className="team-info">
                            <div className="team-avatar">
                              {entry.team_name?.charAt(0).toUpperCase()}
                            </div>
                            <span className="team-name">{entry.team_name}</span>
                          </div>
                        </td>
                        <td className="participated-column">
                          <span className={`participated-badge ${entry.missing_competitions > 0 ? 'incomplete' : 'complete'}`}>
                            {entry.competitions_participated} / {competitions.length}
                          </span>
                          {entry.missing_competitions > 0 && (
                            <span className="missing-indicator" title={`Missing ${entry.missing_competitions} competition(s)`}>
                              ⚠️
                            </span>
                          )}
                        </td>
                        <td className="average-score-column">
                          <span className="average-score-value">
                            {entry.average_score?.toFixed(2) || '0.00'}
                          </span>
                          <span className="score-unit">pts</span>
                        </td>
                        <td className="total-score-column">
                          <span className="total-score-value">
                            {entry.total_score?.toFixed(2) || '0.00'}
                          </span>
                          <span className="score-unit">pts</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Competitions List */}
        <div className="event-competitions-section">
          <h2>Competitions in this Event</h2>
          
          {competitions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🎯</div>
              <h3>No Competitions Yet</h3>
              <p>{isAdmin() ? 'Import Kaggle competitions to add them to this event' : 'Check back later for competitions'}</p>
              {isAdmin() && (
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowKaggleSearch(true)}
                >
                  Import First Competition
                </button>
              )}
            </div>
          ) : (
            <div className="competitions-grid">
              {competitions.map((competition) => (
                <CompetitionCard key={competition.id} competition={competition} />
              ))}
            </div>
          )}
        </div>

        {/* Kaggle Search Modal */}
        {showKaggleSearch && (
          <div className="modal-overlay" onClick={() => setShowKaggleSearch(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Import Kaggle Competition to {event.title}</h2>
                <button 
                  className="modal-close"
                  onClick={() => setShowKaggleSearch(false)}
                >
                  ×
                </button>
              </div>

              <div className="modal-body">
                <div className="kaggle-search-bar">
                  <input
                    type="text"
                    placeholder="Search Kaggle competitions..."
                    value={kaggleSearchTerm}
                    onChange={(e) => setKaggleSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchKaggleCompetitions()}
                    className="search-input"
                  />
                  <button 
                    className="btn btn-primary"
                    onClick={searchKaggleCompetitions}
                    disabled={kaggleLoading}
                  >
                    {kaggleLoading ? 'Searching...' : 'Search'}
                  </button>
                </div>

                <div className="kaggle-results">
                  {kaggleLoading ? (
                    <div className="loading-container">
                      <div className="spinner"></div>
                      <p>Searching Kaggle...</p>
                    </div>
                  ) : kaggleResults.length > 0 ? (
                    <div className="kaggle-results-list">
                      {kaggleResults.map((comp) => (
                        <div key={comp.id} className="kaggle-result-item">
                          <div className="kaggle-result-info">
                            <h3>{comp.title}</h3>
                            <p className="kaggle-result-desc">
                              {comp.description?.substring(0, 150)}...
                            </p>
                            <div className="kaggle-result-meta">
                              <span>🏆 {comp.reward}</span>
                              <span>👥 {comp.teamCount} teams</span>
                              {comp.deadline && (
                                <span>📅 {new Date(comp.deadline).toLocaleDateString()}</span>
                              )}
                            </div>
                          </div>
                          <div className="kaggle-result-actions">
                            {comp.imported ? (
                              <span className="badge badge-success">✓ Imported</span>
                            ) : (
                              <button
                                className="btn btn-primary btn-sm"
                                onClick={() => handleImportClick(comp)}
                                disabled={importingIds.has(comp.id)}
                              >
                                {importingIds.has(comp.id) ? 'Importing...' : 'Import to Event'}
                              </button>
                            )}
                            <a
                              href={comp.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn btn-secondary btn-sm"
                            >
                              View on Kaggle
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : kaggleSearchTerm ? (
                    <div className="empty-state">
                      <p>No results found. Try a different search term.</p>
                    </div>
                  ) : (
                    <div className="empty-state">
                      <p>Enter a search term to find Kaggle competitions</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scoring Configuration Modal */}
        {showScoringForm && selectedCompetition && (
          <div className="modal-overlay" onClick={() => setShowScoringForm(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Configure Scoring for {selectedCompetition.title}</h2>
                <button 
                  className="modal-close"
                  onClick={() => setShowScoringForm(false)}
                >
                  ×
                </button>
              </div>

              <div className="modal-body">
                <div className="scoring-form">
                  <p className="form-description">
                    Set up how scores from Kaggle will be normalized to calculate final rankings.
                    Scores will be calculated using the formula based on the metric direction.
                  </p>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={scoringConfig.higher_is_better}
                        onChange={(e) => setScoringConfig({
                          ...scoringConfig,
                          higher_is_better: e.target.checked
                        })}
                      />
                      <strong>Higher is Better</strong>
                    </label>
                    <p className="help-text">
                      {scoringConfig.higher_is_better 
                        ? '✓ Higher scores = better performance (e.g., Accuracy, F1-Score)'
                        : '✗ Lower scores = better performance (e.g., Error, Loss)'}
                    </p>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Minimum Metric Value</label>
                      <input
                        type="number"
                        step="0.01"
                        value={scoringConfig.metric_min_value}
                        onChange={(e) => setScoringConfig({
                          ...scoringConfig,
                          metric_min_value: parseFloat(e.target.value) || 0
                        })}
                        className="form-control"
                      />
                      <p className="help-text">Worst possible score in the competition</p>
                    </div>

                    <div className="form-group">
                      <label>Maximum Metric Value</label>
                      <input
                        type="number"
                        step="0.01"
                        value={scoringConfig.metric_max_value}
                        onChange={(e) => setScoringConfig({
                          ...scoringConfig,
                          metric_max_value: parseFloat(e.target.value) || 1
                        })}
                        className="form-control"
                      />
                      <p className="help-text">Best possible score in the competition</p>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Points for Perfect Score</label>
                    <input
                      type="number"
                      step="1"
                      value={scoringConfig.points_for_perfect_score}
                      onChange={(e) => setScoringConfig({
                        ...scoringConfig,
                        points_for_perfect_score: parseFloat(e.target.value) || 100
                      })}
                      className="form-control"
                    />
                    <p className="help-text">Maximum points a participant can earn (default: 100)</p>
                  </div>

                  <div className="formula-preview">
                    <strong>Formula Preview:</strong>
                    <code>
                      {scoringConfig.higher_is_better 
                        ? `points = (value - ${scoringConfig.metric_min_value}) / (${scoringConfig.metric_max_value} - ${scoringConfig.metric_min_value}) × ${scoringConfig.points_for_perfect_score}`
                        : `points = (${scoringConfig.metric_max_value} - value) / (${scoringConfig.metric_max_value} - ${scoringConfig.metric_min_value}) × ${scoringConfig.points_for_perfect_score}`
                      }
                    </code>
                  </div>

                  <div className="form-actions">
                    <button
                      className="btn btn-secondary"
                      onClick={() => setShowScoringForm(false)}
                    >
                      Cancel
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={importCompetition}
                      disabled={importingIds.has(selectedCompetition.id)}
                    >
                      {importingIds.has(selectedCompetition.id) ? 'Importing...' : 'Import Competition'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventDetail;
