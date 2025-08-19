/**
 * Message List Component - Guardian Agent Validated
 * Displays chat messages with real-time updates
 */
import React, { useEffect, useRef } from 'react';
import useClientOnly from '../../hooks/useClientOnly';
import styles from './MessageList.module.css';
import { useAuth } from '../../contexts/AuthContext';

const MessageList = ({ messages, loading }) => {
  const { user } = useAuth();
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const isClient = useClientOnly();

  const formatTimestamp = (timestamp) => {
    if (!isClient) {
      return '00:00'; // Server-side placeholder
    }
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (loading) {
    return <div className={styles.loading}>Loading messages...</div>;
  }

  return (
    <div className={styles.messageList}>
      {messages.length === 0 ? (
        <div className={styles.emptyMessages}>
          <p>No messages yet. Start the conversation!</p>
        </div>
      ) : (
        messages.map((message) => (
          <div 
            key={message.id} 
            className={`${styles.message} ${message.sender.id === user?.id ? styles.ownMessage : styles.otherMessage}`}
          >
            <div className={styles.messageHeader}>
              <span className={styles.senderName}>{message.sender.display_name}</span>
              <span className={styles.messageTime}>{formatTimestamp(message.timestamp)}</span>
            </div>
            <div className={styles.messageContent}>
              {message.content}
              {message.translated_content && (
                <div className={styles.translatedContent}>
                  <em>Translated: {message.translated_content}</em>
                </div>
              )}
            </div>
            {message.attachments && message.attachments.length > 0 && (
              <div className={styles.messageAttachments}>
                {message.attachments.map((attachment, index) => (
                  <div key={index} className={styles.attachment}>
                    📎 {attachment.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))
      )}
      <div ref={messagesEndRef} className={styles.messagesEnd} />
    </div>
  );
};

export default MessageList;
