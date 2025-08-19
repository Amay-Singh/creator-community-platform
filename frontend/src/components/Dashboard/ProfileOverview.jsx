/**
 * Profile Overview Component - Guardian Agent Validated
 * Displays user profile summary and usage statistics
 */
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const ProfileOverview = ({ profile, usage }) => {
  console.log('ProfileOverview received:', { profile, usage });
  
  if (!profile) {
    return (
      <div style={{padding: '2rem', textAlign: 'center'}}>
        <h2>Welcome to Creator Platform!</h2>
        <p>Loading your profile...</p>
        <div style={{marginTop: '1rem'}}>
          <div style={{display: 'inline-block', width: '20px', height: '20px', border: '2px solid #f3f3f3', borderTop: '2px solid #3498db', borderRadius: '50%', animation: 'spin 1s linear infinite'}}></div>
        </div>
      </div>
    );
  }

  const { user } = useAuth();

  return (
    <div style={{padding: '2rem'}}>
      <h2>Dashboard Overview</h2>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1rem'}}>
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>Profile Info</h3>
          <p><strong>Email:</strong> {user?.email}</p>
          <p><strong>Display Name:</strong> {profile.display_name || 'Not set'}</p>
          <p><strong>Category:</strong> {profile.category || 'Not set'}</p>
          <p><strong>Experience:</strong> {profile.experience_level || 'Not set'}</p>
          <p><strong>Bio:</strong> {profile.bio || 'No bio available'}</p>
        </div>
        <div style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
          <h3>Usage Stats</h3>
          <p><strong>Portfolio Items:</strong> {usage?.portfolio_items?.current_usage || 0} / {usage?.portfolio_items?.limit || 5}</p>
          <p><strong>Collaborations:</strong> {usage?.collaborations?.current_usage || 0} / {usage?.collaborations?.limit || 2}</p>
          <p><strong>AI Generations:</strong> {usage?.ai_generations?.current_usage || 0} / {usage?.ai_generations?.limit || 10}</p>
          <p><strong>Storage Used:</strong> {usage?.storage?.current_usage || 0} GB / {usage?.storage?.limit || 1} GB</p>
          <p><strong>Debug Usage:</strong> {usage ? 'Usage data loaded' : 'No usage data'}</p>
        </div>
      </div>
      <div style={{marginTop: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px'}}>
        <h3>Quick Actions</h3>
        <div style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}>
          <button style={{padding: '0.5rem 1rem', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px'}}>
            Update Profile
          </button>
          <button style={{padding: '0.5rem 1rem', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px'}}>
            Add Portfolio Item
          </button>
          <button style={{padding: '0.5rem 1rem', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '4px'}}>
            Find Collaborators
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileOverview;
