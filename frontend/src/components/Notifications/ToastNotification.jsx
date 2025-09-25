import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const ToastNotification = ({ 
  id,
  type = 'info', 
  title, 
  message, 
  duration = 5000,
  onClose,
  action
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose?.(id);
    }, 300);
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getBackgroundColor = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  if (!isVisible) return null;

  return (
    <div
      className={`
        fixed top-4 right-4 z-50 max-w-sm w-full
        transform transition-all duration-300 ease-in-out
        ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
      `}
    >
      <div className={`
        rounded-lg border p-4 shadow-lg backdrop-blur-sm
        ${getBackgroundColor()}
      `}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          
          <div className="ml-3 flex-1">
            {title && (
              <h4 className="text-sm font-medium text-gray-900 mb-1">
                {title}
              </h4>
            )}
            <p className="text-sm text-gray-700">
              {message}
            </p>
            
            {action && (
              <div className="mt-3">
                <button
                  onClick={action.onClick}
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                >
                  {action.label}
                </button>
              </div>
            )}
          </div>
          
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleClose}
              className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Toast Container Component
const ToastContainer = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    // Listen for custom toast events
    const handleToastEvent = (event) => {
      addToast(event.detail);
    };

    window.addEventListener('showToast', handleToastEvent);
    return () => window.removeEventListener('showToast', handleToastEvent);
  }, []);

  const addToast = (toastData) => {
    const id = Date.now() + Math.random();
    const newToast = { id, ...toastData };
    
    setToasts(prev => [...prev, newToast]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <ToastNotification
          key={toast.id}
          {...toast}
          onClose={removeToast}
        />
      ))}
    </div>
  );
};

// Toast utility functions
export const showToast = (toastData) => {
  const event = new CustomEvent('showToast', { detail: toastData });
  window.dispatchEvent(event);
};

export const toast = {
  success: (message, title, options = {}) => showToast({
    type: 'success',
    title,
    message,
    ...options
  }),
  
  error: (message, title, options = {}) => showToast({
    type: 'error',
    title,
    message,
    duration: 7000, // Longer duration for errors
    ...options
  }),
  
  warning: (message, title, options = {}) => showToast({
    type: 'warning',
    title,
    message,
    ...options
  }),
  
  info: (message, title, options = {}) => showToast({
    type: 'info',
    title,
    message,
    ...options
  }),

  // Specialized toasts for matching events
  newMatch: (matchData) => showToast({
    type: 'success',
    title: 'New Match Found! 🎯',
    message: `You have a new match with ${matchData.matched_creator_name} (${Math.round(matchData.compatibility_score * 100)}% compatibility)`,
    duration: 8000,
    action: {
      label: 'View Match',
      onClick: () => window.location.href = `/matching?highlight=${matchData.match_id}`
    }
  }),

  matchAccepted: (matchData) => showToast({
    type: 'success',
    title: 'Match Accepted! ✅',
    message: `${matchData.requester_name} accepted your match!`,
    duration: 6000,
    action: {
      label: 'Start Collaboration',
      onClick: () => window.location.href = `/collaborations/new?match=${matchData.match_id}`
    }
  }),

  collaborationInvite: (inviteData) => showToast({
    type: 'info',
    title: 'Collaboration Invite 🤝',
    message: `${inviteData.sender_name} sent you a collaboration invite`,
    duration: 10000,
    action: {
      label: 'View Invite',
      onClick: () => window.location.href = `/collaborations/invites/${inviteData.invite_id}`
    }
  })
};

export { ToastContainer };
export default ToastNotification;
