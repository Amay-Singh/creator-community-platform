/**
 * Polish & Verify Agent: Session Persistence Debug Component
 * Real-time monitoring of token persistence and session restoration
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const SessionPersistence = () => {
  const [sessionLogs, setSessionLogs] = useState([]);
  const [tokenInfo, setTokenInfo] = useState({});
  const { user, token, loading } = useAuth();

  const addSessionLog = (type, message, data = null) => {
    const timestamp = new Date().toISOString();
    setSessionLogs(prev => [...prev.slice(-20), { timestamp, type, message, data }]);
    console.log(`🔐 [SESSION] ${type}: ${message}`, data);
  };

  // Monitor localStorage changes
  useEffect(() => {
    const checkTokenInfo = () => {
      if (typeof window !== 'undefined') {
        const storedToken = localStorage.getItem('token');
        const loginTime = localStorage.getItem('loginTime');
        const now = Date.now();
        const threeHours = 3 * 60 * 60 * 1000;
        
        const info = {
          hasStoredToken: !!storedToken,
          tokenLength: storedToken?.length || 0,
          loginTime: loginTime ? (typeof window !== 'undefined' ? new Date(parseInt(loginTime)).toLocaleString() : 'SSR') : 'None',
          timeElapsed: loginTime ? Math.floor((now - parseInt(loginTime)) / 1000 / 60) : 0,
          timeRemaining: loginTime ? Math.floor((threeHours - (now - parseInt(loginTime))) / 1000 / 60) : 0,
          isExpired: loginTime ? (now - parseInt(loginTime)) > threeHours : true
        };
        
        setTokenInfo(info);
        
        if (storedToken && !info.isExpired && !token) {
          addSessionLog('WARNING', 'Token in storage but not in context', info);
        }
      }
    };

    checkTokenInfo();
    const interval = setInterval(checkTokenInfo, 5000);
    return () => clearInterval(interval);
  }, [token]);

  // Monitor auth state changes
  useEffect(() => {
    addSessionLog('STATE', `Auth state changed - User: ${!!user}, Token: ${!!token}, Loading: ${loading}`);
  }, [user, token, loading]);

  // Test session restoration
  const testSessionRestore = () => {
    addSessionLog('TEST', 'Testing session restoration...');
    window.location.reload();
  };

  // Force token refresh
  const forceTokenRefresh = () => {
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        addSessionLog('FORCE', 'Manually syncing token to context');
        // Force page reload to trigger token restoration
        window.location.reload();
      }
    }
  };

  // Emergency token sync
  const emergencyTokenSync = () => {
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token');
      const loginTime = localStorage.getItem('loginTime');
      
      if (storedToken && loginTime) {
        addSessionLog('EMERGENCY', 'Emergency token sync - clearing and restoring');
        // Clear everything and restore
        localStorage.removeItem('token');
        localStorage.removeItem('loginTime');
        
        setTimeout(() => {
          localStorage.setItem('token', storedToken);
          localStorage.setItem('loginTime', loginTime);
          window.location.reload();
        }, 100);
      }
    }
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '10px',
      left: '10px',
      width: '350px',
      height: '400px',
      backgroundColor: '#001122',
      color: '#00ff88',
      fontFamily: 'monospace',
      fontSize: '11px',
      border: '2px solid #00ff88',
      borderRadius: '8px',
      zIndex: 9998,
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{
        padding: '8px',
        borderBottom: '1px solid #00ff88',
        backgroundColor: '#002244'
      }}>
        <h4 style={{ margin: 0 }}>🔐 Session Persistence Monitor</h4>
        <div style={{ fontSize: '9px', marginTop: '3px' }}>
          <div>Token in Storage: {tokenInfo.hasStoredToken ? '✅' : '❌'}</div>
          <div>Token in Context: {token ? '✅' : '❌'}</div>
          <div>Time Remaining: {tokenInfo.timeRemaining}min</div>
        </div>
        <div style={{ display: 'flex', gap: '3px', marginTop: '5px' }}>
          <button
            onClick={testSessionRestore}
            style={{
              padding: '2px 6px',
              backgroundColor: '#0088ff',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              fontSize: '9px'
            }}
          >
            TEST RESTORE
          </button>
          <button
            onClick={forceTokenRefresh}
            style={{
              padding: '2px 6px',
              backgroundColor: '#ff8800',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              fontSize: '9px'
            }}
          >
            FORCE REFRESH
          </button>
          <button
            onClick={emergencyTokenSync}
            style={{
              padding: '2px 6px',
              backgroundColor: '#ff0088',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              fontSize: '9px'
            }}
          >
            EMERGENCY
          </button>
          <button
            onClick={() => setSessionLogs([])}
            style={{
              padding: '2px 6px',
              backgroundColor: '#ff4444',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              fontSize: '9px'
            }}
          >
            CLEAR
          </button>
        </div>
      </div>
      
      <div style={{
        flex: 1,
        padding: '8px',
        overflowY: 'auto',
        lineHeight: '1.2'
      }}>
        {sessionLogs.map((log, index) => (
          <div key={index} style={{ marginBottom: '2px' }}>
            <span style={{ color: '#666' }}>
              {log.timestamp.split('T')[1].split('.')[0]}
            </span>
            <span style={{ 
              color: log.type === 'WARNING' ? '#ffaa00' : 
                     log.type === 'ERROR' ? '#ff4444' : 
                     log.type === 'TEST' ? '#0088ff' : '#00ff88',
              marginLeft: '5px',
              fontWeight: 'bold'
            }}>
              {log.type}:
            </span>
            <span style={{ marginLeft: '5px' }}>
              {log.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SessionPersistence;
