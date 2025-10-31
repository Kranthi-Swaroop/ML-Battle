import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { competitionEventsAPI } from '../services/api';
import './Home.css';

const Home = () => {
  const { isAuthenticated, user } = useAuth();
  const [featuredEvents, setFeaturedEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFeaturedEvents();
  }, []);

  const fetchFeaturedEvents = async () => {
    try {
      setLoading(true);
      const response = await competitionEventsAPI.getFeatured();
      setFeaturedEvents(response.data.results || response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section" style={{ position: 'relative' }}>
        {/* LiquidEther Background */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
          <LiquidEther
            colors={['#5227FF', '#FF9FFC', '#B19EEF']}
            mouseForce={10}
            cursorSize={100}
            isViscous={false}
            viscous={30}
            iterationsViscous={32}
            iterationsPoisson={32}
            resolution={0.5}
            isBounce={false}
            autoDemo={true}
            autoSpeed={0.5}
            autoIntensity={2.2}
            takeoverDuration={0.25}
            autoResumeDelay={3000}
            autoRampDuration={0.6}
          />
        </div>
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
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
                  <Link to="/events" className="btn btn-secondary btn-lg">
                    Browse Events
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/events" className="btn btn-primary btn-lg">
                    View Events
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
            <PixelCard variant="blue" className="feature-card">
              <div className="feature-icon">🔗</div>
              <h3 className="feature-title">Kaggle Integration</h3>
              <p className="feature-description">
                Seamlessly sync your Kaggle submissions and track your progress
                across all competitions in one place.
              </p>
            </PixelCard>

            <PixelCard variant="pink" className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Real-time Leaderboards</h3>
              <p className="feature-description">
                Watch live updates as competitors submit and climb the rankings
                with WebSocket-powered leaderboards.
              </p>
            </PixelCard>

            <PixelCard variant="yellow" className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3 className="feature-title">ELO Rating System</h3>
              <p className="feature-description">
                Track your skill progression with our dynamic ELO rating system
                that adapts to competition size and difficulty.
              </p>
            </PixelCard>

            <PixelCard variant="blue" className="feature-card">
              <div className="feature-icon">📈</div>
              <h3 className="feature-title">Progress Analytics</h3>
              <p className="feature-description">
                Visualize your rating history, submission trends, and competition
                performance with detailed charts and graphs.
              </p>
            </PixelCard>

            <PixelCard variant="pink" className="feature-card">
              <div className="feature-icon">🏅</div>
              <h3 className="feature-title">Tier System</h3>
              <p className="feature-description">
                Climb through ranks from Novice to Grandmaster as you improve
                your machine learning skills and compete.
              </p>
            </PixelCard>

            <PixelCard variant="yellow" className="feature-card">
              <div className="feature-icon">👥</div>
              <h3 className="feature-title">Community</h3>
              <p className="feature-description">
                Join a vibrant community of data scientists and machine learning
                enthusiasts passionate about competition.
              </p>
            </PixelCard>
          </div>
        </div>
      </section>

      {/* Featured Events Section */}
      <section className="competitions-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Featured Events</h2>
            <Link to="/events" className="view-all-link">
              View All →
            </Link>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading events...</p>
            </div>
          ) : error ? (
            <div className="alert alert-error">{error}</div>
          ) : featuredEvents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🏆</div>
              <h3 className="empty-state-title">No Featured Events</h3>
              <p className="empty-state-description">
                Check back soon for new events to join!
              </p>
            </div>
          ) : (
            <div className="competitions-grid">
              {featuredEvents.slice(0, 3).map((event) => (
                <Link key={event.id} to={`/events/${event.slug}`} className="event-card-link">
                  <div className="event-card-home">
                    {event.banner_image && (
                      <div className="event-card-banner">
                        <img src={event.banner_image} alt={event.title} />
                      </div>
                    )}
                    <div className="event-card-content">
                      <h3>{event.title}</h3>
                      <p className="event-card-desc">
                        {event.description?.substring(0, 100)}...
                      </p>
                      <div className="event-card-meta">
                        <span>🏆 {event.total_prize_pool || 'TBD'}</span>
                        <span>📊 {event.competition_count || 0} competitions</span>
                      </div>
                      <span className={`event-status-badge status-${event.status}`}>
                        {event.status}
                      </span>
                    </div>
                  </div>
                </Link>
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
