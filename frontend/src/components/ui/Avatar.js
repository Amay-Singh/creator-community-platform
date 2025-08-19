import React from 'react';
import clsx from 'clsx';

const Avatar = ({ 
  src, 
  alt, 
  size = 'base',
  fallback,
  className,
  ...props 
}) => {
  const sizes = {
    xs: 'h-6 w-6 text-[var(--font-size-xs)]',
    sm: 'h-8 w-8 text-[var(--font-size-sm)]',
    base: 'h-12 w-12 text-[var(--font-size-base)]',
    lg: 'h-16 w-16 text-[var(--font-size-lg)]',
    xl: 'h-20 w-20 text-[var(--font-size-xl)]',
    '2xl': 'h-24 w-24 text-[var(--font-size-2xl)]'
  };

  const baseStyles = `
    inline-flex items-center justify-center rounded-[var(--radius-full)] 
    bg-[var(--color-neutral-200)] text-[var(--color-neutral-600)] font-medium
    overflow-hidden
  `;

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div
      className={clsx(
        baseStyles,
        sizes[size],
        className
      )}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={alt || 'Avatar'}
          className="h-full w-full object-cover"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
      ) : null}
      <span 
        className={clsx(
          'flex items-center justify-center h-full w-full',
          src ? 'hidden' : 'flex'
        )}
      >
        {fallback || getInitials(alt)}
      </span>
    </div>
  );
};

export default Avatar;
