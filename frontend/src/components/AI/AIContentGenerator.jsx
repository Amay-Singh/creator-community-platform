/**
 * AI Content Generator Component
 * Implements REQ-13, REQ-15: AI content generation and portfolio generator
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import GenerationHistory from './GenerationHistory';
import PortfolioGenerator from './PortfolioGenerator';
import styles from './AIContentGenerator.module.css';

const AIContentGenerator = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('generate');
  const [generationType, setGenerationType] = useState('music');
  const [prompt, setPrompt] = useState('');
  const [parameters, setParameters] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const [generationHistory, setGenerationHistory] = useState([]);

  useEffect(() => {
    loadGenerationHistory();
  }, []);

  const loadGenerationHistory = async () => {
    try {
      const response = await fetch('/api/ai_services/generation-history/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setGenerationHistory(data.history || []);
      }
    } catch (error) {
      console.error('Failed to load generation history:', error);
    }
  };

  const generateContent = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setGenerationResult(null);

    try {
      const response = await fetch('/api/ai_services/generate/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          generation_type: generationType,
          prompt: prompt.trim(),
          parameters
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGenerationResult(data);
        loadGenerationHistory(); // Refresh history
      } else {
        const error = await response.json();
        setGenerationResult({
          success: false,
          error: error.error || 'Generation failed'
        });
      }
    } catch (error) {
      setGenerationResult({
        success: false,
        error: 'Network error occurred'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const regenerateContent = async (generationId) => {
    setIsGenerating(true);
    
    try {
      const response = await fetch(`/api/ai_services/generations/${generationId}/regenerate/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setGenerationResult(data);
        loadGenerationHistory();
      }
    } catch (error) {
      console.error('Failed to regenerate content:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getGenerationTypeConfig = () => {
    const configs = {
      music: {
        title: 'Music Composition',
        icon: '🎵',
        placeholder: 'Describe the music you want to create (genre, mood, instruments, etc.)',
        examples: [
          'A melancholic piano ballad in D minor',
          'Upbeat electronic dance track with synthesizers',
          'Acoustic folk song with storytelling lyrics'
        ]
      },
      artwork: {
        title: 'Visual Artwork',
        icon: '🎨',
        placeholder: 'Describe the artwork you want to create (style, subject, colors, etc.)',
        examples: [
          'Abstract painting with warm colors and flowing shapes',
          'Digital illustration of a futuristic cityscape',
          'Minimalist logo design for a tech startup'
        ]
      },
      story: {
        title: 'Story & Narrative',
        icon: '📖',
        placeholder: 'Describe the story you want to create (genre, characters, setting, etc.)',
        examples: [
          'A sci-fi short story about time travel',
          'Mystery novel set in Victorian London',
          'Coming-of-age story about a young artist'
        ]
      }
    };
    
    return configs[generationType] || configs.music;
  };

  const config = getGenerationTypeConfig();

  return (
    <div className={styles.aiContentGenerator}>
      {/* Tab Navigation */}
      <div className={styles.tabNavigation}>
        <button 
          className={`${styles.tabButton} ${activeTab === 'generate' ? styles.active : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          🤖 Generate Content
        </button>
        <button 
          className={`${styles.tabButton} ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
        >
          📁 Portfolio Generator
        </button>
        <button 
          className={`${styles.tabButton} ${activeTab === 'history' ? styles.active : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📚 History
        </button>
      </div>

      {/* Content Generation Tab */}
      {activeTab === 'generate' && (
        <div className="generation-panel">
          <div className="generator-header">
            <h2>{config.icon} {config.title}</h2>
            <p>Use AI to generate creative content and ideas</p>
          </div>

          {/* Generation Type Selector */}
          <div className="type-selector">
            {['music', 'artwork', 'story'].map(type => (
              <button
                key={type}
                className={`type-btn ${generationType === type ? 'active' : ''}`}
                onClick={() => setGenerationType(type)}
              >
                {type === 'music' && '🎵 Music'}
                {type === 'artwork' && '🎨 Artwork'}
                {type === 'story' && '📖 Story'}
              </button>
            ))}
          </div>

          {/* Prompt Input */}
          <div className="prompt-section">
            <label htmlFor="prompt">Describe what you want to create:</label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={config.placeholder}
              rows={4}
              disabled={isGenerating}
            />
            
            {/* Example Prompts */}
            <div className="examples">
              <p>Examples:</p>
              <div className="example-chips">
                {config.examples.map((example, index) => (
                  <button
                    key={index}
                    className="example-chip"
                    onClick={() => setPrompt(example)}
                    disabled={isGenerating}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            className="generate-btn"
            onClick={generateContent}
            disabled={!prompt.trim() || isGenerating}
          >
            {isGenerating ? (
              <>
                <div className="btn-spinner"></div>
                Generating...
              </>
            ) : (
              <>
                ✨ Generate {config.title}
              </>
            )}
          </button>

          {/* Generation Result */}
          {generationResult && (
            <div className="generation-result">
              {generationResult.success ? (
                <div className="result-success">
                  <div className="result-header">
                    <h3>✅ Generated Successfully!</h3>
                    <div className="result-meta">
                      <span className="quality-score">
                        Quality: {Math.round(generationResult.quality_score * 100)}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="result-content">
                    <pre>{generationResult.generated_content}</pre>
                  </div>
                  
                  <div className="result-actions">
                    <button 
                      className="action-btn secondary"
                      onClick={() => regenerateContent(generationResult.generation_id)}
                      disabled={isGenerating}
                    >
                      🔄 Regenerate
                    </button>
                    <button className="action-btn primary">
                      💾 Save to Portfolio
                    </button>
                    <button className="action-btn">
                      📋 Copy
                    </button>
                  </div>
                </div>
              ) : (
                <div className="result-error">
                  <h3>❌ Generation Failed</h3>
                  <p>{generationResult.error}</p>
                  <button 
                    className="action-btn"
                    onClick={generateContent}
                  >
                    🔄 Try Again
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Portfolio Generator Tab */}
      {activeTab === 'portfolio' && (
        <PortfolioGenerator onGenerate={loadGenerationHistory} />
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <GenerationHistory 
          history={generationHistory}
          onRegenerate={regenerateContent}
          onRefresh={loadGenerationHistory}
        />
      )}
    </div>
  );
};

export default AIContentGenerator;
