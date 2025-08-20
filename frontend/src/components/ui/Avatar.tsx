import React, { forwardRef, ImgHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src'> {
  src?: string;
  alt?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fallback?: string;
  className?: string;
}

const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ src, alt, size = 'md', fallback, className, ...props }, ref) => {
    const [imageError, setImageError] = React.useState(false);
    const [imageLoaded, setImageLoaded] = React.useState(false);

    const handleImageError = () => {
      setImageError(true);
    };

    const handleImageLoad = () => {
      setImageLoaded(true);
      setImageError(false);
    };

    const sizeClasses = {
      xs: 'avatar--xs',
      sm: 'avatar--sm', 
      md: 'avatar--md',
      lg: 'avatar--lg',
      xl: 'avatar--xl',
    };

    // Generate fallback initials from alt text or fallback prop
    const getInitials = (text?: string) => {
      if (!text) return '?';
      return text
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2);
    };

    const initials = getInitials(alt || fallback);

    return (
      <div
        ref={ref}
        className={cn(
          'avatar',
          sizeClasses[size],
          className
        )}
        role="img"
        aria-label={alt || `Avatar for ${fallback || 'user'}`}
      >
        {src && !imageError ? (
          <>
            <img
              src={src}
              alt={alt || ''}
              className="avatar__image"
              onError={handleImageError}
              onLoad={handleImageLoad}
              {...props}
            />
            {!imageLoaded && (
              <div className="avatar__fallback">
                {initials}
              </div>
            )}
          </>
        ) : (
          <div className="avatar__fallback">
            {initials}
          </div>
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

export { Avatar };
