import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useAuth } from '../contexts/AuthContext';
import SearchFilters from '../components/search/SearchFilters';
import SearchResults from '../components/search/SearchResults';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function Search() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [viewMode, setViewMode] = useState('grid');

  // Mock data for demonstration
  const mockResults = [
    {
      id: 1,
      name: 'Alex Chen',
      username: 'alexcreates',
      bio: 'Digital artist specializing in character design and concept art for games and animation.',
      avatar: null,
      location: 'San Francisco, CA',
      skills: ['Digital Art', 'Character Design', 'Concept Art'],
      categories: ['Digital Art', 'Gaming'],
      rating: 4.8,
      reviewCount: 127,
      isOnline: true
    },
    {
      id: 2,
      name: 'Maya Rodriguez',
      username: 'mayaart',
      bio: 'Illustrator and visual storyteller creating vibrant artwork for books and brands.',
      avatar: null,
      location: 'New York, NY',
      skills: ['Illustration', 'Visual Storytelling', 'Branding'],
      categories: ['Illustration', 'Design'],
      rating: 4.9,
      reviewCount: 89,
      isOnline: false
    },
    {
      id: 3,
      name: 'Sam Wilson',
      username: 'sambeats',
      bio: 'Music producer and composer specializing in electronic and cinematic soundscapes.',
      avatar: null,
      location: 'Los Angeles, CA',
      skills: ['Music Production', 'Composition', 'Sound Design'],
      categories: ['Music', 'Audio'],
      rating: 4.7,
      reviewCount: 156,
      isOnline: true
    }
  ];

  useEffect(() => {
    performSearch();
  }, [filters]);

  const performSearch = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      setResults(mockResults);
      setHasMore(false);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    performSearch();
  };

  const handleLoadMore = () => {
    // Implement pagination
    console.log('Load more results');
  };

  return (
    <>
      <Head>
        <title>Search Creators - Creator Community Platform</title>
        <meta name="description" content="Find and connect with talented creators in your field" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-[var(--color-neutral-50)]">
        {/* Header */}
        <header className="bg-white border-b border-[var(--color-neutral-200)] sticky top-0 z-[var(--z-sticky)]">
          <div className="max-w-7xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-4)]">
            <div className="flex items-center justify-between">
              <h1 className="text-[var(--font-size-2xl)] font-bold text-[var(--color-neutral-900)]">
                Discover Creators
              </h1>
              <Button
                variant="primary"
                onClick={() => window.history.back()}
              >
                Back to Dashboard
              </Button>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-[var(--spacing-4)] py-[var(--spacing-8)]">
          {/* Search Bar */}
          <div className="mb-[var(--spacing-8)]">
            <form onSubmit={handleSearch} className="flex gap-[var(--spacing-4)]">
              <div className="flex-1">
                <Input
                  placeholder="Search for creators, skills, or projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  size="lg"
                />
              </div>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={loading}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Search
              </Button>
            </form>
          </div>

          {/* Main Content */}
          <div className="flex flex-col lg:flex-row gap-[var(--spacing-8)]">
            {/* Filters Sidebar */}
            <aside className="lg:w-80 flex-shrink-0">
              <SearchFilters
                filters={filters}
                onFiltersChange={setFilters}
              />
            </aside>

            {/* Results */}
            <main className="flex-1">
              <SearchResults
                results={results}
                loading={loading}
                hasMore={hasMore}
                onLoadMore={handleLoadMore}
                viewMode={viewMode}
              />
            </main>
          </div>
        </div>
      </div>
    </>
  );
}
