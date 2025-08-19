/**
 * Translation Panel Component - Guardian Agent Validated
 * Implements REQ-11: Real-time translation
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const TranslationPanel = ({ message, onTranslate }) => {
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [translating, setTranslating] = useState(false);
  const { user } = useAuth();

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'zh', name: 'Chinese' }
  ];

  const handleTranslate = async () => {
    if (!message || translating) return;
    
    setTranslating(true);
    try {
      // Mock translation - replace with actual API call
      const translatedText = `[Translated to ${targetLanguage}] ${message}`;
      onTranslate(translatedText, targetLanguage);
    } catch (error) {
      console.error('Translation failed:', error);
    } finally {
      setTranslating(false);
    }
  };

  return (
    <div className="translation-panel">
      <div className="translation-controls">
        <select 
          value={targetLanguage} 
          onChange={(e) => setTargetLanguage(e.target.value)}
          className="language-select"
        >
          {languages.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
        
        <button 
          onClick={handleTranslate}
          disabled={translating || !message}
          className="translate-btn"
        >
          {translating ? 'Translating...' : 'Translate'}
        </button>
      </div>
    </div>
  );
};

export default TranslationPanel;
