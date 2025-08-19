/**
 * Dashboard Component Unit Tests - Guardian Agent Validated
 * Testing dashboard functionality and navigation
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../../src/components/Dashboard/Dashboard';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { SubscriptionProvider } from '../../src/contexts/SubscriptionContext';

// Mock components
jest.mock('../../src/components/Dashboard/ProfileOverview', () => {
  return function MockProfileOverview() {
    return <div data-testid="profile-overview">Profile Overview</div>;
  };
});

jest.mock('../../src/components/Collaboration/CollaborationHub', () => {
  return function MockCollaborationHub() {
    return <div data-testid="collaboration-hub">Collaboration Hub</div>;
  };
});

jest.mock('../../src/components/Chat/ChatInterface', () => {
  return function MockChatInterface() {
    return <div data-testid="chat-interface">Chat Interface</div>;
  };
});

jest.mock('../../src/components/AI/AIContentGenerator', () => {
  return function MockAIContentGenerator() {
    return <div data-testid="ai-content-generator">AI Content Generator</div>;
  };
});

// Mock contexts
const mockAuthContext = {
  user: { id: 1, email: 'test@example.com' },
  profile: { 
    display_name: 'Test User',
    category: 'music',
    experience_level: 'intermediate',
    bio: 'Test bio'
  },
  loading: false
};

const mockSubscriptionContext = {
  subscription: { plan: 'free' },
  usage: { ai_generations: 5 },
  loading: false
};

const MockProviders = ({ children }) => (
  <AuthProvider value={mockAuthContext}>
    <SubscriptionProvider value={mockSubscriptionContext}>
      {children}
    </SubscriptionProvider>
  </AuthProvider>
);

describe('Dashboard Component', () => {
  test('renders dashboard with user profile', () => {
    render(
      <MockProviders>
        <Dashboard />
      </MockProviders>
    );

    expect(screen.getByText('Welcome back, Test User!')).toBeInTheDocument();
    expect(screen.getByText('music • intermediate')).toBeInTheDocument();
  });

  test('displays navigation tabs', () => {
    render(
      <MockProviders>
        <Dashboard />
      </MockProviders>
    );

    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Collaborations')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('AI Tools')).toBeInTheDocument();
  });

  test('switches between tabs correctly', () => {
    render(
      <MockProviders>
        <Dashboard />
      </MockProviders>
    );

    // Default tab should show profile overview
    expect(screen.getByTestId('profile-overview')).toBeInTheDocument();

    // Click on Collaborations tab
    fireEvent.click(screen.getByText('Collaborations'));
    expect(screen.getByTestId('collaboration-hub')).toBeInTheDocument();

    // Click on Chat tab
    fireEvent.click(screen.getByText('Chat'));
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();

    // Click on AI Tools tab
    fireEvent.click(screen.getByText('AI Tools'));
    expect(screen.getByTestId('ai-content-generator')).toBeInTheDocument();
  });

  test('displays quick action buttons', () => {
    render(
      <MockProviders>
        <Dashboard />
      </MockProviders>
    );

    expect(screen.getByText('➕ New Portfolio Item')).toBeInTheDocument();
    expect(screen.getByText('🤝 Find Collaborators')).toBeInTheDocument();
    expect(screen.getByText('🤖 Generate Content')).toBeInTheDocument();
  });

  test('shows loading state when user/profile not loaded', () => {
    const loadingAuthContext = {
      user: null,
      profile: null,
      loading: true
    };

    render(
      <AuthProvider value={loadingAuthContext}>
        <SubscriptionProvider value={mockSubscriptionContext}>
          <Dashboard />
        </SubscriptionProvider>
      </AuthProvider>
    );

    expect(screen.getByText('Loading your creative space...')).toBeInTheDocument();
  });
});
