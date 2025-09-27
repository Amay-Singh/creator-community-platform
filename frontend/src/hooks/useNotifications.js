import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import websocketService from '../services/websocketService';
import { notificationAPI } from '../services/notificationAPI';
import { toast } from '../components/Notifications/ToastNotification';

export const useNotifications = () => {
  const { user, token } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [preferences, setPreferences] = useState({});

  useEffect(() => {
    if (user && token) {
      initializeNotifications();
    }

    return () => {
      websocketService.disconnect();
    };
  }, [user, token]);

  const initializeNotifications = async () => {
    try {
      // Load initial data
      await Promise.all([
        loadNotifications(),
        loadUnreadCount(),
        loadPreferences()
      ]);

      // Setup WebSocket connection
      await connectWebSocket();
      
    } catch (error) {
      console.error('Error initializing notifications:', error);
    }
  };

  const connectWebSocket = async () => {
    try {
      await websocketService.connect(token);
      
      // Setup event listeners
      websocketService.on('connected', handleWebSocketConnected);
      websocketService.on('disconnected', handleWebSocketDisconnected);
      websocketService.on('notification', handleNewNotification);
      websocketService.on('matchUpdate', handleMatchUpdate);
      websocketService.on('systemMessage', handleSystemMessage);
      
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const handleWebSocketConnected = () => {
    setConnected(true);
    console.log('Real-time notifications connected');
  };

  const handleWebSocketDisconnected = () => {
    setConnected(false);
    console.log('Real-time notifications disconnected');
  };

  const handleNewNotification = (notification) => {
    // Add to notifications list
    setNotifications(prev => [notification, ...prev.slice(0, 19)]);
    setUnreadCount(prev => prev + 1);

    // Show appropriate toast based on notification type
    switch (notification.type) {
      case 'match_found':
        toast.newMatch(notification.data || notification.payload);
        break;
      case 'match_accepted':
        toast.matchAccepted(notification.data || notification.payload);
        break;
      case 'collaboration_invite':
        toast.collaborationInvite(notification.data || notification.payload);
        break;
      default:
        toast.info(
          notification.message || 'You have a new notification',
          notification.title || 'Notification'
        );
    }

    // Play notification sound if enabled
    if (preferences.sound_enabled) {
      playNotificationSound();
    }
  };

  const handleMatchUpdate = (matchData) => {
    console.log('Match update received:', matchData);
    
    // Handle different types of match updates
    switch (matchData.update_type) {
      case 'status_change':
        if (matchData.new_status === 'accepted') {
          toast.success(
            `Your match with ${matchData.matched_creator_name} was accepted!`,
            'Match Accepted'
          );
        }
        break;
      case 'new_feedback':
        toast.info(
          `You received feedback on your match (Rating: ${matchData.rating}/5)`,
          'New Feedback'
        );
        break;
    }
  };

  const handleSystemMessage = (data) => {
    switch (data.level) {
      case 'success':
        toast.success(data.message, 'System');
        break;
      case 'error':
        toast.error(data.message, 'System');
        break;
      case 'warning':
        toast.warning(data.message, 'System');
        break;
      default:
        toast.info(data.message, 'System');
    }
  };

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationAPI.getNotifications();
      setNotifications(response.results || response);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await notificationAPI.getUnreadCount();
      setUnreadCount(response.unread_count || 0);
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const loadPreferences = async () => {
    try {
      const response = await notificationAPI.getPreferences();
      setPreferences(response.preferences || {});
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationAPI.markAsRead([notificationId]);
      
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId
            ? { ...notif, is_read: true, read_at: new Date().toISOString() }
            : notif
        )
      );
      
      setUnreadCount(prev => Math.max(0, prev - 1));
      
      // Send via WebSocket
      websocketService.markNotificationRead(notificationId);
      
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead();
      
      setNotifications(prev =>
        prev.map(notif => ({
          ...notif,
          is_read: true,
          read_at: new Date().toISOString()
        }))
      );
      
      setUnreadCount(0);
      
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const updatePreferences = async (newPreferences) => {
    try {
      await notificationAPI.updatePreferences(newPreferences);
      setPreferences(prev => ({ ...prev, ...newPreferences }));
      
      // Send via WebSocket
      websocketService.updatePreferences(newPreferences);
      
      toast.success('Notification preferences updated', 'Settings');
      
    } catch (error) {
      console.error('Error updating preferences:', error);
      toast.error('Failed to update preferences', 'Settings');
    }
  };

  const playNotificationSound = () => {
    try {
      // Create a simple notification sound
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
      
    } catch (error) {
      console.error('Error playing notification sound:', error);
    }
  };

  const sendTestNotification = async () => {
    try {
      await notificationAPI.sendTestNotification({
        title: 'Test Notification',
        message: 'This is a test notification to verify the system is working'
      });
      
      toast.success('Test notification sent!', 'Testing');
      
    } catch (error) {
      console.error('Error sending test notification:', error);
      toast.error('Failed to send test notification', 'Testing');
    }
  };

  return {
    // State
    notifications,
    unreadCount,
    connected,
    loading,
    preferences,
    
    // Actions
    markAsRead,
    markAllAsRead,
    updatePreferences,
    loadNotifications,
    sendTestNotification,
    
    // WebSocket actions
    reconnect: () => connectWebSocket(),
    disconnect: () => websocketService.disconnect()
  };
};

export default useNotifications;
