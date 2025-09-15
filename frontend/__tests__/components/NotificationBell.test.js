import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NotificationBell from '../../src/components/ui/NotificationBell';

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

describe('NotificationBell Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorageMock.getItem.mockReturnValue('mock-token');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders notification bell with zero count initially', () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ unread_count: 0 })
    });

    render(<NotificationBell />);
    
    expect(screen.getByRole('button', { name: /notifications/i })).toBeInTheDocument();
    expect(screen.queryByText('0')).not.toBeInTheDocument(); // Badge should be hidden for zero
  });

  it('displays unread count badge when there are unread notifications', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ unread_count: 3 })
    });

    render(<NotificationBell />);
    
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  it('opens dropdown when bell is clicked', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            {
              id: '1',
              type: 'message_received',
              payload: { message: 'Test notification' },
              read_at: null,
              created_at: '2024-01-01T00:00:00Z'
            }
          ],
          next: null,
          previous: null
        })
      });

    render(<NotificationBell />);
    
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText('Test notification')).toBeInTheDocument();
    });
  });

  it('marks all notifications as read when button is clicked', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            {
              id: '1',
              type: 'message_received',
              payload: { message: 'Test notification' },
              read_at: null,
              created_at: '2024-01-01T00:00:00Z'
            }
          ]
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, marked_read: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      });

    render(<NotificationBell />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    // Open dropdown
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText('Test notification')).toBeInTheDocument();
    });

    // Click mark all read
    const markAllReadButton = screen.getByText('Mark All Read');
    fireEvent.click(markAllReadButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/notifications/mark-read/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Token mock-token'
          }),
          body: JSON.stringify({ all: true })
        })
      );
    });
  });

  it('handles keyboard navigation', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            {
              id: '1',
              type: 'message_received',
              payload: { message: 'Test notification' },
              read_at: null,
              created_at: '2024-01-01T00:00:00Z'
            }
          ]
        })
      });

    render(<NotificationBell />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    
    // Test Enter key
    fireEvent.keyDown(bellButton, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(screen.getByText('Test notification')).toBeInTheDocument();
    });

    // Test Escape key to close
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
    
    await waitFor(() => {
      expect(screen.queryByText('Test notification')).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<NotificationBell />);
    
    // Should not crash and should show default state
    expect(screen.getByRole('button', { name: /notifications/i })).toBeInTheDocument();
  });

  it('polls for unread count updates', async () => {
    jest.useFakeTimers();
    
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ unread_count: 1 })
    });

    render(<NotificationBell />);
    
    // Initial call
    expect(fetch).toHaveBeenCalledTimes(1);
    
    // Fast-forward time to trigger polling
    jest.advanceTimersByTime(30000); // 30 seconds
    
    expect(fetch).toHaveBeenCalledTimes(2);
    
    jest.useRealTimers();
  });

  it('closes dropdown when clicking outside', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            {
              id: '1',
              type: 'message_received',
              payload: { message: 'Test notification' },
              read_at: null,
              created_at: '2024-01-01T00:00:00Z'
            }
          ]
        })
      });

    render(<NotificationBell />);
    
    // Open dropdown
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText('Test notification')).toBeInTheDocument();
    });

    // Click outside
    fireEvent.mouseDown(document.body);
    
    await waitFor(() => {
      expect(screen.queryByText('Test notification')).not.toBeInTheDocument();
    });
  });
});
