import React from 'react';
import { motion } from 'framer-motion';

/**
 * Modern Card Component - ReqDoc02 Design System
 * Features: Glassmorphism, hover effects, gradient borders
 */
const Card = ({ 
  children, 
  variant = 'default',
  hover = true,
  className = '',
  onClick,
  ...props 
}) => {
  const baseClasses = `
    relative backdrop-blur-xl rounded-3xl border transition-all duration-300
    overflow-hidden group
  `;

  const variants = {
    default: `
      bg-white/10 border-white/20 shadow-xl
      hover:bg-white/15 hover:border-white/30 hover:shadow-2xl
    `,
    glass: `
      bg-white/5 border-white/10 shadow-2xl
      hover:bg-white/10 hover:border-white/20 hover:shadow-3xl
    `,
    gradient: `
      bg-gradient-to-br from-white/10 to-white/5 border-white/20 shadow-xl
      hover:from-white/15 hover:to-white/10 hover:border-white/30 hover:shadow-2xl
    `,
    solid: `
      bg-white border-gray-200 shadow-lg
      hover:bg-gray-50 hover:border-gray-300 hover:shadow-xl
    `
  };

  const cardClasses = `${baseClasses} ${variants[variant]} ${className} ${onClick ? 'cursor-pointer' : ''}`;

  const cardVariants = {
    initial: { scale: 1, rotateX: 0, rotateY: 0 },
    hover: hover ? { 
      scale: 1.02, 
      rotateX: 2, 
      rotateY: 2,
      transition: { type: "spring", stiffness: 300, damping: 20 }
    } : {}
  };

  return (
    <motion.div
      className={cardClasses}
      variants={cardVariants}
      initial="initial"
      whileHover="hover"
      whileTap={onClick ? { scale: 0.98 } : {}}
      onClick={onClick}
      style={{ transformStyle: 'preserve-3d' }}
      {...props}
    >
      {/* Gradient Border Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
      
      {/* Inner Content Container */}
      <div className="relative z-10 p-6">
        {children}
      </div>

      {/* Shine Effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/30 to-transparent" />
        <div className="absolute top-0 left-0 h-full w-1 bg-gradient-to-b from-transparent via-white/30 to-transparent" />
      </div>

      {/* Floating Particles Effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white/40 rounded-full"
            style={{
              left: `${20 + i * 30}%`,
              top: `${30 + i * 20}%`,
            }}
            animate={{
              y: [-10, -20, -10],
              opacity: [0.4, 0.8, 0.4],
            }}
            transition={{
              duration: 2 + i * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </motion.div>
  );
};

// Card Header Component
const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>
    {children}
  </div>
);

// Card Title Component
const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-xl font-bold text-gray-900 mb-2 ${className}`}>
    {children}
  </h3>
);

// Card Content Component
const CardContent = ({ children, className = '' }) => (
  <div className={`text-gray-600 ${className}`}>
    {children}
  </div>
);

// Card Footer Component
const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-4 pt-4 border-t border-white/20 ${className}`}>
    {children}
  </div>
);

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;
