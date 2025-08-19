import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import clsx from 'clsx';

const Modal = ({ 
  isOpen, 
  onClose, 
  children, 
  title,
  size = 'base',
  className 
}) => {
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);

  const sizes = {
    sm: 'max-w-md',
    base: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      modalRef.current?.focus();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
      previousFocusRef.current?.focus();
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const modalContent = (
    <div 
      className="fixed inset-0 z-[var(--z-modal)] overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity duration-[var(--duration-base)]"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Modal container */}
      <div className="flex min-h-full items-center justify-center p-[var(--spacing-4)]">
        <div
          ref={modalRef}
          tabIndex={-1}
          className={clsx(
            'relative w-full transform overflow-hidden rounded-[var(--radius-lg)] bg-white shadow-[var(--shadow-xl)] transition-all duration-[var(--duration-base)]',
            sizes[size],
            className
          )}
        >
          {/* Header */}
          {title && (
            <div className="flex items-center justify-between p-[var(--spacing-6)] border-b border-[var(--color-neutral-200)]">
              <h2 
                id="modal-title"
                className="text-[var(--font-size-xl)] font-semibold text-[var(--color-neutral-900)]"
              >
                {title}
              </h2>
              <button
                onClick={onClose}
                className="rounded-[var(--radius-sm)] p-[var(--spacing-2)] text-[var(--color-neutral-400)] hover:text-[var(--color-neutral-600)] hover:bg-[var(--color-neutral-100)] transition-colors duration-[var(--duration-fast)]"
                aria-label="Close modal"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
          
          {/* Content */}
          <div className="p-[var(--spacing-6)]">
            {children}
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default Modal;
