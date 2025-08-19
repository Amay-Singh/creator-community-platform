import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchFilters from '../SearchFilters';

describe('SearchFilters Component', () => {
  const mockOnFiltersChange = jest.fn();
  const defaultProps = {
    filters: {},
    onFiltersChange: mockOnFiltersChange
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all filter sections', () => {
    render(<SearchFilters {...defaultProps} />);
    
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Category')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Experience Level')).toBeInTheDocument();
    expect(screen.getByText('Languages')).toBeInTheDocument();
    expect(screen.getByText('Availability')).toBeInTheDocument();
  });

  test('handles category filter changes', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const digitalArtCheckbox = screen.getByLabelText('Digital Art');
    fireEvent.click(digitalArtCheckbox);
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      categories: ['Digital Art']
    });
  });

  test('handles location input changes', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const locationInput = screen.getByPlaceholderText('Enter city or region');
    fireEvent.change(locationInput, { target: { value: 'San Francisco' } });
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      location: 'San Francisco'
    });
  });

  test('handles radius slider changes', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const radiusSlider = screen.getByLabelText('Search radius');
    fireEvent.change(radiusSlider, { target: { value: '100' } });
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      radius: 100
    });
  });

  test('handles experience level selection', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const intermediateRadio = screen.getByLabelText('Intermediate (2-5 years)');
    fireEvent.click(intermediateRadio);
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      experience: 'intermediate'
    });
  });

  test('handles language filter changes', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const spanishCheckbox = screen.getByLabelText('Spanish');
    fireEvent.click(spanishCheckbox);
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      languages: ['Spanish']
    });
  });

  test('handles availability toggle', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const availabilityToggle = screen.getByLabelText('Available for new projects');
    fireEvent.click(availabilityToggle);
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      availableNow: true
    });
  });

  test('clears all filters when clear button is clicked', () => {
    const filtersWithData = {
      categories: ['Digital Art'],
      location: 'San Francisco',
      experience: 'intermediate'
    };
    
    render(<SearchFilters filters={filtersWithData} onFiltersChange={mockOnFiltersChange} />);
    
    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({});
  });

  test('displays current filter values correctly', () => {
    const filtersWithData = {
      categories: ['Digital Art', 'Music'],
      location: 'New York',
      radius: 50,
      experience: 'expert',
      languages: ['English', 'French'],
      availableNow: true
    };
    
    render(<SearchFilters filters={filtersWithData} onFiltersChange={mockOnFiltersChange} />);
    
    expect(screen.getByLabelText('Digital Art')).toBeChecked();
    expect(screen.getByLabelText('Music')).toBeChecked();
    expect(screen.getByDisplayValue('New York')).toBeInTheDocument();
    expect(screen.getByDisplayValue('50')).toBeInTheDocument();
    expect(screen.getByLabelText('Expert (5+ years)')).toBeChecked();
    expect(screen.getByLabelText('English')).toBeChecked();
    expect(screen.getByLabelText('French')).toBeChecked();
    expect(screen.getByLabelText('Available for new projects')).toBeChecked();
  });

  test('has proper accessibility attributes', () => {
    render(<SearchFilters {...defaultProps} />);
    
    const form = screen.getByRole('form');
    expect(form).toHaveAttribute('aria-label', 'Search filters');
    
    const categoryFieldset = screen.getByRole('group', { name: 'Category' });
    expect(categoryFieldset).toBeInTheDocument();
    
    const experienceFieldset = screen.getByRole('group', { name: 'Experience Level' });
    expect(experienceFieldset).toBeInTheDocument();
  });
});
