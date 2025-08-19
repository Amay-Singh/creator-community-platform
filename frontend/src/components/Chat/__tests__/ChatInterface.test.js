import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatInterface from '../ChatInterface';

describe('ChatInterface Component', () => {
  const mockRecipientUser = {
    id: 2,
    name: 'Alex Chen',
    username: 'alexcreates',
    avatar: null,
    isOnline: true
  };

  const defaultProps = {
    threadId: 'thread-123',
    recipientUser: mockRecipientUser
  };

  test('renders chat header with recipient info', () => {
    render(<ChatInterface {...defaultProps} />);
    
    expect(screen.getByText('Alex Chen')).toBeInTheDocument();
    expect(screen.getByText('Online')).toBeInTheDocument();
  });

  test('renders offline status correctly', () => {
    const offlineUser = { ...mockRecipientUser, isOnline: false };
    render(<ChatInterface {...defaultProps} recipientUser={offlineUser} />);
    
    expect(screen.getByText('Last seen 2m ago')).toBeInTheDocument();
  });

  test('displays existing messages', () => {
    render(<ChatInterface {...defaultProps} />);
    
    expect(screen.getByText(/Hey! I love your latest character design/)).toBeInTheDocument();
    expect(screen.getByText(/Thanks! I'd love to hear more about it/)).toBeInTheDocument();
    expect(screen.getByText(/It's an indie RPG about time travel/)).toBeInTheDocument();
  });

  test('sends new message when form is submitted', async () => {
    render(<ChatInterface {...defaultProps} />);
    
    const messageInput = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(messageInput, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    expect(screen.getByText('Test message')).toBeInTheDocument();
    expect(messageInput.value).toBe('');
  });

  test('sends message on Enter key press', async () => {
    render(<ChatInterface {...defaultProps} />);
    
    const messageInput = screen.getByPlaceholderText('Type a message...');
    
    fireEvent.change(messageInput, { target: { value: 'Enter key message' } });
    fireEvent.keyDown(messageInput, { key: 'Enter', shiftKey: false });
    
    expect(screen.getByText('Enter key message')).toBeInTheDocument();
  });

  test('does not send message on Shift+Enter', () => {
    render(<ChatInterface {...defaultProps} />);
    
    const messageInput = screen.getByPlaceholderText('Type a message...');
    
    fireEvent.change(messageInput, { target: { value: 'Shift enter message' } });
    fireEvent.keyDown(messageInput, { key: 'Enter', shiftKey: true });
    
    expect(screen.queryByText('Shift enter message')).not.toBeInTheDocument();
    expect(messageInput.value).toBe('Shift enter message');
  });

  test('disables send button when message is empty', () => {
    render(<ChatInterface {...defaultProps} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();
  });

  test('enables send button when message has content', () => {
    render(<ChatInterface {...defaultProps} />);
    
    const messageInput = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(messageInput, { target: { value: 'Test' } });
    expect(sendButton).not.toBeDisabled();
  });

  test('has proper accessibility attributes', () => {
    render(<ChatInterface {...defaultProps} />);
    
    expect(screen.getByRole('button', { name: 'Voice call' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Video call' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Attach file' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add emoji' })).toBeInTheDocument();
  });

  test('shows message status indicators', () => {
    render(<ChatInterface {...defaultProps} />);
    
    // Check for delivery status indicators in existing messages
    const messageElements = screen.getAllByText(/✓/);
    expect(messageElements.length).toBeGreaterThan(0);
  });

  test('formats timestamps correctly', () => {
    render(<ChatInterface {...defaultProps} />);
    
    // Should show time in 12-hour format
    const timeElements = screen.getAllByText(/\d{1,2}:\d{2}\s?(AM|PM)/i);
    expect(timeElements.length).toBeGreaterThan(0);
  });
});
