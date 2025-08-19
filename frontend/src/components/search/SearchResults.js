import React, { useState } from 'react';
import clsx from 'clsx';
import ProfileCard from '../profile/ProfileCard';
import Button from '../ui/Button';

const SearchResults = ({ 
  results = [], 
  loading = false, 
  hasMore = false,
  onLoadMore,
  viewMode = 'grid',
  className 
}) => {
  const [sortBy, setSortBy] = useState('relevance');

  const sortOptions = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'rating', label: 'Highest Rated' },
    { value: 'recent', label: 'Recently Active' },
    { value: 'location', label: 'Nearest' }
  ];

  if (loading && results.length === 0) {
    return (
      <div className={clsx('w-full', className)}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[var(--spacing-6)]">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="animate-pulse bg-[var(--color-neutral-200)] rounded-[var(--radius-lg)] h-64"
            />
          ))}
        </div>
      </div>
    );
  }

  if (results.length === 0 && !loading) {
    return (
      <div className={clsx('w-full text-center py-[var(--spacing-12)]', className)}>
        <div className="max-w-md mx-auto">
          <svg className="w-16 h-16 mx-auto text-[var(--color-neutral-400)] mb-[var(--spacing-4)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)] mb-[var(--spacing-2)]">
            No creators found
          </h3>
          <p className="text-[var(--font-size-base)] text-[var(--color-neutral-600)] mb-[var(--spacing-6)]">
            Try adjusting your filters or search terms to find more creators.
          </p>
          <Button variant="primary" onClick={() => window.location.reload()}>
            Clear Filters
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('w-full', className)}>
      {/* Results Header */}
      <div className="flex items-center justify-between mb-[var(--spacing-6)]">
        <div className="flex items-center space-x-[var(--spacing-4)]">
          <p className="text-[var(--font-size-base)] text-[var(--color-neutral-700)]">
            Showing {results.length} creators
          </p>
          
          {/* View Mode Toggle */}
          <div className="flex rounded-[var(--radius-base)] border border-[var(--color-neutral-300)]">
            <button
              onClick={() => {/* Handle grid view */}}
              className={clsx(
                'p-[var(--spacing-2)] rounded-l-[var(--radius-base)] transition-colors duration-[var(--duration-fast)]',
                viewMode === 'grid' 
                  ? 'bg-[var(--color-primary-600)] text-white' 
                  : 'bg-white text-[var(--color-neutral-600)] hover:bg-[var(--color-neutral-50)]'
              )}
              aria-label="Grid view"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
            <button
              onClick={() => {/* Handle list view */}}
              className={clsx(
                'p-[var(--spacing-2)] rounded-r-[var(--radius-base)] transition-colors duration-[var(--duration-fast)]',
                viewMode === 'list' 
                  ? 'bg-[var(--color-primary-600)] text-white' 
                  : 'bg-white text-[var(--color-neutral-600)] hover:bg-[var(--color-neutral-50)]'
              )}
              aria-label="List view"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 12a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 16a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-[var(--spacing-3)] py-[var(--spacing-2)] border border-[var(--color-neutral-300)] rounded-[var(--radius-base)] text-[var(--font-size-sm)] focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-[var(--color-primary-500)]"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              Sort: {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Results Grid */}
      <div className={clsx(
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[var(--spacing-6)]'
          : 'space-y-[var(--spacing-4)]'
      )}>
        {results.map((profile) => (
          <ProfileCard
            key={profile.id}
            profile={profile}
            variant={viewMode === 'list' ? 'expanded' : 'default'}
          />
        ))}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="text-center mt-[var(--spacing-8)]">
          <Button
            variant="secondary"
            onClick={onLoadMore}
            loading={loading}
          >
            Load More Results
          </Button>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
