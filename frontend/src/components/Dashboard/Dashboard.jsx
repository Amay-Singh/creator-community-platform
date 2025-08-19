/**
 * Main Dashboard Component
 * Central hub for creators with all platform features
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import ProfileOverview from './ProfileOverview';
import CollaborationHub from '../Collaboration/CollaborationHub';
import ChatInterface from '../Chat/ChatInterface';
import AIContentGenerator from '../AI/AIContentGenerator';
import AdShowcase from '../Ads/AdShowcase';
import SubscriptionStatus from '../Subscription/SubscriptionStatus';
import styles from './Dashboard.module.css';

const Dashboard = () => {
  const { user, profile, logout } = useAuth();
  const { subscription, usage } = useSubscription();
  const [activeTab, setActiveTab] = useState('overview');
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Load initial dashboard data
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load notifications, recent activity, etc.
      const response = await fetch('http://127.0.0.1:8000/api/accounts/dashboard/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleLogout = () => {
    try {
      logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      // Force redirect even if logout fails
      window.location.href = '/login';
    }
  };

  const tabConfig = [
    { id: 'overview', label: 'Overview', icon: '🏠' },
    { id: 'collaborations', label: 'Collaborations', icon: '🤝' },
    { id: 'chat', label: 'Messages', icon: '💬' },
    { id: 'ai-tools', label: 'AI Tools', icon: '🤖' },
    { id: 'portfolio', label: 'Portfolio', icon: '🎨' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <ProfileOverview profile={profile} usage={usage} />;
      case 'collaborations':
        return <CollaborationHub />;
      case 'chat':
        return <ChatInterface />;
      case 'ai-tools':
        return <AIContentGenerator />;
      case 'portfolio':
        return <div>Portfolio Management Component</div>;
      default:
        return <ProfileOverview profile={profile} usage={usage} />;
    }
  };

  console.log('Dashboard render - user:', user, 'profile:', profile);
  console.log('Dashboard render - profile type:', typeof profile, 'profile keys:', profile ? Object.keys(profile) : 'null');
  
  // Profile exists but may be empty object - check for required fields
  if (!user || !profile || !profile.user_email) {
    return (
      <div style={{padding: '2rem', textAlign: 'center'}}>
        <h2>Loading Dashboard...</h2>
        <p>User: {user ? 'Loaded' : 'NULL'}</p>
        <p>Profile: {profile ? 'Loaded' : 'NULL'}</p>
        <div style={{marginTop: '1rem'}}>
          <div style={{display: 'inline-block', width: '30px', height: '30px', border: '3px solid #f3f3f3', borderTop: '3px solid #3498db', borderRadius: '50%', animation: 'spin 1s linear infinite'}}></div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <header className={styles.dashboardHeader}>
        <div className={styles.headerContent}>
          <div className={styles.userInfo}>
            <img 
              src={profile.avatar || '/default-avatar.png'} 
              alt={profile.display_name}
              className={styles.userAvatar}
            />
            <div>
              <h1>Welcome back, {profile.display_name}!</h1>
              <p className={styles.userCategory}>{profile.category} • {profile.experience_level}</p>
            </div>
          </div>
          
          <div className={styles.headerActions}>
            <SubscriptionStatus subscription={subscription} />
            <div className={styles.notifications}>
              <button className={styles.notificationBtn}>
                🔔
                {notifications.length > 0 && (
                  <span className={styles.notificationBadge}>{notifications.length}</span>
                )}
              </button>
            </div>
            <button 
              onClick={handleLogout}
              className={styles.logoutBtn}
              title="Sign out"
            >
              <span className={styles.logoutIcon}>👋</span>
              <span className={styles.logoutText}>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className={styles.dashboardContent}>
        {/* Sidebar Navigation */}
        <nav className={styles.dashboardNav}>
          {tabConfig.map(tab => (
            <button
              key={tab.id}
              className={`${styles.navTab} ${activeTab === tab.id ? styles.active : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className={styles.tabIcon}>{tab.icon}</span>
              <span className={styles.tabLabel}>{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Main Content Area */}
        <main className={styles.dashboardMain}>
          {renderTabContent()}
        </main>

        {/* Sidebar - Ads and Quick Actions */}
        <aside className={styles.dashboardSidebar}>
          <AdShowcase context="dashboard" />
          
          <div className={styles.quickActions}>
            <h3>Quick Actions</h3>
            <button className={styles.quickActionBtn}>
              ➕ New Portfolio Item
            </button>
            <button className={styles.quickActionBtn}>
              🤝 Find Collaborators
            </button>
            <button className={styles.quickActionBtn}>
              🤖 Generate Content
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
