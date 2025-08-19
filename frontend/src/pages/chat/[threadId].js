import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useAuth } from '../../contexts/AuthContext';
import ChatInterface from '../../components/chat/ChatInterface';

export default function ChatThread() {
  const router = useRouter();
  const { threadId } = router.query;
  const { user } = useAuth();
  const [recipientUser, setRecipientUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock recipient data
  const mockRecipient = {
    id: 2,
    name: 'Alex Chen',
    username: 'alexcreates',
    avatar: null,
    isOnline: true
  };

  useEffect(() => {
    if (threadId) {
      // Simulate API call to get thread details
      setTimeout(() => {
        setRecipientUser(mockRecipient);
        setLoading(false);
      }, 500);
    }
  }, [threadId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-neutral-50)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary-600)]" />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{recipientUser ? `Chat with ${recipientUser.name}` : 'Chat'} - Creator Community Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="h-screen flex flex-col">
        <ChatInterface 
          threadId={threadId}
          recipientUser={recipientUser}
        />
      </div>
    </>
  );
}
