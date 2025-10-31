import React from 'react';
import { formatDateTime, formatScore } from '../utils/helpers';
import './SubmissionHistory.css';

const SubmissionHistory = ({ submissions, loading, error }) => {
  if (loading) {
    return (
      <div className="submission-history-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading submissions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="submission-history-container">
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!submissions || submissions.length === 0) {
    return (
      <div className="submission-history-container">
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <h3 className="empty-state-title">No Submissions Yet</h3>
          <p className="empty-state-description">
            Your submission history will appear here once you make your first submission!
          </p>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { class: 'badge-warning', text: 'Pending' },
      processing: { class: 'badge-primary', text: 'Processing' },
      scored: { class: 'badge-success', text: 'Scored' },
      failed: { class: 'badge-danger', text: 'Failed' }
    };

    const statusInfo = statusMap[status] || { class: 'badge-primary', text: status };

    return (
      <span className={`badge ${statusInfo.class}`}>
        {statusInfo.text}
      </span>
    );
  };

  return (
    <div className="submission-history-container">
      <div className="submission-history-header">
        <h2 className="submission-history-title">
          <span className="history-icon">📝</span>
          Submission History
        </h2>
        <span className="submission-count">
          {submissions.length} submission{submissions.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="submissions-list">
        {submissions.map((submission) => (
          <div key={submission.id} className="submission-item">
            <div className="submission-header">
              <div className="submission-info">
                <h4 className="submission-competition">
                  {submission.competition_title || 'Competition'}
                </h4>
                <span className="submission-date">
                  {formatDateTime(submission.submitted_at || submission.created_at)}
                </span>
              </div>
              <div className="submission-status">
                {getStatusBadge(submission.status)}
              </div>
            </div>

            <div className="submission-body">
              <div className="submission-metrics">
                <div className="metric-item">
                  <span className="metric-icon">🎯</span>
                  <div className="metric-content">
                    <span className="metric-label">Public Score</span>
                    <span className="metric-value">
                      {submission.public_score 
                        ? formatScore(submission.public_score) 
                        : 'N/A'
                      }
                    </span>
                  </div>
                </div>

                <div className="metric-item">
                  <span className="metric-icon">🔒</span>
                  <div className="metric-content">
                    <span className="metric-label">Private Score</span>
                    <span className="metric-value">
                      {submission.private_score 
                        ? formatScore(submission.private_score) 
                        : 'Hidden'
                      }
                    </span>
                  </div>
                </div>

                <div className="metric-item">
                  <span className="metric-icon">📊</span>
                  <div className="metric-content">
                    <span className="metric-label">Public Rank</span>
                    <span className="metric-value">
                      {submission.public_rank || 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="metric-item">
                  <span className="metric-icon">🏆</span>
                  <div className="metric-content">
                    <span className="metric-label">Private Rank</span>
                    <span className="metric-value">
                      {submission.private_rank || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {submission.description && (
                <div className="submission-description">
                  <p>{submission.description}</p>
                </div>
              )}

              {submission.kaggle_submission_url && (
                <div className="submission-link">
                  <a 
                    href={submission.kaggle_submission_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary btn-sm"
                  >
                    View on Kaggle
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubmissionHistory;
