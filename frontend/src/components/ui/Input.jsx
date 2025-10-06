import React, { useState, forwardRef } from 'react';
import { motion } from 'framer-motion';

/**
 * Modern Input Component - ReqDoc02 Design System
 * Features: Glassmorphism, floating labels, micro-interactions
 */
const Input = forwardRef(({ 
  label,
  type = 'text',
  placeholder,
  error,
  disabled = false,
  className = '',
  icon: Icon,
  ...props 
}, ref) => {
  const [focused, setFocused] = useState(false);
  const [hasValue, setHasValue] = useState(false);

  const handleChange = (e) => {
    setHasValue(e.target.value.length > 0);
    if (props.onChange) {
      props.onChange(e);
    }
  };

  const baseClasses = `
    w-full px-4 py-4 text-base bg-white/10 backdrop-blur-md
    border border-white/20 rounded-2xl transition-all duration-300
    focus:outline-none focus:ring-4 focus:ring-blue-500/30
    focus:border-blue-500/50 focus:bg-white/15
    disabled:opacity-50 disabled:cursor-not-allowed
    placeholder-gray-400 text-gray-900
  `;

  const errorClasses = error ? 'border-red-500/50 focus:border-red-500/70 focus:ring-red-500/30' : '';
  
  const inputClasses = `${baseClasses} ${errorClasses} ${className} ${Icon ? 'pl-12' : ''}`;

  return (
    <div className="relative">
      {/* Floating Label */}
      {label && (
        <motion.label
          className={`
            absolute left-4 pointer-events-none transition-all duration-300 z-10
            ${focused || hasValue 
              ? 'top-2 text-xs text-blue-600 font-medium' 
              : 'top-4 text-base text-gray-500'
            }
          `}
          animate={{
            y: focused || hasValue ? -8 : 0,
            scale: focused || hasValue ? 0.85 : 1,
          }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          {label}
        </motion.label>
      )}

      {/* Icon */}
      {Icon && (
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 z-10">
          <Icon className="w-5 h-5" />
        </div>
      )}

      {/* Input Field */}
      <motion.input
        ref={ref}
        type={type}
        className={inputClasses}
        placeholder={focused ? placeholder : ''}
        disabled={disabled}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onChange={handleChange}
        whileFocus={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
        {...props}
      />

      {/* Gradient Border Effect */}
      <div className={`
        absolute inset-0 rounded-2xl pointer-events-none transition-opacity duration-300
        bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-blue-500/20
        ${focused ? 'opacity-100' : 'opacity-0'}
      `} style={{ padding: '1px' }}>
        <div className="w-full h-full bg-white/5 rounded-2xl" />
      </div>

      {/* Error Message */}
      {error && (
        <motion.p
          className="mt-2 text-sm text-red-500 flex items-center"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </motion.p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
