/**
 * Collaboration Invites Component - Guardian Agent Validated
 * Implements REQ-8: Collaboration invites with match explanations
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const CollaborationInvites = () => {
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadInvites();
    }
  }, [user]);

  const loadInvites = async () => {
    try {
      // Mock data for demo - replace with actual API call
      setInvites([
        {
          id: 1,
          sender: {
            id: 2,
            display_name: 'Maya Artist',
            category: 'visual-art',
            experience_level: 'advanced'
          },
          status: 'pending',
          match_explanation: 'Your music composition skills complement Maya\'s visual art expertise perfectly for multimedia projects.',
          project_description: 'Creating an immersive audio-visual experience for gallery exhibitions',
          created_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Failed to load invites:', error);
    } finally {
      setLoading(false);
    }
  };

  const respondToInvite = async (inviteId, response) => {
    try {
      // Mock API call - replace with actual implementation
      console.log('Responding to invite:', inviteId, response);
      setInvites(invites.map(invite => 
        invite.id === inviteId 
          ? { ...invite, status: response }
          : invite
      ));
    } catch (error) {
      console.error('Failed to respond to invite:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading invites...</div>;
  }

  return (
    <div className="collaboration-invites">
      <h3>Collaboration Invites</h3>
      {invites.length === 0 ? (
        <p>No collaboration invites at the moment.</p>
      ) : (
        <div className="invites-list">
          {invites.map((invite) => (
            <div key={invite.id} className="invite-card">
              <div className="invite-header">
                <div className="sender-info">
                  <h4>{invite.sender.display_name}</h4>
                  Let's create something amazing together!
                  <span className="sender-category">
                    {invite.sender.category} • {invite.sender.experience_level}
                  </span>
                </div>
                <span className={`status-badge ${invite.status}`}>
                  {invite.status}
                </span>
              </div>
              
              <div className="match-explanation">
                <strong>Why you're a great match:</strong>
                <p>{invite.match_explanation}</p>
              </div>
              
              <div className="project-description">
                <strong>Project:</strong>
                <p>{invite.project_description}</p>
              </div>
              
              {invite.status === 'pending' && (
                <div className="invite-actions">
                  <button 
                    onClick={() => respondToInvite(invite.id, 'accepted')}
                    className="accept-btn"
                  >
                    Accept
                  </button>
                  <button 
                    onClick={() => respondToInvite(invite.id, 'declined')}
                    className="decline-btn"
                  >
                    Decline
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CollaborationInvites;
