import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { getRatingTier } from '../utils/constants';
import './RatingChart.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const RatingChart = ({ ratingHistory, loading, error }) => {
  if (loading) {
    return (
      <div className="rating-chart-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading rating history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rating-chart-container">
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!ratingHistory || ratingHistory.length === 0) {
    return (
      <div className="rating-chart-container">
        <div className="empty-state">
          <div className="empty-state-icon">📈</div>
          <h3 className="empty-state-title">No Rating History</h3>
          <p className="empty-state-description">
            Participate in competitions to build your rating history!
          </p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const labels = ratingHistory.map(entry => 
    new Date(entry.updated_at || entry.created_at).toLocaleDateString()
  );
  
  const ratings = ratingHistory.map(entry => entry.new_rating);
  
  const currentRating = ratings[ratings.length - 1];
  const currentTier = getRatingTier(currentRating);

  const data = {
    labels,
    datasets: [
      {
        label: 'Rating',
        data: ratings,
        borderColor: currentTier.color,
        backgroundColor: `${currentTier.color}20`,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: currentTier.color,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        fill: true,
        tension: 0.4
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          label: function(context) {
            const rating = context.parsed.y;
            const tier = getRatingTier(rating);
            return [
              `Rating: ${rating}`,
              `Tier: ${tier.name}`
            ];
          },
          afterLabel: function(context) {
            const index = context.dataIndex;
            if (index > 0) {
              const change = ratings[index] - ratings[index - 1];
              return `Change: ${change > 0 ? '+' : ''}${change}`;
            }
            return '';
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function(value) {
            return value.toLocaleString();
          }
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  // Calculate stats
  const highestRating = Math.max(...ratings);
  const lowestRating = Math.min(...ratings);
  const ratingChange = ratings[ratings.length - 1] - ratings[0];
  const avgChange = ratings.length > 1 
    ? ratingChange / (ratings.length - 1) 
    : 0;

  return (
    <div className="rating-chart-container">
      <div className="rating-chart-header">
        <h2 className="rating-chart-title">
          <span className="chart-icon">📈</span>
          Rating Progress
        </h2>
        <div className="current-tier-badge" style={{ backgroundColor: `${currentTier.color}20`, color: currentTier.color }}>
          {currentTier.name}
        </div>
      </div>

      <div className="rating-stats">
        <div className="rating-stat">
          <span className="stat-label">Current</span>
          <span className="stat-value" style={{ color: currentTier.color }}>
            {currentRating}
          </span>
        </div>
        <div className="rating-stat">
          <span className="stat-label">Highest</span>
          <span className="stat-value">{highestRating}</span>
        </div>
        <div className="rating-stat">
          <span className="stat-label">Lowest</span>
          <span className="stat-value">{lowestRating}</span>
        </div>
        <div className="rating-stat">
          <span className="stat-label">Total Change</span>
          <span className={`stat-value ${ratingChange >= 0 ? 'positive' : 'negative'}`}>
            {ratingChange > 0 ? '+' : ''}{ratingChange}
          </span>
        </div>
        <div className="rating-stat">
          <span className="stat-label">Avg Change</span>
          <span className={`stat-value ${avgChange >= 0 ? 'positive' : 'negative'}`}>
            {avgChange > 0 ? '+' : ''}{avgChange.toFixed(1)}
          </span>
        </div>
      </div>

      <div className="rating-chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default RatingChart;
