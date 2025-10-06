/**
 * Main Dashboard Component - ReqDoc02 Phase 2 Redesign
 * Modern glassmorphism design with Gen-Z aesthetic
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import Navigation from '../ui/Navigation';
import DashboardCard from '../ui/DashboardCard';
import Card from '../ui/Card';
import Button from '../ui/Button';

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
      const response = await fetch('https://creator-platform-backend-vfuz.onrender.com/api/accounts/dashboard/', {
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Dashboard...</h2>
          <p className="text-gray-600">Setting up your creative workspace...</p>
        </motion.div>
      </div>
    );
  }
};

export default Dashboard;
