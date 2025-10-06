import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import Button from './Button';
import Input from './Input';

/**
 * Chat Interface Component - ReqDoc02 Phase 5
 * Features: Real-time messaging, file sharing, emoji reactions
 */
const ChatInterface = ({ 
  currentUser,
  conversations = [],
  activeConversation,
  onSendMessage,
  onSelectConversation,
  onStartCall,
  onFileUpload
}) => {
  const [message, setMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const newMessage = {
      id: `msg-${Date.now()}`,
      content: message,
      sender: currentUser,
      timestamp: new Date().toISOString(),
      type: 'text'
    };

    onSendMessage?.(newMessage, activeConversation?.id);
    setMessage('');
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      const fileMessage = {
        id: `msg-${Date.now()}-${Math.random()}`,
        content: file.name,
        sender: currentUser,
        timestamp: new Date().toISOString(),
        type: 'file',
        file: file,
        fileUrl: URL.createObjectURL(file)
      };
      onSendMessage?.(fileMessage, activeConversation?.id);
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const MessageBubble = ({ message, isOwn }) => (
    <motion.div
      className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={`flex items-end space-x-2 max-w-xs lg:max-w-md ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {!isOwn && (
          <img
            src={message.sender.avatar || '/default-avatar.png'}
            alt={message.sender.name}
            className="w-8 h-8 rounded-full"
          />
        )}
        
        <div className={`relative px-4 py-3 rounded-2xl ${
          isOwn 
            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
            : 'bg-white/20 backdrop-blur-md text-gray-900'
        }`}>
          {message.type === 'text' && (
            <p className="text-sm">{message.content}</p>
          )}
          
          {message.type === 'file' && (
            <div className="flex items-center space-x-3">
              {message.file?.type?.startsWith('image/') ? (
                <img
                  src={message.fileUrl}
                  alt={message.content}
                  className="max-w-48 max-h-32 rounded-lg object-cover"
                />
              ) : (
                <div className="flex items-center space-x-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm">{message.content}</span>
                </div>
              )}
            </div>
          )}
          
          <div className={`text-xs mt-1 ${isOwn ? 'text-blue-100' : 'text-gray-500'}`}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    </motion.div>
  );

  const ConversationItem = ({ conversation, isActive }) => (
    <motion.div
      className={`p-4 cursor-pointer transition-all duration-300 ${
        isActive 
          ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-r-2 border-blue-500' 
          : 'hover:bg-white/10'
      }`}
      onClick={() => onSelectConversation?.(conversation)}
      whileHover={{ x: 5 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-center space-x-3">
        <div className="relative">
          <img
            src={conversation.avatar || '/default-avatar.png'}
            alt={conversation.name}
            className="w-12 h-12 rounded-full object-cover"
          />
          {conversation.isOnline && (
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-gray-900 truncate">{conversation.name}</h4>
            {conversation.lastMessage && (
              <span className="text-xs text-gray-500">
                {formatTime(conversation.lastMessage.timestamp)}
              </span>
            )}
          </div>
          
          {conversation.lastMessage && (
            <p className="text-sm text-gray-600 truncate">
              {conversation.lastMessage.type === 'file' ? '📎 File' : conversation.lastMessage.content}
            </p>
          )}
          
          {conversation.unreadCount > 0 && (
            <div className="mt-1">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-600 text-white">
                {conversation.unreadCount}
              </span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="flex h-full bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Conversations Sidebar */}
      <div className="w-80 bg-white/10 backdrop-blur-md border-r border-white/20">
        <div className="p-6 border-b border-white/20">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Messages
          </h2>
        </div>
        
        <div className="overflow-y-auto h-full">
          {conversations.map((conversation, index) => (
            <motion.div
              key={conversation.id}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <ConversationItem
                conversation={conversation}
                isActive={activeConversation?.id === conversation.id}
              />
            </motion.div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <motion.div 
              className="p-6 bg-white/10 backdrop-blur-md border-b border-white/20"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <img
                    src={activeConversation.avatar || '/default-avatar.png'}
                    alt={activeConversation.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <h3 className="font-semibold text-gray-900">{activeConversation.name}</h3>
                    <p className="text-sm text-gray-600">
                      {activeConversation.isOnline ? 'Online' : 'Last seen recently'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" onClick={() => onStartCall?.('video')}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onStartCall?.('audio')}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </Button>
                </div>
              </div>
            </motion.div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {activeConversation.messages?.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    isOwn={msg.sender.id === currentUser?.id}
                  />
                ))}
              </AnimatePresence>
              
              {isTyping && (
                <motion.div
                  className="flex justify-start"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="bg-white/20 backdrop-blur-md rounded-2xl px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <motion.div 
              className="p-6 bg-white/10 backdrop-blur-md border-t border-white/20"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <form onSubmit={handleSendMessage} className="flex items-end space-x-4">
                <div className="flex-1">
                  <Input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="resize-none"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </Button>
                  
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    disabled={!message.trim()}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </Button>
                </div>
              </form>
            </motion.div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <motion.div 
              className="text-center"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a conversation</h3>
              <p className="text-gray-600">Choose a conversation from the sidebar to start messaging</p>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
