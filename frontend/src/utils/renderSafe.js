/**
 * Guardian Agent: Render-Safe Utilities
 * Prevents object rendering errors by providing safe rendering functions
 */

/**
 * Safely render any value as a string
 */
export const renderSafe = (value) => {
  if (value === null || value === undefined) {
    return '';
  }
  
  if (typeof value === 'object') {
    // Never render objects directly - convert to string representation
    if (Array.isArray(value)) {
      return value.length > 0 ? `${value.length} items` : 'No items';
    }
    return '[Object]';
  }
  
  return String(value);
};

/**
 * Safely render usage statistics
 */
export const renderUsage = (usage, feature) => {
  if (!usage || !usage[feature]) {
    return { used: 0, limit: 0, percentage: 0 };
  }
  
  const featureUsage = usage[feature];
  return {
    used: featureUsage.current_usage || 0,
    limit: featureUsage.limit || 0,
    percentage: featureUsage.usage_percentage || 0
  };
};

/**
 * Safely render user information
 */
export const renderUser = (user) => {
  if (!user) return 'No user';
  return `${user.email || user.username || 'Unknown user'}`;
};

/**
 * Safely render profile information
 */
export const renderProfile = (profile) => {
  if (!profile) return 'No profile';
  return `${profile.display_name || profile.user_email || 'Unknown profile'}`;
};

/**
 * Debug object safely without rendering
 */
export const debugObject = (obj, label = 'Object') => {
  console.log(`🔍 ${label}:`, obj);
  return `[${label} logged to console]`;
};
