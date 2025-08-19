import React, { useState } from 'react';
import clsx from 'clsx';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Card from '../ui/Card';

const SearchFilters = ({ filters, onFiltersChange, className }) => {
  const [localFilters, setLocalFilters] = useState({
    category: [],
    location: '',
    radius: 100,
    experience: '',
    languages: [],
    availability: '',
    ...filters
  });

  const categories = [
    'Digital Art', 'Music', 'Writing', 'Photography', 'Video', 
    'Design', 'Animation', 'Gaming', 'Fashion', 'Crafts'
  ];

  const experienceLevels = [
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'expert', label: 'Expert' }
  ];

  const languages = [
    'English', 'Spanish', 'French', 'German', 'Italian', 
    'Portuguese', 'Mandarin', 'Japanese', 'Korean'
  ];

  const handleCategoryToggle = (category) => {
    const newCategories = localFilters.category.includes(category)
      ? localFilters.category.filter(c => c !== category)
      : [...localFilters.category, category];
    
    const newFilters = { ...localFilters, category: newCategories };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleLanguageToggle = (language) => {
    const newLanguages = localFilters.languages.includes(language)
      ? localFilters.languages.filter(l => l !== language)
      : [...localFilters.languages, language];
    
    const newFilters = { ...localFilters, languages: newLanguages };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleInputChange = (field, value) => {
    const newFilters = { ...localFilters, [field]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters = {
      category: [],
      location: '',
      radius: 100,
      experience: '',
      languages: [],
      availability: ''
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  return (
    <Card padding="lg" className="w-full max-w-sm">
      <form aria-label="Search filters" onSubmit={(e) => e.preventDefault()}>
        <div className="space-y-[var(--spacing-6)]">
          <div className="flex items-center justify-between">
            <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)]">
              Filters
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllFilters}
              className="text-[var(--font-size-sm)]"
            >
              Clear All
            </Button>
          </div>
        </div>

        {/* Search Keywords */}
        <div>
          <Input
            label="Keywords"
            placeholder="Search skills, tools, etc."
            value={localFilters.keywords || ''}
            onChange={(e) => handleInputChange('keywords', e.target.value)}
          />
        </div>

        {/* Category */}
        <fieldset>
          <legend className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-3)]">
            Category
          </legend>
          <div className="space-y-[var(--spacing-2)]">
            {categories.map((category) => (
              <label key={category} className="flex items-center">
                <input
                  type="checkbox"
                  checked={localFilters.category.includes(category)}
                  onChange={() => handleCategoryToggle(category)}
                  className="h-4 w-4 text-[var(--color-primary-600)] focus:ring-[var(--color-primary-500)] border-[var(--color-neutral-300)] rounded-[var(--radius-sm)]"
                />
                <span className="ml-[var(--spacing-2)] text-[var(--font-size-sm)] text-[var(--color-neutral-700)]">
                  {category}
                </span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Location */}
        <div>
          <Input
            label="Location"
            placeholder="City, state, or country"
            value={localFilters.location}
            onChange={(e) => handleInputChange('location', e.target.value)}
          />
          
          <div className="mt-[var(--spacing-4)]">
            <label className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-2)]">
              Radius: {localFilters.radius} miles
            </label>
            <input
              type="range"
              min="25"
              max="500"
              step="25"
              value={localFilters.radius}
              onChange={(e) => handleInputChange('radius', parseInt(e.target.value))}
              className="w-full h-2 bg-[var(--color-neutral-200)] rounded-[var(--radius-full)] appearance-none cursor-pointer slider"
              aria-label="Search radius"
            />
            <div className="flex justify-between text-[var(--font-size-xs)] text-[var(--color-neutral-500)] mt-[var(--spacing-1)]">
              <span>25 mi</span>
              <span>Remote</span>
            </div>
          </div>
        </div>

        {/* Experience Level */}
        <fieldset>
          <legend className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-3)]">
            Experience Level
          </legend>
          <div className="space-y-[var(--spacing-2)]">
            {experienceLevels.map((level) => (
              <label key={level.value} className="flex items-center">
                <input
                  type="radio"
                  name="experience"
                  value={level.value}
                  checked={localFilters.experience === level.value}
                  onChange={(e) => handleInputChange('experience', e.target.value)}
                  className="h-4 w-4 text-[var(--color-primary-600)] focus:ring-[var(--color-primary-500)] border-[var(--color-neutral-300)]"
                />
                <span className="ml-[var(--spacing-2)] text-[var(--font-size-sm)] text-[var(--color-neutral-700)]">
                  {level.label}
                </span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Languages */}
        <div>
          <label className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-3)]">
            Languages
          </label>
          <div className="space-y-[var(--spacing-2)] max-h-32 overflow-y-auto">
            {languages.map((language) => (
              <label key={language} className="flex items-center">
                <input
                  type="checkbox"
                  checked={localFilters.languages.includes(language)}
                  onChange={() => handleLanguageToggle(language)}
                  className="h-4 w-4 text-[var(--color-primary-600)] focus:ring-[var(--color-primary-500)] border-[var(--color-neutral-300)] rounded-[var(--radius-sm)]"
                />
                <span className="ml-[var(--spacing-2)] text-[var(--font-size-sm)] text-[var(--color-neutral-700)]">
                  {language}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Availability */}
        <div>
          <label className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-3)]">
            Availability
          </label>
          <select
            value={localFilters.availability}
            onChange={(e) => handleInputChange('availability', e.target.value)}
            className="w-full px-[var(--spacing-3)] py-[var(--spacing-2)] border border-[var(--color-neutral-300)] rounded-[var(--radius-base)] text-[var(--font-size-sm)] focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-[var(--color-primary-500)]"
          >
            <option value="">Any</option>
            <option value="available">Available Now</option>
            <option value="part-time">Part-time</option>
            <option value="full-time">Full-time Projects</option>
            <option value="remote">Remote Only</option>
          </select>
        </div>
      </form>
    </Card>
  );
};

export default SearchFilters;
