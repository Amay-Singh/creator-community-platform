import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';

export default function DebugPage() {
  const { user, profile, loading, token } = useAuth();
  const [tokenFromStorage, setTokenFromStorage] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setTokenFromStorage(localStorage.getItem('token'));
    }
  }, []);

  const testLogin = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: 'test@example.com', 
          password: 'testpass123' 
        }),
      });

      const data = await response.json();
      console.log('Login response:', data);
      
      if (data.token) {
        localStorage.setItem('token', data.token);
        window.location.reload();
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  const clearStorage = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  return (
    <div style={{padding: '2rem', fontFamily: 'monospace'}}>
      <h1>Debug Session State</h1>
      
      <div style={{marginBottom: '2rem'}}>
        <h2>Current State:</h2>
        <p><strong>Loading:</strong> {loading ? 'true' : 'false'}</p>
        <p><strong>User:</strong> {user ? `${user.email} (${user.id})` : 'NULL'}</p>
        <p><strong>Profile:</strong> {profile ? `${profile.user_email} (ID: ${profile.id})` : 'NULL'}</p>
        <p><strong>Token in Context:</strong> {token ? 'Present' : 'NULL'}</p>
        <p><strong>Token in localStorage:</strong> {tokenFromStorage || 'NULL'}</p>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <button 
          onClick={testLogin}
          style={{padding: '0.5rem 1rem', marginRight: '1rem', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px'}}
        >
          Test Login
        </button>
        <button 
          onClick={clearStorage}
          style={{padding: '0.5rem 1rem', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px'}}
        >
          Clear Storage
        </button>
      </div>

      <div>
        <h2>Navigation:</h2>
        <a href="/dashboard" style={{color: '#007bff', textDecoration: 'underline'}}>Go to Dashboard</a>
      </div>
    </div>
  );
}
