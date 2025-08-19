/**
 * Chat Room List Component - Guardian Agent Validated
 * Displays available chat rooms and conversations
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const ChatRoomList = ({ onRoomSelect, activeRoom }) => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadChatRooms();
    }
  }, [user]);

  const loadChatRooms = async () => {
    try {
      // Mock data for demo - replace with actual API call
      setRooms([
        {
          id: 1,
          name: 'General Discussion',
          type: 'public',
          participants: 15,
          lastMessage: 'Welcome to the community!',
          lastActivity: new Date().toISOString()
        },
        {
          id: 2,
          name: 'Music Collaboration',
          type: 'group',
          participants: 8,
          lastMessage: 'Anyone interested in a jazz project?',
          lastActivity: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Failed to load chat rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading chat rooms...</div>;
  }

  return (
    <div className="chat-room-list">
      <h3>Chat Rooms</h3>
      {rooms.length === 0 ? (
        <p>No chat rooms available.</p>
      ) : (
        <div className="room-list">
          {rooms.map((room) => (
            <div 
              key={room.id} 
              className={`room-item ${activeRoom?.id === room.id ? 'active' : ''}`}
              onClick={() => onRoomSelect(room)}
            >
              <div className="room-header">
                <span className="room-name">{room.name}</span>
                <span className="room-type">{room.type}</span>
              </div>
              <div className="room-info">
                <span className="participant-count">{room.participants} members</span>
              </div>
              <div className="last-message">{room.lastMessage}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatRoomList;
