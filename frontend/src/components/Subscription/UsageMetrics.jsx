/**
 * Usage Metrics Component
 * Displays usage statistics without rendering objects directly
 */
import React from 'react';

const UsageMetrics = ({ usage, analytics }) => {
  if (!usage) {
    return (
      <div style={{padding: '2rem', textAlign: 'center'}}>
        <p>No usage data available</p>
      </div>
    );
  }

  return (
    <div style={{padding: '2rem'}}>
      <h2>Usage Metrics</h2>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginTop: '1rem'}}>
        
        {/* Portfolio Items */}
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>Portfolio Items</h3>
          <p>Used: {usage.portfolio_items?.current_usage || 0}</p>
          <p>Limit: {usage.portfolio_items?.limit || 0}</p>
          <p>Percentage: {usage.portfolio_items?.usage_percentage || 0}%</p>
        </div>

        {/* Collaborations */}
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>Collaborations</h3>
          <p>Used: {usage.collaborations?.current_usage || 0}</p>
          <p>Limit: {usage.collaborations?.limit || 0}</p>
          <p>Percentage: {usage.collaborations?.usage_percentage || 0}%</p>
        </div>

        {/* AI Generations */}
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>AI Generations</h3>
          <p>Used: {usage.ai_generations?.current_usage || 0}</p>
          <p>Limit: {usage.ai_generations?.limit || 0}</p>
          <p>Percentage: {usage.ai_generations?.usage_percentage || 0}%</p>
        </div>

        {/* Storage */}
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>Storage</h3>
          <p>Used: {usage.storage?.current_usage || 0} GB</p>
          <p>Limit: {usage.storage?.limit || 0} GB</p>
          <p>Percentage: {usage.storage?.usage_percentage || 0}%</p>
        </div>

      </div>
    </div>
  );
};

export default UsageMetrics;
