/**
 * AI Content Generator Unit Tests - Guardian Agent Validated
 * Testing AI content generation functionality
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIContentGenerator from '../../src/components/AI/AIContentGenerator';
import { AuthProvider } from '../../src/contexts/AuthContext';

// Mock components
jest.mock('../../src/components/AI/GenerationHistory', () => {
  return function MockGenerationHistory() {
    return <div data-testid="generation-history">Generation History</div>;
  };
});

jest.mock('../../src/components/AI/PortfolioGenerator', () => {
  return function MockPortfolioGenerator() {
    return <div data-testid="portfolio-generator">Portfolio Generator</div>;
  };
});

const mockAuthContext = {
  user: { id: 1, email: 'test@example.com' },
  loading: false
};

global.fetch = jest.fn();

describe('AIContentGenerator Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders AI content generator tabs', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <AIContentGenerator />
      </AuthProvider>
    );

    expect(screen.getByText('🤖 Generate Content')).toBeInTheDocument();
    expect(screen.getByText('📁 Portfolio Generator')).toBeInTheDocument();
    expect(screen.getByText('📚 History')).toBeInTheDocument();
  });

  test('switches between tabs correctly', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <AIContentGenerator />
      </AuthProvider>
    );

    // Click on Portfolio Generator tab
    fireEvent.click(screen.getByText('📁 Portfolio Generator'));
    expect(screen.getByTestId('portfolio-generator')).toBeInTheDocument();

    // Click on History tab
    fireEvent.click(screen.getByText('📚 History'));
    expect(screen.getByTestId('generation-history')).toBeInTheDocument();
  });

  test('displays generation type options', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <AIContentGenerator />
      </AuthProvider>
    );

    expect(screen.getByDisplayValue('music')).toBeInTheDocument();
  });

  test('handles content generation request', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        success: true,
        content: 'Generated content',
        generation_id: 123
      })
    };
    fetch.mockResolvedValueOnce(mockResponse);

    render(
      <AuthProvider value={mockAuthContext}>
        <AIContentGenerator />
      </AuthProvider>
    );

    const promptInput = screen.getByPlaceholderText(/Describe the music/);
    const generateButton = screen.getByText('Generate Content');

    fireEvent.change(promptInput, { target: { value: 'Create a jazz song' } });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/ai_services/generate/', expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify({
          generation_type: 'music',
          prompt: 'Create a jazz song',
          parameters: {}
        })
      }));
    });
  });

  test('disables generate button when prompt is empty', () => {
    render(
      <AuthProvider value={mockAuthContext}>
        <AIContentGenerator />
      </AuthProvider>
    );

    const generateButton = screen.getByText('Generate Content');
    expect(generateButton).toBeDisabled();
  });
});
