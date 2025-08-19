import React from 'react';
import clsx from 'clsx';

const Button = React.forwardRef(({
  children,
  variant = 'primary',
  size = 'base',
  disabled = false,
  loading = false,
  className,
  ...props
}, ref) => {
  const baseStyles = `
    inline-flex items-center justify-center font-medium transition-all duration-[var(--duration-fast)]
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary-500)] focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const variants = {
    primary: `
      bg-[var(--color-primary-600)] text-white
      hover:bg-[var(--color-primary-700)] hover:shadow-md hover:scale-[1.02]
      active:bg-[var(--color-primary-800)] active:scale-[0.98]
    `,
    secondary: `
      bg-[var(--color-neutral-100)] text-[var(--color-neutral-900)] border border-[var(--color-neutral-300)]
      hover:bg-[var(--color-neutral-200)] hover:shadow-sm hover:scale-[1.02]
      active:bg-[var(--color-neutral-300)] active:scale-[0.98]
    `,
    ghost: `
      bg-transparent text-[var(--color-primary-600)]
      hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-700)]
      active:bg-[var(--color-primary-100)]
    `,
    gradient: `
      bg-gradient-to-r from-[var(--color-primary-600)] to-[var(--color-secondary-600)] text-white
      hover:shadow-lg hover:scale-[1.02]
      active:scale-[0.98]
    `
  };

  const sizes = {
    sm: 'px-[var(--spacing-3)] py-[var(--spacing-2)] text-[var(--font-size-sm)] rounded-[var(--radius-sm)]',
    base: 'px-[var(--spacing-4)] py-[var(--spacing-3)] text-[var(--font-size-base)] rounded-[var(--radius-base)]',
    lg: 'px-[var(--spacing-6)] py-[var(--spacing-4)] text-[var(--font-size-lg)] rounded-[var(--radius-md)]'
  };

  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {loading && (
        <svg 
          className="animate-spin -ml-1 mr-2 h-4 w-4" 
          fill="none" 
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle 
            className="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            strokeWidth="4"
          />
          <path 
            className="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
