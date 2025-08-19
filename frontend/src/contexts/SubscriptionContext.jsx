/**
 * Subscription Context
 * Manages subscription state and usage data
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

export const SubscriptionProvider = ({ children }) => {
  const { user } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadSubscriptionData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const loadSubscriptionData = async () => {
    try {
      await Promise.all([
        loadSubscription(),
        loadUsage()
      ]);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSubscription = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      if (!token) return;

      const response = await fetch('http://127.0.0.1:8000/api/auth/subscription/current/', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSubscription(data.subscription);
      }
    } catch (error) {
      console.error('Failed to load subscription:', error);
    }
  };

  const loadUsage = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      if (!token) return;

      const response = await fetch('http://127.0.0.1:8000/api/auth/subscription/usage-limits/', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsage(data.usage_limits);
      }
    } catch (error) {
      console.error('Failed to load usage:', error);
    }
  };

  const checkUsageLimit = (featureType) => {
    if (!usage || !usage[featureType]) return { canUse: true, limit: 0, used: 0 };
    
    const featureUsage = usage[featureType];
    return {
      canUse: !featureUsage.is_exceeded,
      limit: featureUsage.limit,
      used: featureUsage.current_usage,
      percentage: featureUsage.usage_percentage
    };
  };

  const incrementUsage = async (featureType, amount = 1) => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      if (!token) return false;

      const response = await fetch('http://127.0.0.1:8000/api/auth/subscription/usage/increment/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          feature_type: featureType,
          amount
        })
      });

      if (response.ok) {
        await loadUsage(); // Refresh usage data
        return true;
      }
    } catch (error) {
      console.error('Failed to increment usage:', error);
    }
    return false;
  };

  const value = {
    subscription,
    usage,
    loading,
    checkUsageLimit,
    incrementUsage,
    refreshSubscription: loadSubscriptionData
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};
