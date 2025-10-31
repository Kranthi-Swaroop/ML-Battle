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
    competition.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    competition.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const competitionStats = {
    total: competitions.length,
    ongoing: competitions.filter(c => c.status === 'ongoing').length,
    upcoming: competitions.filter(c => c.status === 'upcoming').length,
    completed: competitions.filter(c => c.status === 'completed').length
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
      </div>
    </div>
  );
};

export default CompetitionList;
