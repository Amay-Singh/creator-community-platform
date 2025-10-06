import React from 'react';
import { motion } from 'framer-motion';
import Card from './Card';

/**
 * Dashboard Card Component - ReqDoc02 Phase 2
 * Features: Quick actions, activity feed, AI suggestions
 */
const DashboardCard = ({ 
  title, 
  subtitle, 
  icon: Icon, 
  children, 
  action, 
  variant = 'default',
  className = '',
  ...props 
}) => {
  const variants = {
    default: 'glass',
    primary: 'gradient',
    secondary: 'default'
  };

  return (
    <Card variant={variants[variant]} hover={true} className={`h-full ${className}`} {...props}>
      <Card.Header>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {Icon && (
              <motion.div 
                className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Icon className="w-6 h-6 text-white" />
              </motion.div>
            )}
            <div>
              <Card.Title className="text-lg font-bold text-gray-900">{title}</Card.Title>
              {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
            </div>
          </div>
          {action && (
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {action}
            </motion.div>
          )}
        </div>
      </Card.Header>
      <Card.Content>
        {children}
      </Card.Content>
    </Card>
  );
};

// Quick Actions Card
const QuickActionsCard = () => {
  const actions = [
    {
      title: 'Find Collaborators',
      description: 'Discover creators to work with',
      icon: (props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'from-blue-500 to-purple-500',
      href: '/discover'
    },
    {
      title: 'AI Content Studio',
      description: 'Generate content with AI',
      icon: (props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: 'from-purple-500 to-pink-500',
      href: '/ai-studio'
    },
    {
      title: 'Start Project',
      description: 'Create a new collaboration',
      icon: (props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      ),
      color: 'from-green-500 to-emerald-500',
      href: '/projects/new'
    }
  ];

  return (
    <DashboardCard
      title="Quick Actions"
      subtitle="Get started with common tasks"
      icon={(props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      )}
    >
      <div className="grid gap-4">
        {actions.map((action, index) => (
          <motion.a
            key={action.title}
            href={action.href}
            className="flex items-center space-x-4 p-4 rounded-2xl bg-white/20 hover:bg-white/30 transition-all duration-300 group"
            whileHover={{ scale: 1.02, x: 5 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
          >
            <div className={`w-10 h-10 bg-gradient-to-br ${action.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
              <action.icon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{action.title}</h4>
              <p className="text-sm text-gray-600">{action.description}</p>
            </div>
            <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </motion.a>
        ))}
      </div>
    </DashboardCard>
  );
};

// Activity Feed Card
const ActivityFeedCard = () => {
  const activities = [
    {
      type: 'collaboration',
      title: 'New collaboration request',
      description: 'Sarah Chen wants to collaborate on a music video',
      time: '2 minutes ago',
      avatar: 'SC',
      color: 'from-blue-500 to-purple-500'
    },
    {
      type: 'message',
      title: 'New message',
      description: 'Alex Rodriguez: "Great work on the latest project!"',
      time: '1 hour ago',
      avatar: 'AR',
      color: 'from-green-500 to-emerald-500'
    },
    {
      type: 'ai',
      title: 'AI suggestion ready',
      description: 'Your content analysis is complete',
      time: '3 hours ago',
      avatar: 'AI',
      color: 'from-purple-500 to-pink-500'
    }
  ];

  return (
    <DashboardCard
      title="Recent Activity"
      subtitle="Stay updated with your latest interactions"
      icon={(props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      )}
    >
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <motion.div
            key={index}
            className="flex items-start space-x-3 p-3 rounded-2xl hover:bg-white/20 transition-all duration-300 cursor-pointer group"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            whileHover={{ scale: 1.02, x: 5 }}
          >
            <div className={`w-10 h-10 bg-gradient-to-br ${activity.color} rounded-xl flex items-center justify-center shadow-lg flex-shrink-0`}>
              <span className="text-white font-bold text-sm">{activity.avatar}</span>
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">{activity.title}</h4>
              <p className="text-sm text-gray-600 truncate">{activity.description}</p>
              <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </DashboardCard>
  );
};

// AI Suggestions Card
const AISuggestionsCard = () => {
  const suggestions = [
    {
      title: 'Trending Creator',
      name: 'Maya Patel',
      specialty: 'Digital Art & Animation',
      match: 95,
      avatar: 'MP'
    },
    {
      title: 'Hot Collaboration',
      name: 'Tech Startup Promo',
      specialty: 'Video Production Needed',
      match: 88,
      avatar: 'TS'
    }
  ];

  return (
    <DashboardCard
      title="AI Suggestions"
      subtitle="Personalized recommendations for you"
      icon={(props) => (
        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      )}
    >
      <div className="space-y-4">
        {suggestions.map((suggestion, index) => (
          <motion.div
            key={index}
            className="flex items-center justify-between p-4 rounded-2xl bg-white/20 hover:bg-white/30 transition-all duration-300 cursor-pointer group"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.2 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-sm">{suggestion.avatar}</span>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">{suggestion.title}</p>
                <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{suggestion.name}</h4>
                <p className="text-sm text-gray-600">{suggestion.specialty}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-green-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-xs">{suggestion.match}</span>
                </div>
                <span className="text-xs text-gray-500">% match</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </DashboardCard>
  );
};

DashboardCard.QuickActions = QuickActionsCard;
DashboardCard.ActivityFeed = ActivityFeedCard;
DashboardCard.AISuggestions = AISuggestionsCard;

export default DashboardCard;
