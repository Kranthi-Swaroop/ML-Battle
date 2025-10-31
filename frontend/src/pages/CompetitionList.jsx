import React, { useEffect, useState } from 'react';
import { competitionsAPI } from '../services/api';
import CompetitionCard from '../components/CompetitionCard';
import './CompetitionList.css';

const CompetitionList = () => {
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, ongoing, upcoming, completed
  const [searchTerm, setSearchTerm] = useState('');
  const [showKaggleSearch, setShowKaggleSearch] = useState(false);
  const [kaggleSearchTerm, setKaggleSearchTerm] = useState('');
  const [kaggleResults, setKaggleResults] = useState([]);
  const [kaggleLoading, setKaggleLoading] = useState(false);
  const [importingIds, setImportingIds] = useState(new Set());
  const [selectedCompetition, setSelectedCompetition] = useState(null);
  const [showScoringForm, setShowScoringForm] = useState(false);
  const [scoringConfig, setScoringConfig] = useState({
    higher_is_better: true,
    metric_min_value: 0.0,
    metric_max_value: 1.0,
    points_for_perfect_score: 100.0
  });

  useEffect(() => {
    fetchCompetitions();
  }, [filter]);

  const fetchCompetitions = async () => {
    try {
      setLoading(true);
      let response;
      
      if (filter === 'ongoing') {
        response = await competitionsAPI.getOngoing();
      } else {
        response = await competitionsAPI.getAll();
      }
      
      let data = response.data.results || response.data;
      
      // Apply filters
      if (filter !== 'all' && filter !== 'ongoing') {
        data = data.filter(comp => comp.status === filter);
      }
      
      setCompetitions(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching competitions:', err);
      setError('Failed to load competitions');
    } finally {
      setLoading(false);
    }
  };

  const filteredCompetitions = competitions.filter(competition =>
    (competition.title && competition.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (competition.description && competition.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const competitionStats = {
    total: competitions.length,
    ongoing: competitions.filter(c => c.status === 'ongoing').length,
    upcoming: competitions.filter(c => c.status === 'upcoming').length,
    completed: competitions.filter(c => c.status === 'completed').length
  };

  const searchKaggleCompetitions = async () => {
    if (!kaggleSearchTerm.trim()) return;
    
    setKaggleLoading(true);
    try {
      const response = await competitionsAPI.searchKaggle(kaggleSearchTerm);
      setKaggleResults(response.data.results || []);
    } catch (err) {
      console.error('Error searching Kaggle:', err);
      alert('Failed to search Kaggle competitions');
    } finally {
      setKaggleLoading(false);
    }
  };

  const handleImportClick = (competition) => {
    setSelectedCompetition(competition);
    setShowScoringForm(true);
  };

  const importCompetition = async () => {
    if (!selectedCompetition) return;
    
    const kaggleId = selectedCompetition.id;
    setImportingIds(prev => new Set(prev).add(kaggleId));
    try {
      const response = await competitionsAPI.importFromKaggle(kaggleId, null, scoringConfig);
      alert(`Competition "${response.data.competition?.title || 'imported'}" imported successfully with scoring config!`);
      
      // Close modals and reset state
      setShowScoringForm(false);
      setSelectedCompetition(null);
      setScoringConfig({
        higher_is_better: true,
        metric_min_value: 0.0,
        metric_max_value: 1.0,
        points_for_perfect_score: 100.0
      });
      
      // Refresh competitions list
      fetchCompetitions();
      // Update Kaggle results to show it's imported
      setKaggleResults(prev => 
        prev.map(comp => 
          comp.id === kaggleId ? { ...comp, imported: true } : comp
        )
      );
    } catch (err) {
      console.error('Error importing competition:', err);
      alert(err.response?.data?.error || 'Failed to import competition');
    } finally {
      setImportingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(kaggleId);
        return newSet;
      });
    }
  };

  return (
    <div className="competition-list-page">
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">Competitions</h1>
          <p className="page-subtitle">
            Browse and join machine learning competitions
          </p>
        </div>

        {/* Stats Overview */}
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total Competitions</span>
            <span className="stat-value">{competitionStats.total}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active</span>
            <span className="stat-value text-success">{competitionStats.ongoing}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Upcoming</span>
            <span className="stat-value text-primary">{competitionStats.upcoming}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Completed</span>
            <span className="stat-value text-gray">{competitionStats.completed}</span>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="filter-section">
          <div className="filter-bar">
            <input
              type="text"
              placeholder="Search competitions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Competitions</option>
              <option value="ongoing">Active</option>
              <option value="upcoming">Upcoming</option>
              <option value="completed">Completed</option>
            </select>

            <button 
              className="btn btn-primary"
              onClick={() => setShowKaggleSearch(true)}
              style={{ marginLeft: '10px' }}
            >
              🔍 Search Kaggle
            </button>
          </div>

          <div className="filter-chips">
            <button
              className={`filter-chip ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={`filter-chip ${filter === 'ongoing' ? 'active' : ''}`}
              onClick={() => setFilter('ongoing')}
            >
              <span className="chip-badge badge-success"></span>
              Active
            </button>
            <button
              className={`filter-chip ${filter === 'upcoming' ? 'active' : ''}`}
              onClick={() => setFilter('upcoming')}
            >
              <span className="chip-badge badge-warning"></span>
              Upcoming
            </button>
            <button
              className={`filter-chip ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => setFilter('completed')}
            >
              <span className="chip-badge badge-danger"></span>
              Completed
            </button>
          </div>
        </div>

        {/* Competitions Grid */}
        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading competitions...</p>
          </div>
        ) : error ? (
          <div className="alert alert-error">{error}</div>
        ) : filteredCompetitions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <h3 className="empty-state-title">No Competitions Found</h3>
            <p className="empty-state-description">
              {searchTerm 
                ? `No competitions match "${searchTerm}"`
                : 'No competitions available with the current filter'
              }
            </p>
            {(searchTerm || filter !== 'all') && (
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setSearchTerm('');
                  setFilter('all');
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="results-count">
              Showing {filteredCompetitions.length} competition{filteredCompetitions.length !== 1 ? 's' : ''}
            </div>
            <div className="competitions-grid">
              {filteredCompetitions.map((competition) => (
                <CompetitionCard key={competition.id} competition={competition} />
              ))}
            </div>
          </>
        )}

        {/* Kaggle Search Modal */}
        {showKaggleSearch && (
          <div className="modal-overlay" onClick={() => setShowKaggleSearch(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Search Kaggle Competitions</h2>
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
                                {importingIds.has(comp.id) ? 'Importing...' : 'Import'}
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

export default CompetitionList;
