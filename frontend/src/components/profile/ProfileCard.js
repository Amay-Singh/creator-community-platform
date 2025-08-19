import React from 'react';
import clsx from 'clsx';
import Avatar from '../ui/Avatar';
import Button from '../ui/Button';
import Card from '../ui/Card';

const ProfileCard = ({ 
  profile, 
  variant = 'default',
  showActions = true,
  className 
}) => {
  const { 
    id,
    name, 
    username, 
    bio, 
    avatar, 
    location, 
    skills = [], 
    rating, 
    reviewCount,
    isOnline,
    categories = []
  } = profile;

  const variants = {
    default: 'max-w-sm',
    compact: 'max-w-xs',
    expanded: 'max-w-md'
  };

  return (
    <Card 
      hover={true}
      className={clsx(variants[variant], className)}
    >
      <div className="flex items-start space-x-[var(--spacing-4)]">
        <div className="relative">
          <Avatar 
            src={avatar} 
            alt={name}
            size="lg"
          />
          {isOnline && (
            <div className="absolute -bottom-1 -right-1 h-4 w-4 bg-[var(--color-accent-500)] border-2 border-white rounded-[var(--radius-full)]" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-[var(--spacing-2)] mb-[var(--spacing-1)]">
            <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)] truncate">
              {name}
            </h3>
            {rating && (
              <div className="flex items-center text-[var(--font-size-sm)] text-[var(--color-neutral-600)]">
                <svg className="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {rating} ({reviewCount})
              </div>
            )}
          </div>
          
          <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-600)] mb-[var(--spacing-1)]">
            @{username}
          </p>
          
          {location && (
            <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-500)] mb-[var(--spacing-3)] flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {location}
            </p>
          )}
        </div>
      </div>

      {bio && (
        <p className="mt-[var(--spacing-4)] text-[var(--font-size-sm)] text-[var(--color-neutral-700)] line-clamp-3">
          {bio}
        </p>
      )}

      {(skills.length > 0 || categories.length > 0) && (
        <div className="mt-[var(--spacing-4)]">
          <div className="flex flex-wrap gap-[var(--spacing-2)]">
            {categories.slice(0, 2).map((category, index) => (
              <span
                key={index}
                className="inline-flex items-center px-[var(--spacing-2)] py-[var(--spacing-1)] rounded-[var(--radius-sm)] text-[var(--font-size-xs)] font-medium bg-[var(--color-primary-100)] text-[var(--color-primary-700)]"
              >
                {category}
              </span>
            ))}
            {skills.slice(0, 3).map((skill, index) => (
              <span
                key={index}
                className="inline-flex items-center px-[var(--spacing-2)] py-[var(--spacing-1)] rounded-[var(--radius-sm)] text-[var(--font-size-xs)] font-medium bg-[var(--color-neutral-100)] text-[var(--color-neutral-700)]"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {showActions && (
        <div className="mt-[var(--spacing-6)] flex space-x-[var(--spacing-3)]">
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={() => {/* Handle invite */}}
          >
            Invite
          </Button>
          <Button
            variant="secondary"
            size="sm"
            className="flex-1"
            onClick={() => {/* Handle message */}}
          >
            Message
          </Button>
        </div>
      )}
    </Card>
  );
};

export default ProfileCard;
