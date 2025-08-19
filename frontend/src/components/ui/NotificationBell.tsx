import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import NotificationList from './NotificationList';

interface NotificationBellProps {
  className?: string;
}

const NotificationBell: React.FC<NotificationBellProps> = ({ className = '' }) => {
  const { user, token } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch unread count
  useEffect(() => {
    if (!user || !token) return;

    const fetchUnreadCount = async () => {
      try {
        const response = await fetch('/api/notifications/unread-count/', {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setUnreadCount(data.unread_count || 0);
        }
      } catch (error) {
        console.error('Failed to fetch unread count:', error);
      }
    };

    fetchUnreadCount();
    
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [user, token]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setIsOpen(!isOpen);
    } else if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleMarkAllRead = async () => {
    if (!token) return;

    setLoading(true);
    try {
      const response = await fetch('/api/notifications/mark-read/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ all: true }),
      });

      if (response.ok) {
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className="
          relative p-[var(--spacing-2)] rounded-[var(--radius-base)]
          text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
          hover:bg-[var(--color-neutral-100)]
          focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
          focus-visible:ring-2 focus-visible:ring-[var(--color-primary-500)]
          transition-all duration-[var(--duration-fast)]
        "
        aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ''}`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* Bell Icon */}
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span
            className="
              absolute -top-1 -right-1 
              bg-[var(--color-error-500)] text-white
              text-[var(--font-size-xs)] font-medium
              rounded-full min-w-[20px] h-5
              flex items-center justify-center
              px-[var(--spacing-1)]
            "
            aria-label={`${unreadCount} unread notifications`}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className="
            absolute right-0 top-full mt-[var(--spacing-2)] z-50
            w-80 max-w-[90vw]
            bg-white border border-[var(--color-neutral-200)]
            rounded-[var(--radius-lg)] shadow-[var(--shadow-lg)]
          "
          role="menu"
          aria-label="Notifications menu"
        >
          {/* Header */}
          <div className="
            flex items-center justify-between
            p-[var(--spacing-4)] border-b border-[var(--color-neutral-200)]
          ">
            <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)]">
              Notifications
            </h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                disabled={loading}
                className="
                  text-[var(--font-size-sm)] text-[var(--color-primary-600)]
                  hover:text-[var(--color-primary-700)]
                  focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                  focus-visible:ring-2 focus-visible:ring-[var(--color-primary-500)]
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors duration-[var(--duration-fast)]
                "
                aria-label="Mark all notifications as read"
              >
                {loading ? 'Marking...' : 'Mark all read'}
              </button>
            )}
          </div>

          {/* Notification List */}
          <div className="max-h-96 overflow-y-auto">
            <NotificationList 
              isDropdown={true}
              onNotificationRead={() => {
                // Refresh unread count
                setUnreadCount(prev => Math.max(0, prev - 1));
              }}
            />
          </div>

          {/* Footer */}
          <div className="
            p-[var(--spacing-3)] border-t border-[var(--color-neutral-200)]
            text-center
          ">
            <a
              href="/notifications"
              className="
                text-[var(--font-size-sm)] text-[var(--color-primary-600)]
                hover:text-[var(--color-primary-700)]
                focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                focus-visible:ring-2 focus-visible:ring-[var(--color-primary-500)]
                transition-colors duration-[var(--duration-fast)]
              "
              onClick={() => setIsOpen(false)}
            >
              View all notifications
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
