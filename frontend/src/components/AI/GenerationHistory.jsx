/**
 * Generation History Component - Guardian Agent Validated
 * Displays AI content generation history
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const GenerationHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user]);

  const loadHistory = async () => {
    try {
      // Mock data for demo - replace with actual API call
      setHistory([
        {
          id: 1,
          type: 'music',
          prompt: 'Create a pop song about summer',
          result: 'Generated lyrics for summer pop song',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          type: 'artwork',
          prompt: 'Abstract digital art',
          result: 'Created abstract digital artwork concept',
          created_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Failed to load generation history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading history...</div>;
  }

  return (
    <div className="generation-history">
      <h3>Generation History</h3>
      {history.length === 0 ? (
        <p>No generation history yet.</p>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.id} className="history-item">
              <div className="item-header">
                <span className="item-type">{item.type}</span>
                <span className="item-date">
                  {typeof window !== 'undefined' ? new Date(item.created_at).toLocaleDateString() : 'Loading...'}
                </span>
              </div>
              <div className="item-prompt">{item.prompt}</div>
              <div className="item-result">{item.result}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GenerationHistory;
