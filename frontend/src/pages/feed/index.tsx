import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';
import ActivityFeedItem from '../../components/ui/ActivityFeedItem';

interface ActivityFeedData {
  id: string;
  action_type: string;
  actor: {
    id: string;
    username: string;
    first_name?: string;
    last_name?: string;
  };
  target_type?: string;
  target_id?: string;
  metadata: any;
  created_at: string;
}

const FeedPage: React.FC = () => {
  const { user, token } = useAuth();
  const [activities, setActivities] = useState<ActivityFeedData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Fetch activity feed
  const fetchActivities = async (pageNum = 1, append = false) => {
    if (!user || !token) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/feed/?page=${pageNum}`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const newActivities = data.results || data;
        
        if (append) {
          setActivities(prev => [...prev, ...newActivities]);
        } else {
          setActivities(newActivities);
        }
        
        setHasMore(!!data.next);
        setError(null);
      } else {
        setError('Failed to fetch activity feed');
      }
    } catch (err) {
      setError('Failed to fetch activity feed');
      console.error('Activity feed fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [user, token]);

  // Load more activities
  const loadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchActivities(nextPage, true);
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
              Please log in to view your activity feed.
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
            <h1 className="text-[var(--font-size-3xl)] font-bold text-[var(--color-neutral-900)] mb-[var(--spacing-2)]">
              Activity Feed
            </h1>
            <p className="text-[var(--color-neutral-600)]">
              Stay updated with your recent activities and interactions
            </p>
          </div>

          {/* Activity Feed */}
          <div className="bg-white rounded-[var(--radius-lg)] shadow-sm border border-[var(--color-neutral-200)]">
            {loading && activities.length === 0 ? (
              <div className="p-[var(--spacing-8)] text-center">
                <div className="animate-spin w-8 h-8 border-2 border-[var(--color-primary-500)] border-t-transparent rounded-full mx-auto mb-[var(--spacing-4)]"></div>
                <p className="text-[var(--color-neutral-600)]">Loading your activity feed...</p>
              </div>
            ) : error ? (
              <div className="p-[var(--spacing-8)] text-center">
                <svg
                  className="w-12 h-12 text-[var(--color-error-400)] mx-auto mb-[var(--spacing-4)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-[var(--color-error-600)] mb-[var(--spacing-4)]">{error}</p>
                <button
                  onClick={() => fetchActivities()}
                  className="
                    px-[var(--spacing-4)] py-[var(--spacing-2)]
                    text-[var(--color-primary-600)] hover:text-[var(--color-primary-700)]
                    border border-[var(--color-primary-200)] hover:border-[var(--color-primary-300)]
                    rounded-[var(--radius-base)]
                    focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                    transition-all duration-[var(--duration-fast)]
                  "
                >
                  Try again
                </button>
              </div>
            ) : activities.length === 0 ? (
              <div className="p-[var(--spacing-8)] text-center">
                <svg
                  className="w-12 h-12 text-[var(--color-neutral-400)] mx-auto mb-[var(--spacing-4)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 className="text-[var(--font-size-lg)] font-medium text-[var(--color-neutral-900)] mb-[var(--spacing-2)]">
                  No activity yet
                </h3>
                <p className="text-[var(--color-neutral-600)]">
                  Start exploring the platform to see your activity here
                </p>
              </div>
            ) : (
              <>
                {/* Activity Items */}
                <div className="divide-y divide-[var(--color-neutral-100)]">
                  {activities.map((activity) => (
                    <ActivityFeedItem key={activity.id} activity={activity} />
                  ))}
                </div>

                {/* Load More Button */}
                {hasMore && (
                  <div className="p-[var(--spacing-4)] text-center border-t border-[var(--color-neutral-100)]">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="
                        px-[var(--spacing-6)] py-[var(--spacing-3)]
                        text-[var(--color-primary-600)] hover:text-[var(--color-primary-700)]
                        border border-[var(--color-primary-200)] hover:border-[var(--color-primary-300)]
                        rounded-[var(--radius-base)]
                        focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)]
                        disabled:opacity-50 disabled:cursor-not-allowed
                        transition-all duration-[var(--duration-fast)]
                        flex items-center space-x-[var(--spacing-2)] mx-auto
                      "
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin w-4 h-4 border-2 border-[var(--color-primary-500)] border-t-transparent rounded-full"></div>
                          <span>Loading...</span>
                        </>
                      ) : (
                        'Load more activities'
                      )}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default FeedPage;
