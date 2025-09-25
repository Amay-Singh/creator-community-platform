import React, { useState, useEffect, useRef } from 'react';
import { Bell, X, Check, CheckCheck, Settings } from 'lucide-react';
import websocketService from '../../services/websocketService';
import { notificationAPI } from '../../services/api';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Setup WebSocket listeners
    websocketService.on('connected', handleWebSocketConnected);
    websocketService.on('disconnected', handleWebSocketDisconnected);
    websocketService.on('notification', handleNewNotification);
    websocketService.on('connectionEstablished', handleConnectionEstablished);

    // Load initial notifications
    loadNotifications();
    loadUnreadCount();

    // Setup click outside listener
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      websocketService.off('connected', handleWebSocketConnected);
      websocketService.off('disconnected', handleWebSocketDisconnected);
      websocketService.off('notification', handleNewNotification);
      websocketService.off('connectionEstablished', handleConnectionEstablished);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleWebSocketConnected = () => {
    setConnected(true);
  };

  const handleWebSocketDisconnected = () => {
    setConnected(false);
  };

  const handleConnectionEstablished = (data) => {
    console.log('WebSocket connection established:', data);
  };

  const handleNewNotification = (notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 19)]);
    setUnreadCount(prev => prev + 1);
    
    // Show browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(notification.title || 'New Notification', {
        body: notification.message || 'You have a new notification',
        icon: '/favicon.ico',
        tag: notification.id
      });
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
      
      // Also send via WebSocket
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

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'match_found':
        return '🎯';
      case 'match_accepted':
        return '✅';
      case 'match_declined':
        return '❌';
      case 'collaboration_invite':
        return '🤝';
      case 'message_received':
        return '💬';
      default:
        return '🔔';
    }
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Notification Bell */}
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          requestNotificationPermission();
        }}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
      >
        <Bell size={24} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        {/* Connection status indicator */}
        <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full ${
          connected ? 'bg-green-500' : 'bg-gray-400'
        }`} />
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <CheckCheck size={16} className="mr-1" />
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Connection Status */}
          <div className={`px-4 py-2 text-sm ${
            connected 
              ? 'bg-green-50 text-green-700 border-b border-green-200' 
              : 'bg-yellow-50 text-yellow-700 border-b border-yellow-200'
          }`}>
            {connected ? '🟢 Real-time notifications active' : '🟡 Connecting...'}
          </div>

          {/* Notifications List */}
          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">
                Loading notifications...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications yet
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => !notification.is_read && markAsRead(notification.id)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className={`text-sm font-medium ${
                          !notification.is_read ? 'text-gray-900' : 'text-gray-600'
                        }`}>
                          {notification.payload?.title || notification.type.replace('_', ' ')}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">
                            {formatTime(notification.created_at)}
                          </span>
                          {!notification.is_read && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsRead(notification.id);
                              }}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Check size={14} />
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.payload?.message || 'New notification'}
                      </p>
                      {notification.payload?.compatibility_score && (
                        <div className="mt-2">
                          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            {Math.round(notification.payload.compatibility_score * 100)}% match
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            <button
              onClick={() => {
                setIsOpen(false);
                // Navigate to full notifications page
                window.location.href = '/notifications';
              }}
              className="text-sm text-blue-600 hover:text-blue-800 w-full text-center"
            >
              View all notifications
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
