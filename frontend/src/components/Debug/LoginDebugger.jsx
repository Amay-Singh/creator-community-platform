/**
 * Polish & Verify Agent: Enhanced Login Debugger
 * Captures and logs all login errors with detailed stack traces
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const LoginDebugger = () => {
  const [email, setEmail] = useState('amaysingh@outlook.com');
  const [password, setPassword] = useState('amay@123');
  const [debugLogs, setDebugLogs] = useState([]);
  const { login } = useAuth();

  const addLog = (type, message, data = null) => {
    const timestamp = new Date().toISOString();
    setDebugLogs(prev => [...prev, { timestamp, type, message, data }]);
    console.log(`🔍 [${type}] ${message}`, data);
  };

  const testLogin = async () => {
    setDebugLogs([]);
    addLog('INFO', 'Starting login test...');
    
    try {
      // Test 1: Direct API call
      addLog('TEST', 'Testing direct API call...');
      const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      addLog('API', `Response status: ${response.status}`);
      const data = await response.json();
      addLog('API', 'Response data:', data);
      
      if (response.ok) {
        addLog('SUCCESS', 'Direct API call successful');
        
        // Test 2: AuthContext login
        addLog('TEST', 'Testing AuthContext login...');
        await login(email, password);
        addLog('SUCCESS', 'AuthContext login successful');
      } else {
        addLog('ERROR', 'API call failed', data);
      }
    } catch (error) {
      addLog('ERROR', 'Login test failed', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace', backgroundColor: '#f8f9fa' }}>
      <h2>🔍 Login Debugger (Polish & Verify Agent)</h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          style={{ marginRight: '1rem', padding: '0.5rem' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          style={{ marginRight: '1rem', padding: '0.5rem' }}
        />
        <button
          onClick={testLogin}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px'
          }}
        >
          Test Login
        </button>
      </div>

      <div style={{ 
        maxHeight: '400px', 
        overflow: 'auto', 
        backgroundColor: '#000', 
        color: '#00ff00', 
        padding: '1rem',
        borderRadius: '4px'
      }}>
        <h3>Debug Logs:</h3>
        {debugLogs.map((log, index) => (
          <div key={index} style={{ marginBottom: '0.5rem' }}>
            <strong>[{log.timestamp.split('T')[1].split('.')[0]}] {log.type}:</strong> {log.message}
            {log.data && (
              <pre style={{ marginLeft: '1rem', fontSize: '0.8em' }}>
                {JSON.stringify(log.data, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoginDebugger;
