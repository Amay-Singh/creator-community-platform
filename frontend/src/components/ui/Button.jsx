import React from 'react';
import { motion } from 'framer-motion';

/**
 * Modern Button Component - ReqDoc02 Design System
 * Features: Glassmorphism, gradients, micro-interactions
 */
const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  loading = false,
  onClick,
  className = '',
  ...props 
}) => {
  const baseClasses = `
    relative inline-flex items-center justify-center font-semibold rounded-2xl
    transition-all duration-300 ease-out transform-gpu
    focus:outline-none focus:ring-4 focus:ring-opacity-50
    disabled:opacity-50 disabled:cursor-not-allowed
    overflow-hidden backdrop-blur-sm
  `;

  const variants = {
    primary: `
      bg-gradient-to-r from-blue-600 to-purple-600 text-white
      hover:from-blue-700 hover:to-purple-700 hover:scale-105
      focus:ring-blue-500 shadow-lg hover:shadow-xl
      border border-white/20
    `,
    secondary: `
      bg-white/10 backdrop-blur-md text-gray-900 border border-white/30
      hover:bg-white/20 hover:scale-105 hover:border-white/40
      focus:ring-gray-500 shadow-lg hover:shadow-xl
    `,
    ghost: `
      bg-transparent text-gray-700 hover:bg-white/10
      hover:scale-105 focus:ring-gray-400
      border border-transparent hover:border-white/20
    `,
    glass: `
      bg-white/5 backdrop-blur-xl border border-white/20
      text-white hover:bg-white/10 hover:scale-105
      focus:ring-white/50 shadow-2xl hover:shadow-3xl
    `
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
    xl: 'px-10 py-5 text-xl'
  };

  const buttonClasses = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;

  return (
    <motion.button
      className={buttonClasses}
      disabled={disabled || loading}
      onClick={onClick}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      {...props}
    >
      {/* Gradient overlay for extra depth */}
      <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/5 to-white/0 opacity-0 hover:opacity-100 transition-opacity duration-300" />
      
      {/* Loading spinner */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      {/* Button content */}
      <span className={`relative z-10 ${loading ? 'opacity-0' : 'opacity-100'}`}>
        {children}
      </span>
      
      {/* Shine effect */}
      <div className="absolute inset-0 -top-2 -left-2 w-4 h-full bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 opacity-0 hover:opacity-100 hover:animate-shine" />
    </motion.button>
  );
};

export default Button;
