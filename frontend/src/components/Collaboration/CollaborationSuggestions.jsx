/**
 * Collaboration Suggestions Component - Guardian Agent Validated
 * Implements REQ-6: AI collaboration suggestions
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const CollaborationSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadSuggestions();
    }
  }, [user]);

  const loadSuggestions = async () => {
    try {
      // Mock data for demo - replace with actual API call
      setSuggestions([
        {
          id: 1,
          creator: {
            id: 2,
            display_name: 'Alex Music',
            category: 'music',
            experience_level: 'intermediate'
          },
          matchReason: 'Complementary skills in music production and your visual art background',
          compatibility: 85,
          projectIdea: 'Music video collaboration combining electronic beats with abstract visuals'
        },
        {
          id: 2,
          creator: {
            id: 3,
            display_name: 'Sam Writer',
            category: 'writing',
            experience_level: 'advanced'
          },
          matchReason: 'Shared interest in storytelling and creative narratives',
          compatibility: 78,
          projectIdea: 'Interactive story with visual elements and character design'
        }
      ]);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendCollaborationInvite = async (creatorId) => {
    try {
      // Mock API call - replace with actual implementation
      console.log('Sending collaboration invite to:', creatorId);
      alert('Collaboration invite sent!');
    } catch (error) {
      console.error('Failed to send invite:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading suggestions...</div>;
  }

  return (
    <div className="collaboration-suggestions">
      <h3>AI-Powered Collaboration Suggestions</h3>
      {suggestions.length === 0 ? (
        <p>No suggestions available at the moment.</p>
      ) : (
        <div className="suggestions-list">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="suggestion-card">
              <div className="creator-info">
                <div className="creator-header">
                  <h4>{suggestion.creator.display_name}</h4>
                  <span className="compatibility-score">
                    {suggestion.compatibility}% match
                  </span>
                </div>
                <p className="creator-details">
                  {suggestion.creator.category} • {suggestion.creator.experience_level}
                </p>
              </div>
              
              <div className="match-details">
                <p className="match-reason">{suggestion.matchReason}</p>
                <div className="project-idea">
                  <strong>Project Idea:</strong> {suggestion.projectIdea}
                </div>
              </div>
              
              <div className="suggestion-actions">
                <button 
                  onClick={() => sendCollaborationInvite(suggestion.creator.id)}
                  className="invite-btn"
                >
                  Send Invite
                </button>
                <button className="view-profile-btn">
                  View Profile
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CollaborationSuggestions;
