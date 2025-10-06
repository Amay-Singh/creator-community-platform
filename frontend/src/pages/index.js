import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { CheckCircleIcon, UserGroupIcon, SparklesIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const router = useRouter();
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    // Check backend status
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

  const features = [
    {
      icon: UserGroupIcon,
      title: 'Creator Matching',
      description: 'AI-powered matching system connects you with compatible creators for collaboration'
    },
    {
      icon: SparklesIcon,
      title: 'AI-Powered Tools',
      description: 'Advanced AI tools for content generation, portfolio optimization, and creative assistance'
    },
    {
      icon: GlobeAltIcon,
      title: 'Global Community',
      description: 'Connect with creators worldwide across all creative disciplines and experience levels'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Creator Community Platform
              </h1>
            </div>
            
            {/* Backend Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-500' : 
                  backendStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  Backend: {backendStatus === 'connected' ? 'Online' : 
                           backendStatus === 'checking' ? 'Checking...' : 'Offline'}
                </span>
              </div>
              
              <div className="flex space-x-3">
                <Link 
                  href="/login" 
                  className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  Login
                </Link>
                <Link 
                  href="/register" 
                  className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
            Connect. Create. 
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {" "}Collaborate.
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            Join the world's most advanced creator community platform. Connect with like-minded creators, 
            discover collaboration opportunities, and build amazing projects together with AI-powered tools.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link 
              href="/register" 
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
            >
              Start Creating Today
            </Link>
            <Link 
              href="/search" 
              className="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:border-blue-500 hover:text-blue-600 transition-all duration-200"
            >
              Explore Creators
            </Link>
          </div>

          {/* Backend Status Card */}
          {backendStatus === 'connected' && (
            <div className="inline-flex items-center space-x-2 bg-green-50 border border-green-200 rounded-lg px-4 py-2 mb-16">
              <CheckCircleIcon className="w-5 h-5 text-green-600" />
              <span className="text-green-800 font-medium">All systems operational</span>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-200 border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mb-6">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-20 bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
          <div className="grid md:grid-cols-4 gap-8 text-center">
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
      <footer className="bg-gray-900 text-white py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">Creator Community Platform</span>
          </div>
          <p className="text-gray-400">
            Empowering creators worldwide to connect, collaborate, and create amazing things together.
          </p>
        </div>
      </footer>
    </div>
  );
}
