import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface Notification {
  id: string;
  type: string;
  payload: any;
  read_at: string | null;
  created_at: string;
}

interface NotificationListProps {
  isDropdown?: boolean;
  onNotificationRead?: () => void;
}

const NotificationList: React.FC<NotificationListProps> = ({ 
  isDropdown = false, 
  onNotificationRead 
}) => {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Fetch notifications
  const fetchNotifications = async (pageNum = 1, append = false) => {
    if (!user || !token) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/notifications/?page=${pageNum}`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const newNotifications = data.results || data;
        
        if (append) {
          setNotifications(prev => [...prev, ...newNotifications]);
        } else {
          setNotifications(newNotifications);
        }
        
        setHasMore(!!data.next);
        setError(null);
      } else {
        setError('Failed to fetch notifications');
      }
    } catch (err) {
      setError('Failed to fetch notifications');
      console.error('Notification fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [user, token]);

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    if (!token) return;

    try {
      const response = await fetch('/api/notifications/mark-read/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: [notificationId] }),
      });

      if (response.ok) {
        setNotifications(prev =>
          prev.map(notif =>
            notif.id === notificationId
              ? { ...notif, read_at: new Date().toISOString() }
              : notif
          )
        );
        onNotificationRead?.();
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Load more notifications
  const loadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchNotifications(nextPage, true);
    }
  };

  // Format notification message
  const formatNotificationMessage = (notification: Notification) => {
    const { type, payload } = notification;
    
    switch (type) {
      case 'message_received':
        return `New message from ${payload.sender_name || 'Unknown'}`;
      case 'collaboration_invite':
        return `Collaboration invite from ${payload.sender_name || 'Unknown'}`;
      case 'profile_view':
        return `${payload.viewer_name || 'Someone'} viewed your profile`;
      case 'system_update':
        return payload.message || 'System update';
      default:
        return payload.message || 'New notification';
    }
  };

  // Get notification icon
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'message_received':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case 'collaboration_invite':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        );
      case 'profile_view':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  // Format relative time
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading && notifications.length === 0) {
    return (
      <div className="p-[var(--spacing-4)] text-center">
        <div className="animate-spin w-6 h-6 border-2 border-[var(--color-primary-500)] border-t-transparent rounded-full mx-auto"></div>
        <p className="mt-[var(--spacing-2)] text-[var(--color-neutral-600)]">Loading notifications...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-[var(--spacing-4)] text-center">
        <p className="text-[var(--color-error-600)]">{error}</p>
        <button
          onClick={() => fetchNotifications()}
          className="
            mt-[var(--spacing-2)] text-[var(--color-primary-600)]
            hover:text-[var(--color-primary-700)]
            focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
          "
        >
          Try again
        </button>
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <div className="p-[var(--spacing-6)] text-center">
        <svg
          className="w-12 h-12 text-[var(--color-neutral-400)] mx-auto mb-[var(--spacing-3)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <p className="text-[var(--color-neutral-600)]">No notifications yet</p>
      </div>
    );
  }

  return (
    <div className={isDropdown ? '' : 'space-y-[var(--spacing-2)]'}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            ${isDropdown ? 'border-b border-[var(--color-neutral-100)] last:border-b-0' : 'border border-[var(--color-neutral-200)] rounded-[var(--radius-base)]'}
            p-[var(--spacing-4)]
            ${notification.read_at ? 'bg-white' : 'bg-[var(--color-primary-50)]'}
            hover:bg-[var(--color-neutral-50)]
            transition-colors duration-[var(--duration-fast)]
            cursor-pointer
          `}
          onClick={() => !notification.read_at && markAsRead(notification.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if ((e.key === 'Enter' || e.key === ' ') && !notification.read_at) {
              e.preventDefault();
              markAsRead(notification.id);
            }
          }}
          aria-label={`Notification: ${formatNotificationMessage(notification)}${notification.read_at ? ' (read)' : ' (unread)'}`}
        >
          <div className="flex items-start space-x-[var(--spacing-3)]">
            {/* Icon */}
            <div className={`
              flex-shrink-0 p-[var(--spacing-2)] rounded-full
              ${notification.read_at ? 'text-[var(--color-neutral-500)] bg-[var(--color-neutral-100)]' : 'text-[var(--color-primary-600)] bg-[var(--color-primary-100)]'}
            `}>
              {getNotificationIcon(notification.type)}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className={`
                text-[var(--font-size-sm)]
                ${notification.read_at ? 'text-[var(--color-neutral-700)]' : 'text-[var(--color-neutral-900)] font-medium'}
              `}>
                {formatNotificationMessage(notification)}
              </p>
              
              <p className="text-[var(--font-size-xs)] text-[var(--color-neutral-500)] mt-[var(--spacing-1)]">
                {formatRelativeTime(notification.created_at)}
              </p>
            </div>

            {/* Unread indicator */}
            {!notification.read_at && (
              <div className="flex-shrink-0">
                <div className="w-2 h-2 bg-[var(--color-primary-500)] rounded-full" aria-hidden="true"></div>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Load More Button (for non-dropdown view) */}
      {!isDropdown && hasMore && (
        <div className="text-center pt-[var(--spacing-4)]">
          <button
            onClick={loadMore}
            disabled={loading}
            className="
              px-[var(--spacing-4)] py-[var(--spacing-2)]
              text-[var(--color-primary-600)] hover:text-[var(--color-primary-700)]
              border border-[var(--color-primary-200)] hover:border-[var(--color-primary-300)]
              rounded-[var(--radius-base)]
              focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-[var(--duration-fast)]
            "
          >
            {loading ? 'Loading...' : 'Load more'}
          </button>
        </div>
      )}
    </div>
  );
};

export default NotificationList;
