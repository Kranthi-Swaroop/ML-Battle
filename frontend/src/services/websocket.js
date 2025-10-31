/**
 * WebSocket Service - Manager for real-time connections
 */

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

class WebSocketManager {
  constructor() {
    this.connections = new Map();
  }

  /**
   * Connect to a WebSocket endpoint
   * @param {string} path - WebSocket path (e.g., 'leaderboard/1')
   * @param {Object} callbacks - Event callbacks {onMessage, onOpen, onClose, onError}
   * @returns {WebSocket} WebSocket instance
   */
  connect(path, callbacks = {}) {
    const url = `${WS_URL}/${path}/`;
    
    // Check if connection already exists
    if (this.connections.has(path)) {
      console.warn(`WebSocket connection already exists for ${path}`);
      return this.connections.get(path);
    }

    const ws = new WebSocket(url);

    ws.onopen = (event) => {
      console.log(`WebSocket connected: ${path}`);
      if (callbacks.onOpen) callbacks.onOpen(event);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (callbacks.onMessage) callbacks.onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (event) => {
      console.error(`WebSocket error on ${path}:`, event);
      if (callbacks.onError) callbacks.onError(event);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket closed: ${path}`, event.code, event.reason);
      this.connections.delete(path);
      if (callbacks.onClose) callbacks.onClose(event);
    };

    this.connections.set(path, ws);
    return ws;
  }

  /**
   * Send message through WebSocket
   * @param {string} path - WebSocket path
   * @param {Object} message - Message to send
   */
  send(path, message) {
    const ws = this.connections.get(path);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.error(`WebSocket not connected for ${path}`);
    }
  }

  /**
   * Close WebSocket connection
   * @param {string} path - WebSocket path
   */
  close(path) {
    const ws = this.connections.get(path);
    if (ws) {
      ws.close();
      this.connections.delete(path);
    }
  }

  /**
   * Close all WebSocket connections
   */
  closeAll() {
    this.connections.forEach((ws, path) => {
      ws.close();
    });
    this.connections.clear();
  }

  /**
   * Check if WebSocket is connected
   * @param {string} path - WebSocket path
   * @returns {boolean} Connection status
   */
  isConnected(path) {
    const ws = this.connections.get(path);
    return ws && ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
const wsManager = new WebSocketManager();

export default wsManager;
