import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import Button from './Button';
import Input from './Input';

/**
 * AI Studio Component - ReqDoc02 Phase 6
 * Features: Content generation, AI tools, creative assistance
 */
const AIStudio = ({ onGenerateContent, onSaveContent }) => {
  const [activeTab, setActiveTab] = useState('text');
  const [prompt, setPrompt] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [contentHistory, setContentHistory] = useState([]);

  const aiTools = [
    {
      id: 'text',
      name: 'Text Generator',
      icon: '📝',
      description: 'Generate articles, captions, and creative writing',
      color: 'from-blue-500 to-purple-500'
    },
    {
      id: 'image',
      name: 'Image Prompts',
      icon: '🎨',
      description: 'Create detailed prompts for AI image generation',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'video',
      name: 'Video Scripts',
      icon: '🎬',
      description: 'Generate video scripts and storyboards',
      color: 'from-pink-500 to-red-500'
    },
    {
      id: 'social',
      name: 'Social Media',
      icon: '📱',
      description: 'Create engaging social media content',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'music',
      name: 'Music Ideas',
      icon: '🎵',
      description: 'Generate lyrics and music concepts',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      id: 'code',
      name: 'Code Helper',
      icon: '💻',
      description: 'Generate code snippets and documentation',
      color: 'from-indigo-500 to-blue-500'
    }
  ];

  const templates = {
    text: [
      'Blog post about [topic]',
      'Product description for [product]',
      'Email newsletter about [subject]',
      'Creative story beginning with [scenario]'
    ],
    image: [
      'Portrait of [subject] in [style]',
      'Landscape showing [scene] with [mood]',
      'Abstract representation of [concept]',
      'Product photo of [item] with [lighting]'
    ],
    video: [
      '30-second commercial for [product]',
      'Tutorial video about [topic]',
      'Behind-the-scenes of [process]',
      'Interview questions for [guest]'
    ],
    social: [
      'Instagram caption for [post type]',
      'Twitter thread about [topic]',
      'LinkedIn post about [achievement]',
      'TikTok video idea for [niche]'
    ]
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    
    // Simulate AI generation
    setTimeout(() => {
      const mockContent = generateMockContent(activeTab, prompt);
      setGeneratedContent(mockContent);
      
      const newContent = {
        id: `content-${Date.now()}`,
        type: activeTab,
        prompt: prompt,
        content: mockContent,
        timestamp: new Date().toISOString()
      };
      
      setContentHistory(prev => [newContent, ...prev.slice(0, 9)]);
      setIsGenerating(false);
      onGenerateContent?.(newContent);
    }, 2000);
  };

  const generateMockContent = (type, prompt) => {
    const mockResponses = {
      text: `Here's a creative response to "${prompt}":\n\nThis is where AI-generated text content would appear. The system would analyze your prompt and create engaging, relevant content tailored to your specific needs. The content would be original, well-structured, and ready to use in your projects.`,
      image: `AI Image Prompt for "${prompt}":\n\nA highly detailed, photorealistic image featuring ${prompt}. Shot with professional lighting, sharp focus, vibrant colors, and artistic composition. Style: modern, clean, visually striking. Camera: DSLR, 85mm lens, f/1.8 aperture. Mood: inspiring and creative.`,
      video: `Video Script for "${prompt}":\n\n[INTRO - 0:00-0:05]\nHook: Attention-grabbing opening\n\n[MAIN CONTENT - 0:05-0:25]\nKey points about ${prompt}\n\n[CALL TO ACTION - 0:25-0:30]\nEngage with audience\n\nVisual notes: Dynamic shots, smooth transitions, engaging graphics.`,
      social: `Social Media Content for "${prompt}":\n\n🚀 ${prompt} is changing the game!\n\nHere's why this matters:\n✨ Point 1\n💡 Point 2\n🎯 Point 3\n\nWhat do you think? Drop your thoughts below! 👇\n\n#CreativeContent #Innovation #Community`
    };
    
    return mockResponses[type] || 'AI-generated content would appear here.';
  };

  const ToolCard = ({ tool, isActive }) => (
    <motion.div
      className={`cursor-pointer transition-all duration-300 ${
        isActive ? 'scale-105' : 'hover:scale-102'
      }`}
      onClick={() => setActiveTab(tool.id)}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        variant={isActive ? "gradient" : "glass"} 
        className={`p-6 text-center ${isActive ? 'ring-2 ring-blue-500' : ''}`}
      >
        <div className={`w-16 h-16 bg-gradient-to-br ${tool.color} rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
          <span className="text-2xl">{tool.icon}</span>
        </div>
        <h3 className="font-bold text-gray-900 mb-2">{tool.name}</h3>
        <p className="text-sm text-gray-600">{tool.description}</p>
      </Card>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div 
          className="text-center mb-8"
          initial={{ y: -30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Creative Studio
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Unleash your creativity with AI-powered content generation. From text to visuals, let AI be your creative partner.
          </p>
        </motion.div>

        {/* AI Tools Grid */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {aiTools.map((tool, index) => (
            <motion.div
              key={tool.id}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 * index }}
            >
              <ToolCard tool={tool} isActive={activeTab === tool.id} />
            </motion.div>
          ))}
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Content Generation */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ x: -30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Card variant="glass" className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <span className="text-3xl mr-3">{aiTools.find(t => t.id === activeTab)?.icon}</span>
                  {aiTools.find(t => t.id === activeTab)?.name}
                </h2>

                {/* Templates */}
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Quick Templates:</h3>
                  <div className="flex flex-wrap gap-2">
                    {templates[activeTab]?.map((template, index) => (
                      <motion.button
                        key={index}
                        className="px-3 py-2 bg-white/20 hover:bg-white/30 text-gray-700 rounded-full text-sm transition-all duration-300"
                        onClick={() => setPrompt(template)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        {template}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Prompt Input */}
                <div className="mb-6">
                  <Input
                    label="Your Creative Prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={`Describe what you want to create with ${aiTools.find(t => t.id === activeTab)?.name.toLowerCase()}...`}
                    className="min-h-[100px]"
                  />
                </div>

                <div className="flex space-x-4 mb-6">
                  <Button
                    variant="primary"
                    onClick={handleGenerate}
                    disabled={!prompt.trim() || isGenerating}
                    loading={isGenerating}
                    className="flex-1"
                  >
                    {isGenerating ? 'Generating...' : 'Generate Content'}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setPrompt('');
                      setGeneratedContent('');
                    }}
                  >
                    Clear
                  </Button>
                </div>

                {/* Generated Content */}
                <AnimatePresence>
                  {generatedContent && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.5 }}
                    >
                      <Card variant="default" className="p-6 bg-gradient-to-br from-blue-50 to-purple-50">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-semibold text-gray-900">Generated Content</h3>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onSaveContent?.(generatedContent)}
                          >
                            Save
                          </Button>
                        </div>
                        <div className="bg-white/50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap">
                          {generatedContent}
                        </div>
                      </Card>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            </motion.div>
          </div>

          {/* Content History */}
          <div>
            <motion.div
              initial={{ x: 30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <Card variant="glass" className="p-6">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Recent Generations
                </h3>
                
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {contentHistory.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <p className="text-sm">No content generated yet</p>
                    </div>
                  ) : (
                    contentHistory.map((item, index) => (
                      <motion.div
                        key={item.id}
                        className="p-3 bg-white/20 rounded-lg cursor-pointer hover:bg-white/30 transition-colors"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        onClick={() => setGeneratedContent(item.content)}
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-lg">{aiTools.find(t => t.id === item.type)?.icon}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 truncate">{item.prompt}</p>
                      </motion.div>
                    ))
                  )}
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIStudio;
