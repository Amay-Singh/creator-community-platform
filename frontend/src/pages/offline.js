import { useState, useEffect } from 'react';
import Head from 'next/head';
import { WifiIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    setIsOnline(navigator.onLine);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    if (isOnline) {
      window.location.reload();
    }
  };

  return (
    <>
      <Head>
        <title>Offline - Creator Community Platform</title>
        <meta name="description" content="You are currently offline" />
      </Head>
      
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="flex justify-center">
            <WifiIcon className={`h-16 w-16 ${isOnline ? 'text-green-500' : 'text-gray-400'}`} />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isOnline ? 'Connection Restored' : 'You\'re Offline'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {isOnline 
              ? 'Your internet connection has been restored. You can now continue using the platform.'
              : 'It looks like you\'re not connected to the internet. Some features may be limited.'
            }
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="space-y-6">
              {/* Connection Status */}
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Status:</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  isOnline 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {isOnline ? 'Online' : 'Offline'}
                </span>
              </div>

              {/* Retry Button */}
              <button
                onClick={handleRetry}
                disabled={!isOnline && retryCount > 3}
                className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                  isOnline
                    ? 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
                    : retryCount > 3
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gray-600 hover:bg-gray-700 focus:ring-gray-500'
                } focus:outline-none focus:ring-2 focus:ring-offset-2`}
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                {isOnline ? 'Return to App' : `Retry Connection ${retryCount > 0 ? `(${retryCount})` : ''}`}
              </button>

              {retryCount > 3 && !isOnline && (
                <p className="text-xs text-gray-500 text-center">
                  Too many retry attempts. Please check your internet connection and refresh the page manually.
                </p>
              )}

              {/* Offline Features */}
              {!isOnline && (
                <div className="mt-6 border-t border-gray-200 pt-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">
                    Available Offline Features:
                  </h3>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li className="flex items-center">
                      <span className="h-1.5 w-1.5 bg-green-400 rounded-full mr-2"></span>
                      View cached notifications
                    </li>
                    <li className="flex items-center">
                      <span className="h-1.5 w-1.5 bg-green-400 rounded-full mr-2"></span>
                      Browse saved matches
                    </li>
                    <li className="flex items-center">
                      <span className="h-1.5 w-1.5 bg-green-400 rounded-full mr-2"></span>
                      Read collaboration invites
                    </li>
                    <li className="flex items-center">
                      <span className="h-1.5 w-1.5 bg-yellow-400 rounded-full mr-2"></span>
                      Limited profile editing
                    </li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3">
                    Changes made offline will sync when you reconnect.
                  </p>
                </div>
              )}

              {/* Tips */}
              <div className="mt-6 border-t border-gray-200 pt-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3">
                  Tips:
                </h3>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Check your Wi-Fi or mobile data connection</li>
                  <li>• Try moving to an area with better signal</li>
                  <li>• Restart your router if using Wi-Fi</li>
                  <li>• Contact your internet service provider if issues persist</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Install App Prompt */}
        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Install the App
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    Install our app for better offline experience and faster access to your content.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
