/**
 * useWebSocket Hook - WebSocket connection management
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import wsManager from '../services/websocket';

/**
 * Custom hook for WebSocket connections
 * @param {string} path - WebSocket path
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket state and methods
 */
const useWebSocket = (path, options = {}) => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!path) return;

    try {
      wsRef.current = wsManager.connect(path, {
        onOpen: (event) => {
          setIsConnected(true);
          setError(null);
          if (onOpen) onOpen(event);
        },
        onMessage: (data) => {
          setLastMessage(data);
          if (onMessage) onMessage(data);
        },
        onClose: (event) => {
          setIsConnected(false);
          if (onClose) onClose(event);
          
          // Attempt to reconnect
          if (reconnect && mountedRef.current) {
            reconnectTimerRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
          }
        },
        onError: (event) => {
          setError(event);
          if (onError) onError(event);
        },
      });
    } catch (err) {
      setError(err);
      console.error('WebSocket connection error:', err);
    }
  }, [path, onMessage, onOpen, onClose, onError, reconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    if (path) {
      wsManager.close(path);
    }
    setIsConnected(false);
  }, [path]);

  const sendMessage = useCallback((message) => {
    if (path && isConnected) {
      wsManager.send(path, message);
    } else {
      console.warn('WebSocket not connected. Cannot send message.');
    }
  }, [path, isConnected]);

  useEffect(() => {
    if (autoConnect && path) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, path, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    connect,
    disconnect,
  };
};

export default useWebSocket;
