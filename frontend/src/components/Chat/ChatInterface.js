import React, { useState, useEffect, useRef } from 'react';
import clsx from 'clsx';
import Avatar from '../ui/Avatar';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Card from '../ui/Card';

const ChatInterface = ({ threadId, recipientUser }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Mock messages for demonstration
  const mockMessages = [
    {
      id: 1,
      senderId: recipientUser?.id,
      senderName: recipientUser?.name,
      content: "Hey! I love your latest character design. Would you be interested in collaborating on a game project?",
      timestamp: new Date(Date.now() - 300000),
      status: 'delivered'
    },
    {
      id: 2,
      senderId: 'current-user',
      senderName: 'You',
      content: "Thanks! I'd love to hear more about it. What kind of game?",
      timestamp: new Date(Date.now() - 240000),
      status: 'read'
    },
    {
      id: 3,
      senderId: recipientUser?.id,
      senderName: recipientUser?.name,
      content: "It's an indie RPG about time travel. I need character concepts for the main protagonists.",
      timestamp: new Date(Date.now() - 180000),
      status: 'delivered'
    }
  ];

  useEffect(() => {
    setMessages(mockMessages);
  }, [threadId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const message = {
      id: Date.now(),
      senderId: 'current-user',
      senderName: 'You',
      content: newMessage,
      timestamp: new Date(),
      status: 'sending'
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setMessages(prev => 
        prev.map(msg => 
          msg.id === message.id 
            ? { ...msg, status: 'delivered' }
            : msg
        )
      );
    } catch (error) {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === message.id 
            ? { ...msg, status: 'failed' }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(timestamp);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-[var(--spacing-4)] border-b border-[var(--color-neutral-200)]">
        <div className="flex items-center space-x-[var(--spacing-3)]">
          <Avatar 
            src={recipientUser?.avatar} 
            alt={recipientUser?.name}
            size="sm"
          />
          <div>
            <h2 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-neutral-900)]">
              {recipientUser?.name}
            </h2>
            <p className="text-[var(--font-size-sm)] text-[var(--color-neutral-500)]">
              {recipientUser?.isOnline ? 'Online' : 'Last seen 2m ago'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-[var(--spacing-2)]">
          <Button variant="ghost" size="sm" aria-label="Voice call">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </Button>
          <Button variant="ghost" size="sm" aria-label="Video call">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-[var(--spacing-4)] space-y-[var(--spacing-4)]">
        {messages.map((message) => (
          <div
            key={message.id}
            className={clsx(
              'flex',
              message.senderId === 'current-user' ? 'justify-end' : 'justify-start'
            )}
          >
            <div
              className={clsx(
                'max-w-xs lg:max-w-md px-[var(--spacing-4)] py-[var(--spacing-3)] rounded-[var(--radius-lg)]',
                message.senderId === 'current-user'
                  ? 'bg-[var(--color-primary-600)] text-white rounded-br-[var(--radius-sm)]'
                  : 'bg-[var(--color-neutral-100)] text-[var(--color-neutral-900)] rounded-bl-[var(--radius-sm)]'
              )}
            >
              <p className="text-[var(--font-size-base)] leading-relaxed">
                {message.content}
              </p>
              <div className={clsx(
                'flex items-center justify-between mt-[var(--spacing-2)] text-[var(--font-size-xs)]',
                message.senderId === 'current-user' 
                  ? 'text-white/70' 
                  : 'text-[var(--color-neutral-500)]'
              )}>
                <span>{formatTime(message.timestamp)}</span>
                {message.senderId === 'current-user' && (
                  <span className="ml-[var(--spacing-2)]">
                    {message.status === 'sending' && '⏳'}
                    {message.status === 'delivered' && '✓'}
                    {message.status === 'read' && '✓✓'}
                    {message.status === 'failed' && '❌'}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-[var(--color-neutral-100)] px-[var(--spacing-4)] py-[var(--spacing-3)] rounded-[var(--radius-lg)] rounded-bl-[var(--radius-sm)]">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-[var(--color-neutral-400)] rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-[var(--color-neutral-400)] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-[var(--color-neutral-400)] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Composer */}
      <div className="border-t border-[var(--color-neutral-200)] p-[var(--spacing-4)]">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-[var(--spacing-3)]">
          <div className="flex-1">
            <Input
              ref={inputRef}
              placeholder="Type a message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(e);
                }
              }}
            />
          </div>
          
          <div className="flex items-center space-x-[var(--spacing-2)]">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label="Attach file"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </Button>
            
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label="Add emoji"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </Button>
            
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={!newMessage.trim()}
              loading={loading}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
