import React from 'react';
import clsx from 'clsx';

const Card = ({ 
  children, 
  variant = 'default',
  padding = 'base',
  hover = false,
  className,
  ...props 
}) => {
  const baseStyles = `
    bg-white rounded-[var(--radius-lg)] border border-[var(--color-neutral-200)]
    transition-all duration-[var(--duration-fast)]
  `;

  const variants = {
    default: 'shadow-[var(--shadow-sm)]',
    elevated: 'shadow-[var(--shadow-md)]',
    interactive: `
      shadow-[var(--shadow-sm)] cursor-pointer
      hover:shadow-[var(--shadow-md)] hover:scale-[1.02] hover:-translate-y-1
    `
  };

  const paddingStyles = {
    none: '',
    sm: 'p-[var(--spacing-4)]',
    base: 'p-[var(--spacing-6)]',
    lg: 'p-[var(--spacing-8)]'
  };

  const hoverStyles = hover ? variants.interactive : variants[variant];

  return (
    <div
      className={clsx(
        baseStyles,
        hoverStyles,
        paddingStyles[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
