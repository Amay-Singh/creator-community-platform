import React from 'react'

const Badge = ({ children, variant = 'default', size = 'default', className = '', ...props }) => {
  const baseClasses = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2'
  
  const variants = {
    default: 'border-transparent bg-gray-900 text-gray-50 hover:bg-gray-900/80',
    secondary: 'border-transparent bg-gray-100 text-gray-900 hover:bg-gray-100/80',
    destructive: 'border-transparent bg-red-500 text-gray-50 hover:bg-red-500/80',
    outline: 'text-gray-950'
  }
  
  const sizes = {
    default: 'px-2.5 py-0.5 text-xs',
    sm: 'px-2 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  }
  
  return (
    <div
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export default Badge
