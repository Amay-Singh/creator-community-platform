class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
    this.listeners = new Map();
    this.isConnecting = false;
    this.shouldReconnect = true;
  }

  connect(token) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting) {
      return Promise.reject(new Error('Already connecting'));
    }

    this.isConnecting = true;
    const wsUrl = `ws://localhost:8000/ws/notifications/?token=${token}`;

    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.emit('connected');
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          if (this.shouldReconnect && event.code !== 1000) {
            this.attemptReconnect(token);
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          this.emit('error', error);
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect() {
    this.shouldReconnect = false;
    if (this.socket) {
      this.socket.close(1000, 'User disconnected');
      this.socket = null;
    }
  }

  attemptReconnect(token) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('reconnectFailed');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect(token).catch(() => {
          // Reconnection failed, will try again
        });
      }
    }, delay);
  }

  handleMessage(data) {
    const { type } = data;
    
    switch (type) {
      case 'connection_established':
        this.emit('connectionEstablished', data);
        break;
      case 'notification':
        this.emit('notification', data.notification);
        break;
      case 'match_update':
        this.emit('matchUpdate', data.match_data);
        break;
      case 'system_message':
        this.emit('systemMessage', data);
        break;
      case 'pong':
        this.emit('pong', data);
        break;
      default:
        console.log('Unknown message type:', type, data);
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
      return true;
    }
    console.warn('WebSocket not connected, cannot send message');
    return false;
  }

  ping() {
    return this.send({ type: 'ping' });
  }

  markNotificationRead(notificationId) {
    return this.send({
      type: 'mark_notification_read',
      notification_id: notificationId
    });
  }

  updatePreferences(preferences) {
    return this.send({
      type: 'update_preferences',
      preferences
    });
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket event callback:', error);
        }
      });
    }
  }

  // Connection status
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }

  getReadyState() {
    return this.socket ? this.socket.readyState : WebSocket.CLOSED;
  }
}

// Singleton instance
const websocketService = new WebSocketService();

export default websocketService;
