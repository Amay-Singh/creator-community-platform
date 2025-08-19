/**
 * Chat Interface Component
 * Implements REQ-9, REQ-10, REQ-11: Chat functionality, meeting invites, real-time translation
 */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChatRoomList from './ChatRoomList';
import MeetingInviteModal from './MeetingInviteModal';
import TranslationPanel from './TranslationPanel';
import styles from './ChatInterface.module.css';

const ChatInterface = () => {
  const { user } = useAuth();
  const [chatRooms, setChatRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [translationLanguage, setTranslationLanguage] = useState('es');
  const wsRef = useRef(null);

  useEffect(() => {
    loadChatRooms();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (activeRoom) {
      loadMessages(activeRoom.id);
      connectWebSocket(activeRoom.id);
    }
  }, [activeRoom]);

  const loadChatRooms = async () => {
    try {
      const response = await fetch('/api/chat/rooms/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setChatRooms(data.results || []);
        if (data.results && data.results.length > 0) {
          setActiveRoom(data.results[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load chat rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (roomId) => {
    try {
      const response = await fetch(`/api/chat/rooms/${roomId}/messages/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.results || []);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const connectWebSocket = (roomId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://localhost:8000/ws/chat/${roomId}/`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'chat_message') {
        setMessages(prev => [data.message, ...prev]);
      }
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const sendMessage = async (content, messageType = 'text', fileAttachment = null) => {
    if (!activeRoom || !content.trim()) return;

    const messageData = {
      content: content.trim(),
      message_type: messageType,
      file_attachment: fileAttachment
    };

    try {
      const formData = new FormData();
      formData.append('content', messageData.content);
      formData.append('message_type', messageData.message_type);
      if (fileAttachment) {
        formData.append('file_attachment', fileAttachment);
      }

      const response = await fetch(`/api/chat/rooms/${activeRoom.id}/messages/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const createMeetingInvite = async (meetingData) => {
    try {
      const response = await fetch('/api/chat/meetings/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...meetingData,
          chat_room: activeRoom.id
        })
      });

      if (response.ok) {
        setShowMeetingModal(false);
        // Refresh messages to show meeting invite
        loadMessages(activeRoom.id);
      }
    } catch (error) {
      console.error('Failed to create meeting invite:', error);
    }
  };

  const translateMessage = async (messageId, targetLanguage) => {
    try {
      const response = await fetch(`/api/chat/messages/${messageId}/translate/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          target_language: targetLanguage
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Update message with translation
        setMessages(prev => prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, translations: { ...msg.translations, [targetLanguage]: data.translated_content } }
            : msg
        ));
      }
    } catch (error) {
      console.error('Failed to translate message:', error);
    }
  };

  if (loading) {
    return (
      <div className="chat-loading">
        <div className="loading-spinner"></div>
        <p>Loading conversations...</p>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      {/* Chat Rooms Sidebar */}
      <div className="chat-sidebar">
        <div className="chat-header">
          <h2>Messages</h2>
          <button 
            className="new-chat-btn"
            onClick={() => {/* Open new chat modal */}}
          >
            ➕
          </button>
        </div>
        
        <ChatRoomList 
          rooms={chatRooms}
          activeRoom={activeRoom}
          onRoomSelect={setActiveRoom}
        />
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {activeRoom ? (
          <>
            {/* Chat Header */}
            <div className="chat-room-header">
              <div className="room-info">
                <h3>{activeRoom.name}</h3>
                <p>{activeRoom.participants?.length} participants</p>
              </div>
              
              <div className="chat-actions">
                <button 
                  className="action-btn"
                  onClick={() => setShowTranslation(!showTranslation)}
                  title="Toggle Translation"
                >
                  🌐
                </button>
                <button 
                  className="action-btn"
                  onClick={() => setShowMeetingModal(true)}
                  title="Schedule Meeting"
                >
                  📅
                </button>
                <button className="action-btn" title="Room Settings">
                  ⚙️
                </button>
              </div>
            </div>

            {/* Translation Panel */}
            {showTranslation && (
              <TranslationPanel 
                language={translationLanguage}
                onLanguageChange={setTranslationLanguage}
                onClose={() => setShowTranslation(false)}
              />
            )}

            {/* Messages */}
            <MessageList 
              messages={messages}
              currentUser={user}
              onTranslate={translateMessage}
              translationLanguage={translationLanguage}
            />

            {/* Message Input */}
            <MessageInput 
              onSendMessage={sendMessage}
              disabled={!activeRoom}
            />
          </>
        ) : (
          <div className="no-chat-selected">
            <div className="empty-state">
              <h3>Select a conversation</h3>
              <p>Choose a chat room from the sidebar to start messaging</p>
            </div>
          </div>
        )}
      </div>

      {/* Meeting Invite Modal */}
      {showMeetingModal && (
        <MeetingInviteModal 
          onClose={() => setShowMeetingModal(false)}
          onCreateMeeting={createMeetingInvite}
          participants={activeRoom?.participants || []}
        />
      )}
    </div>
  );
};

export default ChatInterface;
