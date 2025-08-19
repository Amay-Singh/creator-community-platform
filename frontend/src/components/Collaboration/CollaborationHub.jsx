/**
 * Collaboration Hub Component
 * Implements REQ-8, REQ-12: Collaboration invites with match explanations, collaboration tools
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import CollaborationInvites from './CollaborationInvites';
import CollaborationTools from './CollaborationTools';
import CollaborationSuggestions from './CollaborationSuggestions';
import styles from './CollaborationHub.module.css';

const CollaborationHub = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('invites');
  const [invites, setInvites] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [activeCollaborations, setActiveCollaborations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCollaborationData();
  }, []);

  const loadCollaborationData = async () => {
    try {
      await Promise.all([
        loadInvites(),
        loadSuggestions(),
        loadActiveCollaborations()
      ]);
    } catch (error) {
      console.error('Failed to load collaboration data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadInvites = async () => {
    try {
      const response = await fetch('/api/collaborations/invites/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInvites(data.results || []);
      }
    } catch (error) {
      console.error('Failed to load invites:', error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const response = await fetch('/api/collaborations/suggestions/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const loadActiveCollaborations = async () => {
    try {
      const response = await fetch('/api/collaborations/invites/?status=accepted', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setActiveCollaborations(data.results || []);
      }
    } catch (error) {
      console.error('Failed to load active collaborations:', error);
    }
  };

  const handleInviteResponse = async (inviteId, status) => {
    try {
      const response = await fetch(`/api/collaborations/invites/${inviteId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        loadInvites();
        if (status === 'accepted') {
          loadActiveCollaborations();
        }
      }
    } catch (error) {
      console.error('Failed to respond to invite:', error);
    }
  };

  const sendCollaborationInvite = async (recipientId, title, description) => {
    try {
      const response = await fetch('/api/collaborations/invites/create/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipient: recipientId,
          title,
          description
        })
      });

      if (response.ok) {
        loadInvites();
        return true;
      }
    } catch (error) {
      console.error('Failed to send invite:', error);
    }
    return false;
  };

  const tabConfig = [
    { id: 'invites', label: 'Invites', icon: '📨', count: invites.length },
    { id: 'active', label: 'Active', icon: '🤝', count: activeCollaborations.length },
    { id: 'suggestions', label: 'Suggestions', icon: '💡', count: suggestions.length },
    { id: 'tools', label: 'Tools', icon: '🛠️' }
  ];

  if (loading) {
    return (
      <div className="collaboration-loading">
        <div className="loading-spinner"></div>
        <p>Loading collaborations...</p>
      </div>
    );
  }

  return (
    <div className="collaboration-hub">
      <div className="hub-header">
        <h2>Collaboration Hub</h2>
        <p>Connect, create, and collaborate with fellow creators</p>
      </div>

      {/* Tab Navigation */}
      <div className="hub-tabs">
        {tabConfig.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
            {tab.count !== undefined && tab.count > 0 && (
              <span className="tab-count">{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="hub-content">
        {activeTab === 'invites' && (
          <CollaborationInvites
            invites={invites}
            onInviteResponse={handleInviteResponse}
            onSendInvite={sendCollaborationInvite}
          />
        )}

        {activeTab === 'active' && (
          <div className="active-collaborations">
            <div className="section-header">
              <h3>Active Collaborations</h3>
              <p>Your ongoing creative partnerships</p>
            </div>

            {activeCollaborations.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🤝</div>
                <h3>No active collaborations</h3>
                <p>Accept collaboration invites or send new ones to get started</p>
                <button 
                  className="cta-btn"
                  onClick={() => setActiveTab('suggestions')}
                >
                  Find Collaborators
                </button>
              </div>
            ) : (
              <div className="collaborations-grid">
                {activeCollaborations.map(collab => (
                  <div key={collab.id} className="collaboration-card">
                    <div className="card-header">
                      <h4>{collab.title}</h4>
                      <span className="status-badge active">Active</span>
                    </div>
                    
                    <p className="card-description">{collab.description}</p>
                    
                    <div className="collaborators">
                      <div className="collaborator">
                        <img 
                          src={collab.sender.avatar || '/default-avatar.png'} 
                          alt={collab.sender.display_name}
                        />
                        <span>{collab.sender.display_name}</span>
                      </div>
                      <div className="collaborator">
                        <img 
                          src={collab.recipient.avatar || '/default-avatar.png'} 
                          alt={collab.recipient.display_name}
                        />
                        <span>{collab.recipient.display_name}</span>
                      </div>
                    </div>
                    
                    <div className="card-actions">
                      <button 
                        className="action-btn primary"
                        onClick={() => setActiveTab('tools')}
                      >
                        Open Tools
                      </button>
                      <button className="action-btn">
                        💬 Chat
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'suggestions' && (
          <CollaborationSuggestions
            suggestions={suggestions}
            onSendInvite={sendCollaborationInvite}
            onRefresh={loadSuggestions}
          />
        )}

        {activeTab === 'tools' && (
          <CollaborationTools
            collaborations={activeCollaborations}
          />
        )}
      </div>
    </div>
  );
};

export default CollaborationHub;
