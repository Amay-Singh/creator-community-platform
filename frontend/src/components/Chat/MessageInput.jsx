/**
 * Message Input Component - Guardian Agent Validated
 * Handles message composition and sending
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const MessageInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const { user } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage({
        content: message.trim(),
        attachments: attachments
      });
      setMessage('');
      setAttachments([]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setAttachments([...attachments, ...files]);
  };

  const removeAttachment = (index) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  return (
    <div className="message-input">
      {attachments.length > 0 && (
        <div className="attachments-preview">
          {attachments.map((file, index) => (
            <div key={index} className="attachment-item">
              <span>{file.name}</span>
              <button onClick={() => removeAttachment(index)}>×</button>
            </div>
          ))}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-container">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={disabled}
            rows={1}
            className="message-textarea"
          />
          
          <div className="input-actions">
            <label className="file-upload-btn">
              📎
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </label>
            
            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className="send-btn"
            >
              Send
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default MessageInput;
