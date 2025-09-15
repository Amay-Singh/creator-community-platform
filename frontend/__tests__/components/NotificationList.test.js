import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NotificationList from '../../src/components/ui/NotificationList';

// Mock AuthContext
const mockAuthContext = {
  user: { id: '1', username: 'testuser' },
  token: 'mock-token',
  login: jest.fn(),
  logout: jest.fn(),
  loading: false
};

jest.mock('../../src/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }) => children
}));

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

describe('NotificationList Component', () => {
  const mockNotifications = [
    {
      id: '1',
      type: 'message_received',
      payload: { message: 'You have a new message from John' },
      read_at: null,
      created_at: '2024-01-01T12:00:00Z'
    },
    {
      id: '2',
      type: 'profile_viewed',
      payload: { message: 'Someone viewed your profile' },
      read_at: '2024-01-01T11:00:00Z',
      created_at: '2024-01-01T10:00:00Z'
    },
    {
      id: '3',
      type: 'profile_followed',
      payload: { message: 'You have a new follower' },
      read_at: null,
      created_at: '2024-01-01T09:00:00Z'
    }
  ];

  beforeEach(() => {
    fetch.mockClear();
    localStorageMock.getItem.mockReturnValue('mock-token');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<NotificationList />);
    
    expect(screen.getByText('Loading notifications...')).toBeInTheDocument();
  });

  it('renders notifications list when data is loaded', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: mockNotifications,
        next: null,
        previous: null
      })
    });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
      expect(screen.getByText('Someone viewed your profile')).toBeInTheDocument();
      expect(screen.getByText('You have a new follower')).toBeInTheDocument();
    });
  });

  it('displays unread notifications with different styling', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: mockNotifications,
        next: null,
        previous: null
      })
    });

    render(<NotificationList />);
    
    await waitFor(() => {
      const unreadNotifications = screen.getAllByText(/You have a new message from John|You have a new follower/);
      expect(unreadNotifications).toHaveLength(2);
    });
  });

  it('marks individual notification as read when clicked', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockNotifications,
          next: null,
          previous: null
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, marked_read: 1 })
      });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
    });

    const firstNotification = screen.getByText('You have a new message from John').closest('div');
    fireEvent.click(firstNotification);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/notifications/mark-read/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Token mock-token'
          }),
          body: JSON.stringify({ ids: ['1'] })
        })
      );
    });
  });

  it('handles pagination correctly', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockNotifications.slice(0, 2),
          next: '/api/notifications/?page=2',
          previous: null
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [mockNotifications[2]],
          next: null,
          previous: '/api/notifications/?page=1'
        })
      });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
      expect(screen.getByText('Someone viewed your profile')).toBeInTheDocument();
    });

    const loadMoreButton = screen.getByText('Load More');
    fireEvent.click(loadMoreButton);

    await waitFor(() => {
      expect(screen.getByText('You have a new follower')).toBeInTheDocument();
    });
  });

  it('filters notifications by status', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: mockNotifications.filter(n => !n.read_at),
        next: null,
        previous: null
      })
    });

    render(<NotificationList filter="unread" />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
      expect(screen.getByText('You have a new follower')).toBeInTheDocument();
      expect(screen.queryByText('Someone viewed your profile')).not.toBeInTheDocument();
    });
  });

  it('displays empty state when no notifications', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: [],
        next: null,
        previous: null
      })
    });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('No notifications yet')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load notifications')).toBeInTheDocument();
    });
  });

  it('displays relative timestamps correctly', async () => {
    const now = new Date('2024-01-01T12:30:00Z');
    jest.useFakeTimers();
    jest.setSystemTime(now);

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: mockNotifications,
        next: null,
        previous: null
      })
    });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('30 minutes ago')).toBeInTheDocument(); // First notification
      expect(screen.getByText('3 hours ago')).toBeInTheDocument(); // Third notification
    });

    jest.useRealTimers();
  });

  it('supports keyboard navigation', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: mockNotifications,
        next: null,
        previous: null
      })
    });

    render(<NotificationList />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
    });

    const firstNotification = screen.getByText('You have a new message from John').closest('div');
    
    // Test Enter key to mark as read
    fireEvent.keyDown(firstNotification, { key: 'Enter', code: 'Enter' });
    
    // Should trigger mark as read functionality
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/notifications/mark-read/',
        expect.objectContaining({
          method: 'POST'
        })
      );
    });
  });

  it('refreshes data when onRefresh prop is called', async () => {
    let refreshCallback;
    const onRefresh = jest.fn((callback) => {
      refreshCallback = callback;
    });

    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: mockNotifications,
        next: null,
        previous: null
      })
    });

    render(<NotificationList onRefresh={onRefresh} />);
    
    await waitFor(() => {
      expect(screen.getByText('You have a new message from John')).toBeInTheDocument();
    });

    // Simulate refresh
    if (refreshCallback) {
      refreshCallback();
    }

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });
});
