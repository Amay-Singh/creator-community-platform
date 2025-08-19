import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';
import NotificationList from '../../components/ui/NotificationList';

const NotificationsPage: React.FC = () => {
  const { user, token } = useAuth();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [loading, setLoading] = useState(false);

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
        // Refresh the page to show updated notifications
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-[var(--font-size-2xl)] font-bold text-[var(--color-neutral-900)] mb-[var(--spacing-4)]">
              Access Denied
            </h1>
            <p className="text-[var(--color-neutral-600)]">
              Please log in to view your notifications.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-[var(--color-neutral-50)]">
        <div className="max-w-4xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-8)]">
          {/* Header */}
          <div className="mb-[var(--spacing-8)]">
            <div className="flex items-center justify-between mb-[var(--spacing-4)]">
              <h1 className="text-[var(--font-size-3xl)] font-bold text-[var(--color-neutral-900)]">
                Notifications
              </h1>
              
              <button
                onClick={handleMarkAllRead}
                disabled={loading}
                className="
                  flex items-center space-x-[var(--spacing-2)]
                  px-[var(--spacing-3)] py-[var(--spacing-2)]
                  bg-[var(--color-neutral-100)] text-[var(--color-neutral-900)]
                  border border-[var(--color-neutral-300)]
                  rounded-[var(--radius-sm)]
                  hover:bg-[var(--color-neutral-200)] hover:shadow-sm
                  focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all duration-[var(--duration-fast)]
                "
              >
                {loading ? (
                  <>
                    <div className="animate-spin w-4 h-4 border-2 border-[var(--color-primary-500)] border-t-transparent rounded-full"></div>
                    <span>Marking...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Mark all read</span>
                  </>
                )}
              </button>
            </div>

            {/* Filter Tabs */}
            <div className="flex space-x-[var(--spacing-1)] bg-[var(--color-neutral-100)] p-[var(--spacing-1)] rounded-[var(--radius-lg)]">
              <button
                onClick={() => setFilter('all')}
                className={`
                  px-[var(--spacing-4)] py-[var(--spacing-2)]
                  text-[var(--font-size-sm)] font-medium rounded-[var(--radius-base)]
                  transition-all duration-[var(--duration-fast)]
                  focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                  ${filter === 'all'
                    ? 'bg-white text-[var(--color-neutral-900)] shadow-sm'
                    : 'text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]'
                  }
                `}
                aria-pressed={filter === 'all'}
              >
                All
              </button>
              <button
                onClick={() => setFilter('unread')}
                className={`
                  px-[var(--spacing-4)] py-[var(--spacing-2)]
                  text-[var(--font-size-sm)] font-medium rounded-[var(--radius-base)]
                  transition-all duration-[var(--duration-fast)]
                  focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                  ${filter === 'unread'
                    ? 'bg-white text-[var(--color-neutral-900)] shadow-sm'
                    : 'text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]'
                  }
                `}
                aria-pressed={filter === 'unread'}
              >
                Unread
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="bg-white rounded-[var(--radius-lg)] shadow-sm border border-[var(--color-neutral-200)]">
            <NotificationList 
              isDropdown={false}
            />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default NotificationsPage;
