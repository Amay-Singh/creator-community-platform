import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import Button from '../src/components/ui/Button';
import Card from '../src/components/ui/Card';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    fetch('https://creator-platform-backend-vfuz.onrender.com/api/healthz')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setBackendStatus('connected');
        } else {
          setBackendStatus('error');
        }
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-blue-300/10 to-purple-300/10 rounded-full blur-3xl animate-spin" style={{ animationDuration: '20s' }} />
      </div>

      {/* Header */}
      <motion.header 
        className="relative z-10 backdrop-blur-md bg-white/10 border-b border-white/20"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <motion.div 
              className="flex items-center space-x-3"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Creator Community Platform
              </h1>
            </motion.div>
            
            <div className="flex items-center space-x-6">
              <motion.div 
                className="flex items-center space-x-2"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 300 }}
              >
                <div className={`w-3 h-3 rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-500' : 
                  backendStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'
                } shadow-lg`}></div>
                <span className="text-sm font-medium text-gray-700">
                  {backendStatus === 'connected' ? 'Online' : 
                   backendStatus === 'checking' ? 'Connecting...' : 'Offline'}
                </span>
              </motion.div>
              
              <div className="flex space-x-3">
                <Link href="/login">
                  <Button variant="ghost" size="md">Login</Button>
                </Link>
                <Link href="/register">
                  <Button variant="primary" size="md">Sign Up</Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <main className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 py-20">
          <motion.div 
            className="text-center mb-16"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <motion.h1 
              className="text-6xl md:text-7xl font-bold mb-6 leading-tight"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1, delay: 0.4 }}
            >
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Connect.
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent">
                Create.
              </span>
              <br />
              <span className="bg-gradient-to-r from-pink-600 via-orange-500 to-yellow-500 bg-clip-text text-transparent">
                Collaborate.
              </span>
            </motion.h1>
            
            <motion.p 
              className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto mb-12 leading-relaxed"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              Join the world's most advanced creator community platform. Connect with like-minded creators, 
              discover collaboration opportunities, and build amazing projects together with AI-powered matching.
            </motion.p>

            <motion.div 
              className="flex flex-col sm:flex-row gap-6 justify-center items-center"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.8 }}
            >
              <Link href="/register">
                <Button variant="primary" size="xl" className="min-w-[200px]">
                  Start Creating Today
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="glass" size="xl" className="min-w-[200px]">
                  Sign In
                </Button>
              </Link>
            </motion.div>
          </motion.div>

          {/* Status Card */}
          {backendStatus === 'connected' && (
            <motion.div 
              className="max-w-md mx-auto mb-16"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 1 }}
            >
              <Card variant="glass" className="text-center">
                <div className="flex items-center justify-center space-x-3">
                  <div className="w-4 h-4 bg-green-500 rounded-full shadow-lg animate-pulse"></div>
                  <span className="text-green-800 font-semibold">All systems operational</span>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Features */}
          <motion.div 
            className="grid md:grid-cols-3 gap-8 mb-16"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <Card variant="glass" hover={true}>
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <Card.Title>AI Creator Matching</Card.Title>
              <Card.Content>
                AI-powered matching system connects you with compatible creators for collaboration using advanced algorithms
              </Card.Content>
            </Card>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Tools</h3>
            <p className="text-gray-600">Advanced AI tools for content generation, portfolio optimization, and creative assistance</p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Global Community</h3>
            <p className="text-gray-600">Connect with creators worldwide across all creative disciplines and experience levels</p>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-lg p-8 shadow-sm border">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">Platform Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-gray-600">Active Creators</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600 mb-2">50,000+</div>
              <div className="text-gray-600">Collaborations</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">100+</div>
              <div className="text-gray-600">Countries</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Support</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xs">C</span>
            </div>
            <span className="text-lg font-semibold">Creator Community Platform</span>
          </div>
          <p className="text-gray-400">
            Empowering creators worldwide to connect, collaborate, and create amazing things together.
          </p>
        </div>
      </footer>
    </div>
  );
}
