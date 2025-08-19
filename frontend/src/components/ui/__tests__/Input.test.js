import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Input from '../Input';

describe('Input Component', () => {
  test('renders with label', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  test('renders without label', () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  test('shows error message when error prop is provided', () => {
    render(<Input label="Email" error="Invalid email" />);
    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toHaveClass('border-[var(--color-error-500)]');
  });

  test('shows helper text when provided', () => {
    render(<Input label="Password" helperText="Must be at least 8 characters" />);
    expect(screen.getByText('Must be at least 8 characters')).toBeInTheDocument();
  });

  test('handles different input types', () => {
    const { rerender } = render(<Input type="email" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" />);
    expect(screen.getByLabelText('', { selector: 'input' })).toHaveAttribute('type', 'password');
  });

  test('handles different sizes', () => {
    const { rerender } = render(<Input size="sm" />);
    expect(screen.getByRole('textbox')).toHaveClass('px-[var(--spacing-3)]');

    rerender(<Input size="lg" />);
    expect(screen.getByRole('textbox')).toHaveClass('px-[var(--spacing-4)]');
  });

  test('handles value changes', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test value' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  test('forwards ref correctly', () => {
    const ref = React.createRef();
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  test('has proper accessibility attributes', () => {
    render(<Input label="Email" required />);
    const input = screen.getByLabelText('Email');
    expect(input).toHaveAttribute('required');
    expect(input).toHaveAttribute('aria-required', 'true');
  });

  test('associates error message with input via aria-describedby', () => {
    render(<Input label="Email" error="Invalid email" />);
    const input = screen.getByLabelText('Email');
    const errorElement = screen.getByText('Invalid email');
    
    expect(input).toHaveAttribute('aria-describedby');
    expect(errorElement).toHaveAttribute('id', input.getAttribute('aria-describedby'));
  });

  test('associates helper text with input via aria-describedby', () => {
    render(<Input label="Password" helperText="Must be 8+ characters" />);
    const input = screen.getByLabelText('Password');
    const helperElement = screen.getByText('Must be 8+ characters');
    
    expect(input).toHaveAttribute('aria-describedby');
    expect(helperElement).toHaveAttribute('id', input.getAttribute('aria-describedby'));
  });
});
