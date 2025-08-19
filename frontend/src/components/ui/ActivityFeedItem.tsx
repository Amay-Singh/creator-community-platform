import React from 'react';

interface ActivityFeedItem {
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

interface ActivityFeedItemProps {
  activity: ActivityFeedItem;
}

const ActivityFeedItem: React.FC<ActivityFeedItemProps> = ({ activity }) => {
  const { actor, action_type, metadata, created_at } = activity;

  // Format actor name
  const actorName = actor.first_name && actor.last_name 
    ? `${actor.first_name} ${actor.last_name}`
    : actor.username;

  // Format activity message
  const formatActivityMessage = () => {
    switch (action_type) {
      case 'profile_updated':
        return `${actorName} updated their profile`;
      case 'message_sent':
        return `${actorName} sent a message`;
      case 'collaboration_created':
        return `${actorName} created a new collaboration`;
      case 'collaboration_joined':
        return `${actorName} joined a collaboration`;
      case 'profile_viewed':
        return `${actorName} viewed a profile`;
      case 'search_performed':
        return `${actorName} performed a search`;
      default:
        return `${actorName} performed an action`;
    }
  };

  // Get activity icon
  const getActivityIcon = () => {
    switch (action_type) {
      case 'profile_updated':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        );
      case 'message_sent':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case 'collaboration_created':
      case 'collaboration_joined':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        );
      case 'profile_viewed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        );
      case 'search_performed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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

  return (
    <div className="
      flex items-start space-x-[var(--spacing-4)]
      p-[var(--spacing-4)] border-b border-[var(--color-neutral-100)]
      hover:bg-[var(--color-neutral-50)]
      transition-colors duration-[var(--duration-fast)]
    ">
      {/* Actor Avatar */}
      <div className="flex-shrink-0">
        <div className="
          w-10 h-10 rounded-full bg-[var(--color-primary-100)]
          flex items-center justify-center
          text-[var(--color-primary-600)] font-medium
        ">
          {actorName.charAt(0).toUpperCase()}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-[var(--spacing-3)] mb-[var(--spacing-1)]">
          {/* Activity Icon */}
          <div className="
            flex-shrink-0 p-[var(--spacing-1)] rounded-full
            bg-[var(--color-neutral-100)] text-[var(--color-neutral-600)]
          ">
            {getActivityIcon()}
          </div>

          {/* Activity Message */}
          <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-900)]">
            {formatActivityMessage()}
          </p>
        </div>

        {/* Metadata */}
        {metadata && Object.keys(metadata).length > 0 && (
          <div className="ml-[var(--spacing-8)] mb-[var(--spacing-2)]">
            {metadata.message && (
              <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                "{metadata.message}"
              </p>
            )}
            {metadata.collaboration_title && (
              <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                Collaboration: {metadata.collaboration_title}
              </p>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-[var(--font-size-xs)] text-[var(--color-neutral-500)] ml-[var(--spacing-8)]">
          {formatRelativeTime(created_at)}
        </p>
      </div>
    </div>
  );
};

export default ActivityFeedItem;
