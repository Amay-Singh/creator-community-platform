import React, { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  helperText?: string;
  label?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      error = false,
      helperText,
      label,
      leftIcon,
      rightIcon,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className="input-group">
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
          </label>
        )}
        
        <div className="input-wrapper">
          {leftIcon && (
            <div className="input-icon input-icon--left">
              {leftIcon}
            </div>
          )}
          
          <input
            type={type}
            className={cn(
              'input',
              error && 'input--error',
              leftIcon && 'input--with-left-icon',
              rightIcon && 'input--with-right-icon',
              className
            )}
            ref={ref}
            id={inputId}
            {...props}
          />
          
          {rightIcon && (
            <div className="input-icon input-icon--right">
              {rightIcon}
            </div>
          )}
        </div>
        
        {helperText && (
          <div className={cn(
            'input-helper',
            error && 'input-helper--error'
          )}>
            {helperText}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
