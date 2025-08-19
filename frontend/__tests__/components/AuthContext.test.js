/**
 * AuthContext Unit Tests - Guardian Agent Validated
 * Comprehensive testing for authentication functionality
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuth } from '../../src/contexts/AuthContext';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock fetch
global.fetch = jest.fn();

// Test component to use AuthContext
const TestComponent = () => {
  const { user, login, register, logout, loading } = useAuth();
  
  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Ready'}</div>
      <div data-testid="user">{user ? user.email : 'No user'}</div>
      <button onClick={() => login('test@example.com', 'password')} data-testid="login-btn">
        Login
      </button>
      <button onClick={() => register('test@example.com', 'password', 'Test User')} data-testid="register-btn">
        Register
      </button>
      <button onClick={logout} data-testid="logout-btn">
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  test('provides initial state correctly', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
    expect(screen.getByTestId('loading')).toHaveTextContent('Ready');
  });

  test('handles successful login', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        token: 'mock-token',
        user: { id: 1, email: 'test@example.com', display_name: 'Test User' }
      })
    };
    fetch.mockResolvedValueOnce(mockResponse);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    fireEvent.click(screen.getByTestId('login-btn'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@example.com', password: 'password' })
      });
    });

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', 'mock-token');
  });

  test('handles login failure', async () => {
    const mockResponse = {
      ok: false,
      json: async () => ({ error: 'Invalid credentials' })
    };
    fetch.mockResolvedValueOnce(mockResponse);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    fireEvent.click(screen.getByTestId('login-btn'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });

    expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
  });

  test('handles successful registration', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        token: 'mock-token',
        user: { id: 1, email: 'test@example.com', display_name: 'Test User' }
      })
    };
    fetch.mockResolvedValueOnce(mockResponse);
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) }); // Mock profile fetch

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    fireEvent.click(screen.getByTestId('register-btn'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: 'test@example.com', 
          username: 'password', 
          password: 'Test User',
          password_confirm: undefined
        })
      });
    });

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', 'mock-token');
  });

  test('handles logout correctly', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    fireEvent.click(screen.getByTestId('logout-btn'));

    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
  });

  test('handles SSR safely', () => {
    // Mock window as undefined to simulate SSR
    const originalWindow = global.window;
    delete global.window;

    expect(() => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    }).not.toThrow();

    global.window = originalWindow;
  });
});
