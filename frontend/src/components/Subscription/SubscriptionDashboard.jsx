/**
 * Subscription Dashboard Component
 * Implements REQ-22-25: Subscription and payment system
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import SubscriptionPlans from './SubscriptionPlans';
import UsageMetrics from './UsageMetrics';
import PaymentHistory from './PaymentHistory';
import PremiumAddons from './PremiumAddons';
import './SubscriptionDashboard.css';

const SubscriptionDashboard = () => {
  const { user } = useAuth();
  const { subscription, usage, refreshSubscription } = useSubscription();
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptionAnalytics();
  }, []);

  const loadSubscriptionAnalytics = async () => {
    try {
      const response = await fetch('/api/accounts/subscription/analytics/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planId, billingCycle) => {
    try {
      const response = await fetch('/api/accounts/subscription/create/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          plan_id: planId,
          billing_cycle: billingCycle
        })
      });

      if (response.ok) {
        await refreshSubscription();
        setActiveTab('overview');
      }
    } catch (error) {
      console.error('Failed to upgrade subscription:', error);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return;

    try {
      const response = await fetch('/api/accounts/subscription/cancel/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reason: 'User requested cancellation'
        })
      });

      if (response.ok) {
        await refreshSubscription();
      }
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
    }
  };

  const tabConfig = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'plans', label: 'Plans', icon: '💎' },
    { id: 'usage', label: 'Usage', icon: '📈' },
    { id: 'addons', label: 'Add-ons', icon: '🔧' },
    { id: 'billing', label: 'Billing', icon: '💳' }
  ];

  if (loading) {
    return (
      <div className="subscription-loading">
        <div className="loading-spinner"></div>
        <p>Loading subscription details...</p>
      </div>
    );
  }

  return (
    <div className="subscription-dashboard">
      <div className="dashboard-header">
        <h2>Subscription & Billing</h2>
        <p>Manage your plan, usage, and billing preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="dashboard-tabs">
        {tabConfig.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            {/* Current Plan */}
            <div className="current-plan-card">
              <div className="card-header">
                <h3>Current Plan</h3>
                <span className={`plan-badge ${subscription?.plan?.plan_type}`}>
                  {subscription?.plan?.name}
                </span>
              </div>
              
              <div className="plan-details">
                <div className="plan-info">
                  <p><strong>Status:</strong> {subscription?.status}</p>
                  <p><strong>Billing:</strong> {subscription?.billing_cycle}</p>
                  <p><strong>Renewal:</strong> {subscription?.current_period_end && typeof window !== 'undefined' ? new Date(subscription.current_period_end).toLocaleDateString() : 'Loading...'}</p>
                  <p><strong>Days Remaining:</strong> {subscription?.days_remaining}</p>
                </div>
                
                <div className="plan-actions">
                  {subscription?.plan?.plan_type !== 'pro' && (
                    <button 
                      className="upgrade-btn"
                      onClick={() => setActiveTab('plans')}
                    >
                      ⬆️ Upgrade Plan
                    </button>
                  )}
                  {subscription?.status === 'active' && subscription?.plan?.plan_type !== 'free' && (
                    <button 
                      className="cancel-btn"
                      onClick={handleCancelSubscription}
                    >
                      ❌ Cancel Plan
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Usage Overview */}
            {analytics && (
              <div className="usage-overview">
                <h3>Usage This Month</h3>
                <div className="usage-grid">
                  <div className="usage-item">
                    <div className="usage-icon">🎨</div>
                    <div className="usage-info">
                      <span className="usage-label">Portfolio Items</span>
                      <div className="usage-bar">
                        <div 
                          className="usage-fill"
                          style={{ width: `${analytics.feature_utilization.portfolio_items.percentage}%` }}
                        ></div>
                      </div>
                      <span className="usage-text">
                        {analytics.feature_utilization.portfolio_items.used} / {analytics.feature_utilization.portfolio_items.limit}
                      </span>
                    </div>
                  </div>

                  <div className="usage-item">
                    <div className="usage-icon">🤝</div>
                    <div className="usage-info">
                      <span className="usage-label">Collaborations</span>
                      <div className="usage-bar">
                        <div 
                          className="usage-fill"
                          style={{ width: `${analytics.feature_utilization.collaborations.percentage}%` }}
                        ></div>
                      </div>
                      <span className="usage-text">
                        {analytics.feature_utilization.collaborations.used} / {analytics.feature_utilization.collaborations.limit}
                      </span>
                    </div>
                  </div>

                  <div className="usage-item">
                    <div className="usage-icon">🤖</div>
                    <div className="usage-info">
                      <span className="usage-label">AI Generations</span>
                      <div className="usage-bar">
                        <div 
                          className="usage-fill"
                          style={{ width: `${analytics.feature_utilization.ai_generations.percentage}%` }}
                        ></div>
                      </div>
                      <span className="usage-text">
                        {analytics.feature_utilization.ai_generations.used} / {analytics.feature_utilization.ai_generations.limit}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {analytics?.recommendations && analytics.recommendations.length > 0 && (
              <div className="recommendations">
                <h3>Recommendations</h3>
                <div className="recommendation-list">
                  {analytics.recommendations.map((rec, index) => (
                    <div key={index} className={`recommendation-item ${rec.type}`}>
                      <div className="rec-icon">
                        {rec.type === 'upgrade' && '⬆️'}
                        {rec.type === 'addon' && '🔧'}
                      </div>
                      <div className="rec-content">
                        <p>{rec.message}</p>
                        <button 
                          className="rec-action"
                          onClick={() => {
                            if (rec.action === 'upgrade_plan') setActiveTab('plans');
                            if (rec.action === 'buy_ai_credits') setActiveTab('addons');
                          }}
                        >
                          Take Action
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'plans' && (
          <SubscriptionPlans 
            currentPlan={subscription?.plan}
            onUpgrade={handleUpgrade}
          />
        )}

        {activeTab === 'usage' && (
          <UsageMetrics 
            usage={usage}
            analytics={analytics}
          />
        )}

        {activeTab === 'addons' && (
          <PremiumAddons />
        )}

        {activeTab === 'billing' && (
          <PaymentHistory />
        )}
      </div>
    </div>
  );
};

export default SubscriptionDashboard;
