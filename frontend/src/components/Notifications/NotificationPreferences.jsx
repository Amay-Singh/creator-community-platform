import React, { useState, useEffect } from 'react';
import { Save, Bell, Volume2, VolumeX, Smartphone, Mail } from 'lucide-react';
import { useNotifications } from '../../hooks/useNotifications';

const NotificationPreferences = () => {
  const { preferences, updatePreferences, loading } = useNotifications();
  const [localPreferences, setLocalPreferences] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  const handleToggle = (key) => {
    setLocalPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updatePreferences(localPreferences);
    } finally {
      setSaving(false);
    }
  };

  const preferenceGroups = [
    {
      title: 'AI Matching Notifications',
      icon: <Bell className="w-5 h-5" />,
      preferences: [
        { key: 'match_found', label: 'New matches found', description: 'Get notified when AI finds new potential collaborators' },
        { key: 'match_accepted', label: 'Match accepted', description: 'When someone accepts your match' },
        { key: 'match_declined', label: 'Match declined', description: 'When someone declines your match' },
        { key: 'match_feedback_received', label: 'Match feedback', description: 'When you receive feedback on matches' },
        { key: 'match_expired', label: 'Match expired', description: 'When matches expire due to inactivity' }
      ]
    },
    {
      title: 'Collaboration & Social',
      icon: <Bell className="w-5 h-5" />,
      preferences: [
        { key: 'collaboration_invite', label: 'Collaboration invites', description: 'When someone invites you to collaborate' },
        { key: 'message_received', label: 'New messages', description: 'Direct messages and chat notifications' },
        { key: 'profile_followed', label: 'New followers', description: 'When someone follows your profile' }
      ]
    },
    {
      title: 'System & Updates',
      icon: <Bell className="w-5 h-5" />,
      preferences: [
        { key: 'system_announcement', label: 'System announcements', description: 'Important platform updates and news' }
      ]
    },
    {
      title: 'Delivery Methods',
      icon: <Smartphone className="w-5 h-5" />,
      preferences: [
        { key: 'push_notifications', label: 'Push notifications', description: 'Browser and mobile push notifications' },
        { key: 'email_notifications', label: 'Email notifications', description: 'Receive notifications via email' },
        { key: 'sound_enabled', label: 'Sound alerts', description: 'Play sound when notifications arrive' }
      ]
    }
  ];

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Notification Preferences</h1>
        <p className="text-gray-600">
          Customize how and when you receive notifications from the Creator Community Platform.
        </p>
      </div>

      <div className="space-y-8">
        {preferenceGroups.map((group, groupIndex) => (
          <div key={groupIndex} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                {group.icon}
                <h2 className="text-lg font-semibold text-gray-900">{group.title}</h2>
              </div>
            </div>
            
            <div className="divide-y divide-gray-200">
              {group.preferences.map((pref) => (
                <div key={pref.key} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-sm font-medium text-gray-900">
                          {pref.label}
                        </h3>
                        {pref.key === 'sound_enabled' && (
                          localPreferences[pref.key] ? 
                            <Volume2 className="w-4 h-4 text-green-500" /> : 
                            <VolumeX className="w-4 h-4 text-gray-400" />
                        )}
                        {pref.key === 'email_notifications' && (
                          <Mail className="w-4 h-4 text-blue-500" />
                        )}
                        {pref.key === 'push_notifications' && (
                          <Smartphone className="w-4 h-4 text-purple-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {pref.description}
                      </p>
                    </div>
                    
                    <div className="ml-4">
                      <button
                        onClick={() => handleToggle(pref.key)}
                        className={`
                          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                          ${localPreferences[pref.key] 
                            ? 'bg-blue-600' 
                            : 'bg-gray-200'
                          }
                        `}
                      >
                        <span
                          className={`
                            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                            ${localPreferences[pref.key] 
                              ? 'translate-x-6' 
                              : 'translate-x-1'
                            }
                          `}
                        />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Save Button */}
      <div className="mt-8 flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`
            flex items-center space-x-2 px-6 py-3 rounded-lg font-medium
            ${saving
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
            }
            text-white transition-colors
          `}
        >
          <Save className="w-4 h-4" />
          <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
        </button>
      </div>

      {/* Browser Notification Permission */}
      <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start space-x-3">
          <Bell className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-yellow-800">
              Browser Notification Permission
            </h3>
            <p className="text-sm text-yellow-700 mt-1">
              To receive real-time notifications, please allow browser notifications when prompted.
            </p>
            <button
              onClick={() => {
                if ('Notification' in window) {
                  Notification.requestPermission();
                }
              }}
              className="mt-2 text-sm text-yellow-800 underline hover:text-yellow-900"
            >
              Request permission
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationPreferences;
