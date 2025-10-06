import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Card from './Card';
import Button from './Button';

/**
 * Creator Card Component - ReqDoc02 Phase 3
 * Features: Grid/list view, hover effects, action buttons
 */
const CreatorCard = ({ 
  creator, 
  viewMode = 'grid', 
  onFollow, 
  onCollaborate, 
  onMessage,
  className = '' 
}) => {
  const [isFollowing, setIsFollowing] = useState(creator.isFollowing || false);
  const [showFullBio, setShowFullBio] = useState(false);

  const handleFollow = () => {
    setIsFollowing(!isFollowing);
    onFollow?.(creator.id, !isFollowing);
  };

  const skills = creator.skills || [];
  const displaySkills = skills.slice(0, 3);
  const remainingSkills = skills.length - 3;

  if (viewMode === 'list') {
    return (
      <motion.div
        className={`w-full ${className}`}
        whileHover={{ scale: 1.01 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        <Card variant="glass" hover={true} className="p-6">
          <div className="flex items-start space-x-6">
            {/* Avatar */}
            <motion.div 
              className="relative flex-shrink-0"
              whileHover={{ scale: 1.1 }}
            >
              <div className="w-20 h-20 rounded-2xl overflow-hidden bg-gradient-to-br from-blue-500 to-purple-500 p-0.5">
                <img
                  src={creator.avatar || '/default-avatar.png'}
                  alt={creator.name}
                  className="w-full h-full object-cover rounded-2xl"
                />
              </div>
              {creator.isOnline && (
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-2 border-white rounded-full"></div>
              )}
            </motion.div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{creator.name}</h3>
                  <p className="text-blue-600 font-medium">{creator.title}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                    <span className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {creator.location}
                    </span>
                    <span className="flex items-center">
                      <svg className="w-4 h-4 mr-1 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                      </svg>
                      {creator.rating} ({creator.reviewCount})
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" onClick={handleFollow}>
                    {isFollowing ? 'Following' : 'Follow'}
                  </Button>
                  <Button variant="primary" size="sm" onClick={() => onCollaborate?.(creator.id)}>
                    Collaborate
                  </Button>
                </div>
              </div>

              <p className="text-gray-600 mb-4 line-clamp-2">{creator.bio}</p>

              {/* Skills */}
              <div className="flex flex-wrap gap-2 mb-4">
                {displaySkills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-700 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
                {remainingSkills > 0 && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                    +{remainingSkills} more
                  </span>
                )}
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <span>{creator.projectCount} projects</span>
                <span>{creator.followerCount} followers</span>
                <span>Available {creator.availability}</span>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    );
  }

  // Grid view
  return (
    <motion.div
      className={`w-full ${className}`}
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Card variant="glass" hover={true} className="h-full overflow-hidden">
        {/* Cover Image */}
        <div className="relative h-32 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500">
          {creator.coverImage && (
            <img
              src={creator.coverImage}
              alt={`${creator.name}'s cover`}
              className="w-full h-full object-cover"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          
          {/* Online Status */}
          {creator.isOnline && (
            <div className="absolute top-4 right-4 flex items-center space-x-2 px-3 py-1 bg-green-500/90 backdrop-blur-sm rounded-full text-white text-sm font-medium">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span>Online</span>
            </div>
          )}
        </div>

        <div className="p-6">
          {/* Avatar */}
          <div className="flex items-start justify-between mb-4">
            <motion.div 
              className="relative -mt-12"
              whileHover={{ scale: 1.1 }}
            >
              <div className="w-16 h-16 rounded-2xl overflow-hidden bg-white p-0.5 shadow-lg">
                <img
                  src={creator.avatar || '/default-avatar.png'}
                  alt={creator.name}
                  className="w-full h-full object-cover rounded-2xl"
                />
              </div>
            </motion.div>
            
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">{creator.rating}</span>
            </div>
          </div>

          {/* Creator Info */}
          <div className="mb-4">
            <h3 className="text-lg font-bold text-gray-900 mb-1 truncate">{creator.name}</h3>
            <p className="text-blue-600 font-medium text-sm mb-2 truncate">{creator.title}</p>
            <p className="text-gray-500 text-sm flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {creator.location}
            </p>
          </div>

          {/* Bio */}
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">{creator.bio}</p>

          {/* Skills */}
          <div className="flex flex-wrap gap-2 mb-4">
            {displaySkills.map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-700 rounded-lg text-xs font-medium"
              >
                {skill}
              </span>
            ))}
            {remainingSkills > 0 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs">
                +{remainingSkills}
              </span>
            )}
          </div>

          {/* Stats */}
          <div className="flex justify-between text-xs text-gray-500 mb-4">
            <span>{creator.projectCount} projects</span>
            <span>{creator.followerCount} followers</span>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <Button
              variant={isFollowing ? "secondary" : "ghost"}
              size="sm"
              onClick={handleFollow}
              className="flex-1"
            >
              {isFollowing ? 'Following' : 'Follow'}
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => onCollaborate?.(creator.id)}
              className="flex-1"
            >
              Collaborate
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

// Creator Grid Component
const CreatorGrid = ({ creators, viewMode, onViewModeChange, ...cardProps }) => {
  return (
    <div className="w-full">
      {/* View Toggle */}
      <div className="flex items-center justify-between mb-6">
        <p className="text-gray-600">
          Showing {creators.length} creator{creators.length !== 1 ? 's' : ''}
        </p>
        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'grid' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => onViewModeChange?.('grid')}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </Button>
          <Button
            variant={viewMode === 'list' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => onViewModeChange?.('list')}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </Button>
        </div>
      </div>

      {/* Creator Cards */}
      <div className={
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
          : 'space-y-4'
      }>
        {creators.map((creator, index) => (
          <motion.div
            key={creator.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
          >
            <CreatorCard
              creator={creator}
              viewMode={viewMode}
              {...cardProps}
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
};

CreatorCard.Grid = CreatorGrid;

export default CreatorCard;
