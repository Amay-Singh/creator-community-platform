import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Card from '../../../src/components/ui/Card';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>
  }
}));

describe('Card Component', () => {
  test('renders card with children', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  test('applies default variant styles', () => {
    render(<Card data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('bg-white/10', 'border-white/20');
  });

  test('applies glass variant styles', () => {
    render(<Card variant="glass" data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('bg-white/5', 'border-white/10');
  });

  test('applies gradient variant styles', () => {
    render(<Card variant="gradient" data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('bg-gradient-to-br', 'from-white/10', 'to-white/5');
  });

  test('handles click events when onClick is provided', () => {
    const handleClick = jest.fn();
    render(<Card onClick={handleClick}>Clickable Card</Card>);
    
    fireEvent.click(screen.getByText('Clickable Card'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies cursor-pointer when onClick is provided', () => {
    const handleClick = jest.fn();
    render(<Card onClick={handleClick} data-testid="card">Clickable</Card>);
    expect(screen.getByTestId('card')).toHaveClass('cursor-pointer');
  });

  test('renders Card.Header correctly', () => {
    render(
      <Card>
        <Card.Header>Header content</Card.Header>
      </Card>
    );
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  test('renders Card.Title correctly', () => {
    render(
      <Card>
        <Card.Title>Card Title</Card.Title>
      </Card>
    );
    const title = screen.getByText('Card Title');
    expect(title).toBeInTheDocument();
    expect(title).toHaveClass('text-xl', 'font-bold', 'text-gray-900');
  });

  test('renders Card.Content correctly', () => {
    render(
      <Card>
        <Card.Content>Card content</Card.Content>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  test('renders Card.Footer correctly', () => {
    render(
      <Card>
        <Card.Footer>Footer content</Card.Footer>
      </Card>
    );
    const footer = screen.getByText('Footer content');
    expect(footer).toBeInTheDocument();
    expect(footer).toHaveClass('border-t', 'border-white/20');
  });

  test('applies custom className', () => {
    render(<Card className="custom-class" data-testid="card">Content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('custom-class');
  });
});
