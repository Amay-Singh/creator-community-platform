import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActivityFeedItem from '../../src/components/ui/ActivityFeedItem';

describe('ActivityFeedItem Component', () => {
  const mockActivity = {
    id: '1',
    actor: {
      id: '1',
      username: 'johndoe',
      email: 'john@example.com'
    },
    action_type: 'profile_updated',
    target_type: 'profile',
    metadata: {
      description: 'Updated bio and avatar'
    },
    created_at: '2024-01-01T12:00:00Z'
  };

  it('renders activity item with correct content', () => {
    render(<ActivityFeedItem activity={mockActivity} />);
    
    expect(screen.getByText('johndoe')).toBeInTheDocument();
    expect(screen.getByText(/updated their profile/i)).toBeInTheDocument();
  });

  it('displays correct icon for different activity types', () => {
    const profileActivity = { ...mockActivity, action_type: 'profile_updated' };
    const messageActivity = { ...mockActivity, action_type: 'message_sent' };
    const followActivity = { ...mockActivity, action_type: 'profile_followed' };

    const { rerender } = render(<ActivityFeedItem activity={profileActivity} />);
    expect(screen.getByTestId('profile-icon')).toBeInTheDocument();

    rerender(<ActivityFeedItem activity={messageActivity} />);
    expect(screen.getByTestId('message-icon')).toBeInTheDocument();

    rerender(<ActivityFeedItem activity={followActivity} />);
    expect(screen.getByTestId('follow-icon')).toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    const now = new Date('2024-01-01T12:30:00Z');
    jest.useFakeTimers();
    jest.setSystemTime(now);

    render(<ActivityFeedItem activity={mockActivity} />);
    
    expect(screen.getByText('30 minutes ago')).toBeInTheDocument();

    jest.useRealTimers();
  });

  it('handles activity without actor gracefully', () => {
    const systemActivity = {
      ...mockActivity,
      actor: null,
      action_type: 'system_announcement'
    };

    render(<ActivityFeedItem activity={systemActivity} />);
    
    expect(screen.getByText('System')).toBeInTheDocument();
  });

  it('displays metadata description when available', () => {
    render(<ActivityFeedItem activity={mockActivity} />);
    
    expect(screen.getByText('Updated bio and avatar')).toBeInTheDocument();
  });

  it('handles different action types with correct messages', () => {
    const activities = [
      { ...mockActivity, action_type: 'profile_created' },
      { ...mockActivity, action_type: 'message_sent' },
      { ...mockActivity, action_type: 'collaboration_joined' },
      { ...mockActivity, action_type: 'content_generated' }
    ];

    activities.forEach((activity, index) => {
      const { rerender } = render(<ActivityFeedItem activity={activity} />);
      
      switch (activity.action_type) {
        case 'profile_created':
          expect(screen.getByText(/created their profile/i)).toBeInTheDocument();
          break;
        case 'message_sent':
          expect(screen.getByText(/sent a message/i)).toBeInTheDocument();
          break;
        case 'collaboration_joined':
          expect(screen.getByText(/joined a collaboration/i)).toBeInTheDocument();
          break;
        case 'content_generated':
          expect(screen.getByText(/generated content/i)).toBeInTheDocument();
          break;
      }
      
      if (index < activities.length - 1) {
        rerender(<ActivityFeedItem activity={activities[index + 1]} />);
      }
    });
  });

  it('applies correct styling for different activity types', () => {
    render(<ActivityFeedItem activity={mockActivity} />);
    
    const container = screen.getByTestId('activity-item');
    expect(container).toHaveClass('activity-item');
  });

  it('handles missing metadata gracefully', () => {
    const activityWithoutMetadata = {
      ...mockActivity,
      metadata: {}
    };

    render(<ActivityFeedItem activity={activityWithoutMetadata} />);
    
    expect(screen.getByText('johndoe')).toBeInTheDocument();
    expect(screen.getByText(/updated their profile/i)).toBeInTheDocument();
  });
});
