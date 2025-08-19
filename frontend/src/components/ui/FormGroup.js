import React from 'react';
import clsx from 'clsx';

const FormGroup = ({ 
  children, 
  className,
  spacing = 'base'
}) => {
  const spacingStyles = {
    sm: 'space-y-[var(--spacing-3)]',
    base: 'space-y-[var(--spacing-4)]',
    lg: 'space-y-[var(--spacing-6)]'
  };

  return (
    <div className={clsx(spacingStyles[spacing], className)}>
      {children}
    </div>
  );
};

export default FormGroup;
