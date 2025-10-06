import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Input from './Input';
import Button from './Button';
import Card from './Card';

/**
 * Advanced Search Interface - ReqDoc02 Phase 3
 * Features: Collapsible filters, real-time search, modern design
 */
const SearchInterface = ({ onSearch, onFilterChange, initialFilters = {} }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState(initialFilters);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState(0);

  const filterCategories = [
    {
      id: 'category',
      label: 'Category',
      type: 'select',
      options: [
        { value: 'all', label: 'All Categories' },
        { value: 'design', label: 'Design & Visual Arts' },
        { value: 'music', label: 'Music & Audio' },
        { value: 'video', label: 'Video & Animation' },
        { value: 'writing', label: 'Writing & Content' },
        { value: 'tech', label: 'Technology & Development' },
        { value: 'marketing', label: 'Marketing & Business' }
      ]
    },
    {
      id: 'experience',
      label: 'Experience Level',
      type: 'select',
      options: [
        { value: 'all', label: 'All Levels' },
        { value: 'beginner', label: 'Beginner (0-2 years)' },
        { value: 'intermediate', label: 'Intermediate (2-5 years)' },
        { value: 'advanced', label: 'Advanced (5-10 years)' },
        { value: 'expert', label: 'Expert (10+ years)' }
      ]
    },
    {
      id: 'location',
      label: 'Location',
      type: 'input',
      placeholder: 'City, Country or Remote'
    },
    {
      id: 'availability',
      label: 'Availability',
      type: 'select',
      options: [
        { value: 'all', label: 'Any Availability' },
        { value: 'available', label: 'Available Now' },
        { value: 'part-time', label: 'Part-time Only' },
        { value: 'full-time', label: 'Full-time Only' },
        { value: 'project-based', label: 'Project-based' }
      ]
    }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch?.(searchQuery, filters);
  };

  const handleFilterChange = (filterId, value) => {
    const newFilters = { ...filters, [filterId]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
    
    // Count active filters
    const activeCount = Object.values(newFilters).filter(v => v && v !== 'all').length;
    setActiveFilters(activeCount);
  };

  const clearFilters = () => {
    const clearedFilters = {};
    filterCategories.forEach(cat => {
      clearedFilters[cat.id] = cat.type === 'select' ? 'all' : '';
    });
    setFilters(clearedFilters);
    setActiveFilters(0);
    onFilterChange?.(clearedFilters);
  };

  return (
    <div className="w-full">
      {/* Main Search Bar */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <Card variant="glass" className="p-6 mb-6">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search creators, skills, or projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={({ className }) => (
                  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                )}
                className="text-lg"
              />
            </div>
            <div className="flex gap-3">
              <Button
                type="button"
                variant="glass"
                onClick={() => setShowFilters(!showFilters)}
                className="relative"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Filters
                {activeFilters > 0 && (
                  <motion.span
                    className="absolute -top-2 -right-2 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500 }}
                  >
                    {activeFilters}
                  </motion.span>
                )}
              </Button>
              <Button type="submit" variant="primary">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Search
              </Button>
            </div>
          </form>
        </Card>
      </motion.div>

      {/* Advanced Filters */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden mb-6"
          >
            <Card variant="glass" className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Advanced Filters</h3>
                {activeFilters > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    Clear All ({activeFilters})
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filterCategories.map((category, index) => (
                  <motion.div
                    key={category.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                  >
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {category.label}
                    </label>
                    
                    {category.type === 'select' ? (
                      <select
                        value={filters[category.id] || 'all'}
                        onChange={(e) => handleFilterChange(category.id, e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl focus:outline-none focus:ring-4 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all duration-300"
                      >
                        {category.options.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <Input
                        type="text"
                        placeholder={category.placeholder}
                        value={filters[category.id] || ''}
                        onChange={(e) => handleFilterChange(category.id, e.target.value)}
                      />
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Quick Filter Tags */}
              <div className="mt-6 pt-6 border-t border-white/20">
                <p className="text-sm font-medium text-gray-700 mb-3">Quick Filters:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Available Now',
                    'Remote Only',
                    'Top Rated',
                    'New Creators',
                    'AI Specialists',
                    'Video Experts'
                  ].map((tag, index) => (
                    <motion.button
                      key={tag}
                      className="px-4 py-2 bg-white/20 hover:bg-white/30 text-gray-700 rounded-full text-sm font-medium transition-all duration-300 hover:scale-105"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      {tag}
                    </motion.button>
                  ))}
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active Filters Display */}
      {activeFilters > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex flex-wrap gap-2">
            {Object.entries(filters).map(([key, value]) => {
              if (!value || value === 'all') return null;
              const category = filterCategories.find(cat => cat.id === key);
              const displayValue = category?.type === 'select' 
                ? category.options.find(opt => opt.value === value)?.label 
                : value;
              
              return (
                <motion.div
                  key={key}
                  className="flex items-center space-x-2 px-3 py-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-blue-200/50 rounded-full text-sm"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  layout
                >
                  <span className="font-medium text-blue-700">
                    {category?.label}: {displayValue}
                  </span>
                  <button
                    onClick={() => handleFilterChange(key, category?.type === 'select' ? 'all' : '')}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SearchInterface;
