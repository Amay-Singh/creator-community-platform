/**
 * Login Page Unit Tests - Guardian Agent Validated
 * Testing login page functionality and form validation
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter } from 'next/router';
import Login from '../../src/pages/auth/login';
import { AuthProvider } from '../../src/contexts/AuthContext';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

const mockPush = jest.fn();
const mockRouter = {
  push: mockPush,
  pathname: '/login'
};

const mockAuthContext = {
  login: jest.fn(),
  loading: false,
  user: null
};

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useRouter.mockReturnValue(mockRouter);
  });

  test('renders login form elements', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });

  test('validates email format', async () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    const emailInput = screen.getByLabelText('Email:');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    mockAuthContext.login.mockResolvedValueOnce({ success: true });

    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    const emailInput = screen.getByLabelText('Email:');
    const passwordInput = screen.getByLabelText('Password:');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockAuthContext.login).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  test('handles login error', async () => {
    mockAuthContext.login.mockResolvedValueOnce({ 
      success: false, 
      error: 'Invalid credentials' 
    });

    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    const emailInput = screen.getByLabelText('Email:');
    const passwordInput = screen.getByLabelText('Password:');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  test('navigates to register page', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <Login />
      </AuthProvider>
    );

    const registerLink = screen.getByText('Sign up here');
    fireEvent.click(registerLink);

    expect(mockPush).toHaveBeenCalledWith('/register');
  });
});
