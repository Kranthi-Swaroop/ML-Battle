import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { competitionsAPI } from '../services/api';
import CompetitionCard from '../components/CompetitionCard';
import './Home.css';

const Home = () => {
  const { isAuthenticated, user } = useAuth();
  const [ongoingCompetitions, setOngoingCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOngoingCompetitions();
  }, []);

  const fetchOngoingCompetitions = async () => {
    try {
      setLoading(true);
      const response = await competitionsAPI.getOngoing();
      setOngoingCompetitions(response.data.results || response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching competitions:', err);
      setError('Failed to load competitions');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Welcome to <span className="gradient-text">MLBattle</span>
            </h1>
            <p className="hero-subtitle">
              Compete in machine learning competitions, climb the leaderboard,
              and showcase your data science skills with Kaggle integration.
            </p>
            <div className="hero-actions">
              {!isAuthenticated ? (
                <>
                  <Link to="/register" className="btn btn-primary btn-lg">
                    Get Started
                  </Link>
                  <Link to="/competitions" className="btn btn-secondary btn-lg">
                    Browse Competitions
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/competitions" className="btn btn-primary btn-lg">
                    View Competitions
                  </Link>
                  <Link to="/profile" className="btn btn-secondary btn-lg">
                    My Profile
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Hero Stats */}
          {isAuthenticated && user && (
            <div className="hero-stats">
              <div className="hero-stat-card">
                <span className="stat-icon">⭐</span>
                <div className="stat-content">
                  <span className="stat-label">Your Rating</span>
                  <span className="stat-value">{user.elo_rating || 1500}</span>
                </div>
              </div>
              <div className="hero-stat-card">
                <span className="stat-icon">🏆</span>
                <div className="stat-content">
                  <span className="stat-label">Highest Rating</span>
                  <span className="stat-value">{user.highest_rating || user.elo_rating || 1500}</span>
                </div>
              </div>
              <div className="hero-stat-card">
                <span className="stat-icon">🎯</span>
                <div className="stat-content">
                  <span className="stat-label">Competitions</span>
                  <span className="stat-value">{user.competitions_participated || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Why MLBattle?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔗</div>
              <h3 className="feature-title">Kaggle Integration</h3>
              <p className="feature-description">
                Seamlessly sync your Kaggle submissions and track your progress
                across all competitions in one place.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Real-time Leaderboards</h3>
              <p className="feature-description">
                Watch live updates as competitors submit and climb the rankings
                with WebSocket-powered leaderboards.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3 className="feature-title">ELO Rating System</h3>
              <p className="feature-description">
                Track your skill progression with our dynamic ELO rating system
                that adapts to competition size and difficulty.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3 className="feature-title">Progress Analytics</h3>
              <p className="feature-description">
                Visualize your rating history, submission trends, and competition
                performance with detailed charts and graphs.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🏅</div>
              <h3 className="feature-title">Tier System</h3>
              <p className="feature-description">
                Climb through ranks from Novice to Grandmaster as you improve
                your machine learning skills and compete.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3 className="feature-title">Community</h3>
              <p className="feature-description">
                Join a vibrant community of data scientists and machine learning
                enthusiasts passionate about competition.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Active Competitions Section */}
      <section className="competitions-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Active Competitions</h2>
            <Link to="/competitions" className="view-all-link">
              View All →
            </Link>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading competitions...</p>
            </div>
          ) : error ? (
            <div className="alert alert-error">{error}</div>
          ) : ongoingCompetitions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🏆</div>
              <h3 className="empty-state-title">No Active Competitions</h3>
              <p className="empty-state-description">
                Check back soon for new competitions to join!
              </p>
            </div>
          ) : (
            <div className="competitions-grid">
              {ongoingCompetitions.slice(0, 3).map((competition) => (
                <CompetitionCard key={competition.id} competition={competition} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      {!isAuthenticated && (
        <section className="cta-section">
          <div className="container">
            <div className="cta-content">
              <h2 className="cta-title">Ready to Start Competing?</h2>
              <p className="cta-description">
                Join thousands of data scientists testing their skills in real-world
                machine learning competitions.
              </p>
              <Link to="/register" className="btn btn-primary btn-lg">
                Create Your Account
              </Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default Home;
