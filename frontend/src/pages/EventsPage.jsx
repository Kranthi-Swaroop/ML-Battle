import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { competitionEventsAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import './EventsPage.css';

const EventsPage = () => {
  const { isAdmin } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    organizer: '',
    total_prize_pool: '',
    banner_image: '',
    is_featured: false
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await competitionEventsAPI.getAll();
      setEvents(response.data.results || response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await competitionEventsAPI.create(formData);
      alert('Event created successfully!');
      setShowCreateModal(false);
      setFormData({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        organizer: '',
        total_prize_pool: '',
        banner_image: '',
        is_featured: false
      });
      fetchEvents();
    } catch (err) {
      console.error('Error creating event:', err);
      alert(err.response?.data?.error || 'Failed to create event');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      upcoming: { class: 'badge-warning', text: 'Upcoming' },
      ongoing: { class: 'badge-success', text: 'Ongoing' },
      completed: { class: 'badge-gray', text: 'Completed' }
    };
    const badge = badges[status] || badges.upcoming;
    return <span className={`badge ${badge.class}`}>{badge.text}</span>;
  };

  return (
    <div className="events-page">
      <div className="page-container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Competition Events</h1>
            <p className="page-subtitle">
              Create and manage competition events like "Neural Night"
            </p>
          </div>
          {isAdmin() && (
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              + Create Event
            </button>
          )}
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading events...</p>
          </div>
        ) : error ? (
          <div className="alert alert-error">{error}</div>
        ) : events.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🎯</div>
            <h3 className="empty-state-title">No Events Yet</h3>
            <p className="empty-state-description">
              Create your first competition event to organize multiple Kaggle competitions
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create First Event
            </button>
          </div>
        ) : (
          <div className="events-grid">
            {events.map((event) => (
              <div 
                key={event.id} 
                className="event-card"
                onClick={() => navigate(`/events/${event.slug}`)}
              >
                {event.banner_image && (
                  <div className="event-banner">
                    <img src={event.banner_image} alt={event.title} />
                  </div>
                )}
                <div className="event-card-content">
                  <div className="event-header">
                    <h3>{event.title}</h3>
                    {getStatusBadge(event.status)}
                  </div>
                  <p className="event-description">
                    {event.description?.substring(0, 120)}...
                  </p>
                  <div className="event-meta">
                    {event.organizer && (
                      <span>👥 {event.organizer}</span>
                    )}
                    {event.total_prize_pool && (
                      <span>🏆 {event.total_prize_pool}</span>
                    )}
                    <span>📊 {event.competition_count} competitions</span>
                  </div>
                  <div className="event-dates">
                    <span>📅 {new Date(event.start_date).toLocaleDateString()}</span>
                    <span>→</span>
                    <span>{new Date(event.end_date).toLocaleDateString()}</span>
                  </div>
                  {event.is_featured && (
                    <div className="featured-badge">⭐ Featured</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Event Modal */}
        {showCreateModal && (
          <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
            <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Create Competition Event</h2>
                <button 
                  className="modal-close"
                  onClick={() => setShowCreateModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="modal-body">
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label htmlFor="title">Event Title *</label>
                    <input
                      type="text"
                      id="title"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      placeholder="e.g., Neural Night 2025"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="description">Description *</label>
                    <textarea
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      placeholder="Describe your competition event..."
                      rows="4"
                      required
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="start_date">Start Date *</label>
                      <input
                        type="datetime-local"
                        id="start_date"
                        name="start_date"
                        value={formData.start_date}
                        onChange={handleInputChange}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="end_date">End Date *</label>
                      <input
                        type="datetime-local"
                        id="end_date"
                        name="end_date"
                        value={formData.end_date}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="organizer">Organizer</label>
                      <input
                        type="text"
                        id="organizer"
                        name="organizer"
                        value={formData.organizer}
                        onChange={handleInputChange}
                        placeholder="e.g., ML Battle Team"
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="total_prize_pool">Total Prize Pool</label>
                      <input
                        type="text"
                        id="total_prize_pool"
                        name="total_prize_pool"
                        value={formData.total_prize_pool}
                        onChange={handleInputChange}
                        placeholder="e.g., $100,000"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="banner_image">Banner Image URL</label>
                    <input
                      type="url"
                      id="banner_image"
                      name="banner_image"
                      value={formData.banner_image}
                      onChange={handleInputChange}
                      placeholder="https://example.com/banner.jpg"
                    />
                  </div>

                  <div className="form-group checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        name="is_featured"
                        checked={formData.is_featured}
                        onChange={handleInputChange}
                      />
                      <span>Mark as Featured Event</span>
                    </label>
                  </div>

                  <div className="form-actions">
                    <button 
                      type="button" 
                      className="btn btn-secondary"
                      onClick={() => setShowCreateModal(false)}
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Create Event
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventsPage;
