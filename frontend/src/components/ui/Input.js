import React from 'react';
import clsx from 'clsx';

const Input = React.forwardRef(({
  label,
  error,
  helperText,
  type = 'text',
  size = 'base',
  className,
  ...props
}, ref) => {
  const baseStyles = `
    w-full border transition-all duration-[var(--duration-fast)]
    focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-[var(--color-primary-500)]
    disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-neutral-100)]
    placeholder:text-[var(--color-neutral-400)]
  `;

  const variants = {
    default: `
      border-[var(--color-neutral-300)] bg-white text-[var(--color-neutral-900)]
      hover:border-[var(--color-neutral-400)]
    `,
    error: `
      border-[var(--color-error)] bg-white text-[var(--color-neutral-900)]
      focus:ring-[var(--color-error)] focus:border-[var(--color-error)]
    `
  };

  const sizes = {
    sm: 'px-[var(--spacing-3)] py-[var(--spacing-2)] text-[var(--font-size-sm)] rounded-[var(--radius-sm)]',
    base: 'px-[var(--spacing-4)] py-[var(--spacing-3)] text-[var(--font-size-base)] rounded-[var(--radius-base)]',
    lg: 'px-[var(--spacing-5)] py-[var(--spacing-4)] text-[var(--font-size-lg)] rounded-[var(--radius-md)]'
  };

  const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="w-full">
      {label && (
        <label 
          htmlFor={inputId}
          className="block text-[var(--font-size-sm)] font-medium text-[var(--color-neutral-700)] mb-[var(--spacing-2)]"
        >
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        type={type}
        className={clsx(
          baseStyles,
          error ? variants.error : variants.default,
          sizes[size],
          className
        )}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
        {...props}
      />
      {error && (
        <p 
          id={`${inputId}-error`}
          className="mt-[var(--spacing-2)] text-[var(--font-size-sm)] text-[var(--color-error)]"
          role="alert"
        >
          {error}
        </p>
      )}
      {helperText && !error && (
        <p 
          id={`${inputId}-helper`}
          className="mt-[var(--spacing-2)] text-[var(--font-size-sm)] text-[var(--color-neutral-500)]"
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
