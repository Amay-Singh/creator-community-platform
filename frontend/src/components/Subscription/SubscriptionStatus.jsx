/**
 * Subscription Status Component - Guardian Agent Validated
 * Displays user subscription information and usage
 */
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';

const SubscriptionStatus = ({ subscription }) => {
  const { user } = useAuth();
  const { usage } = useSubscription();

  if (!subscription) {
    return (
      <div className="subscription-status">
        <span className="status-badge free">Free Plan</span>
      </div>
    );
  }

  return (
    <div className="subscription-status">
      <div className="status-info">
        <span className={`status-badge ${subscription.plan?.plan_type || subscription.plan}`}>
          {subscription.plan?.name || subscription.plan || 'Free'} Plan
        </span>
        {usage && (
          <div className="usage-info">
            <small>{usage.ai_generations?.current_usage || 0}/100 AI generations</small>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionStatus;
