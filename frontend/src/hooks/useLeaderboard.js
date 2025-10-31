/**
 * useLeaderboard Hook - Leaderboard data with WebSocket updates
 */
import { useState, useEffect, useCallback } from 'react';
import { leaderboardAPI } from '../services/api';
import useWebSocket from './useWebSocket';

/**
 * Custom hook for leaderboard with real-time updates
 * @param {number} competitionId - Competition ID
 * @returns {Object} Leaderboard state and methods
 */
const useLeaderboard = (competitionId) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch initial leaderboard data
  const fetchLeaderboard = useCallback(async () => {
    if (!competitionId) return;

    try {
      setLoading(true);
      const response = await leaderboardAPI.getByCompetition(competitionId);
      // Handle paginated response - extract results array
      const data = response.data?.results || response.data || [];
      // Ensure data is an array
      const entries = Array.isArray(data) ? data : [];
      setLeaderboard(entries);
      setError(null);
    } catch (err) {
      setError(err);
      console.error('Failed to fetch leaderboard:', err);
      setLeaderboard([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  }, [competitionId]);

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage } = useWebSocket(
    competitionId ? `leaderboard/${competitionId}` : null,
    {
      onMessage: (data) => {
        if (data.type === 'leaderboard_update' || data.type === 'leaderboard_init') {
          // Ensure entries is an array
          const entries = Array.isArray(data.data?.entries) ? data.data.entries : [];
          setLeaderboard(entries);
        }
      },
      autoConnect: !!competitionId,
    }
  );

  // Initial fetch
  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const refresh = () => {
    fetchLeaderboard();
  };

  return {
    leaderboard,
    loading,
    error,
    isConnected,
    refresh,
  };
};

export { useLeaderboard };
export default useLeaderboard;
