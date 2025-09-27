import api from './api';

export const notificationAPI = {
  // Get notifications with pagination and filtering
  getNotifications: async (params = {}) => {
    const queryParams = new URLSearchParams({
      page: params.page || 1,
      status: params.status || 'all',
      page_size: params.pageSize || 20
    });
    
    const response = await api.get(`/notifications/?${queryParams}`);
    return response.data;
  },

  // Get unread notification count
  getUnreadCount: async () => {
    const response = await api.get('/notifications/unread-count/');
    return response.data;
  },

  // Mark notifications as read
  markAsRead: async (notificationIds) => {
    const response = await api.post('/notifications/mark-read/', {
      ids: notificationIds
    });
    return response.data;
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    const response = await api.post('/notifications/mark-read/', {
      all: true
    });
    return response.data;
  },

  // Get activity feed
  getActivityFeed: async (params = {}) => {
    const queryParams = new URLSearchParams({
      page: params.page || 1,
      page_size: params.pageSize || 20
    });
    
    const response = await api.get(`/notifications/feed/?${queryParams}`);
    return response.data;
  },

  // Match-specific notifications
  getMatchNotifications: async (params = {}) => {
    const queryParams = new URLSearchParams({
      page: params.page || 1,
      status: params.status || 'all',
      page_size: params.pageSize || 20
    });
    
    const response = await api.get(`/notifications/matches/?${queryParams}`);
    return response.data;
  },

  // Mark match notification as read
  markMatchNotificationRead: async (notificationId) => {
    const response = await api.post(`/notifications/matches/${notificationId}/read/`);
    return response.data;
  },

  // Get notification preferences
  getPreferences: async () => {
    const response = await api.get('/notifications/preferences/');
    return response.data;
  },

  // Update notification preferences
  updatePreferences: async (preferences) => {
    const response = await api.put('/notifications/preferences/', {
      preferences
    });
    return response.data;
  },

  // Send test notification (for development)
  sendTestNotification: async (data = {}) => {
    const response = await api.post('/notifications/test/', {
      type: data.type || 'system_announcement',
      title: data.title || 'Test Notification',
      message: data.message || 'This is a test notification'
    });
    return response.data;
  },

  // Get WebSocket connection status
  getWebSocketStatus: async () => {
    const response = await api.get('/notifications/websocket-status/');
    return response.data;
  },

  // Push notification endpoints
  getVapidPublicKey: async () => {
    const response = await api.get('/notifications/push/vapid-key/');
    return response.data;
  },

  subscribePush: async (subscription) => {
    const response = await api.post('/notifications/push/subscribe/', {
      subscription: subscription
    });
    return response.data;
  },

  unsubscribePush: async () => {
    const response = await api.post('/notifications/push/unsubscribe/');
    return response.data;
  },

  sendTestPushNotification: async () => {
    const response = await api.post('/notifications/push/test/');
    return response.data;
  }
};

export default notificationAPI;
