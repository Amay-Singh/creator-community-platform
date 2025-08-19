/**
 * 4-Agent Live Monitoring System
 * Continuously monitors login attempts and auto-fixes errors
 */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const LiveMonitor = () => {
  const [logs, setLogs] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [errorCount, setErrorCount] = useState(0);
  const [autoFixCount, setAutoFixCount] = useState(0);
  const logsRef = useRef(null);
  const { user, profile, loading, token } = useAuth();

  const addLog = (agent, type, message, data = null) => {
    const timestamp = new Date().toISOString();
    const logEntry = { timestamp, agent, type, message, data };
    
    setLogs(prev => {
      const newLogs = [...prev, logEntry];
      // Keep only last 100 logs
      return newLogs.slice(-100);
    });
    
    console.log(`🤖 [${agent}] ${type}: ${message}`, data);
    
    // Auto-scroll to bottom
    setTimeout(() => {
      if (logsRef.current) {
        logsRef.current.scrollTop = logsRef.current.scrollHeight;
      }
    }, 100);
  };

  // Orchestrator Agent - Monitor auth state changes
  useEffect(() => {
    addLog('ORCHESTRATOR', 'STATE', `Auth state - User: ${!!user}, Profile: ${!!profile}, Loading: ${loading}, Token: ${!!token}`);
  }, [user, profile, loading, token]);

  // CodeSync Agent - Monitor network errors
  useEffect(() => {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      try {
        addLog('CODESYNC', 'NETWORK', `API call: ${args[0]}`);
        const response = await originalFetch(...args);
        
        if (!response.ok) {
          addLog('CODESYNC', 'ERROR', `API error ${response.status}: ${args[0]}`);
          setErrorCount(prev => prev + 1);
          
          // Auto-fix: Retry with credentials if CORS error
          if (response.status === 0 || response.status === 500) {
            addLog('CODESYNC', 'AUTOFIX', 'Retrying with credentials...');
            const retryResponse = await originalFetch(args[0], {
              ...args[1],
              credentials: 'include'
            });
            setAutoFixCount(prev => prev + 1);
            return retryResponse;
          }
        } else {
          addLog('CODESYNC', 'SUCCESS', `API success: ${args[0]}`);
        }
        
        return response;
      } catch (error) {
        addLog('CODESYNC', 'ERROR', `Network error: ${error.message}`, error);
        setErrorCount(prev => prev + 1);
        throw error;
      }
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  // Polish & Verify Agent - Monitor console errors
  useEffect(() => {
    const originalError = console.error;
    console.error = (...args) => {
      addLog('POLISH', 'ERROR', 'Console error detected', args);
      setErrorCount(prev => prev + 1);
      
      // Log auth errors but don't auto-clear
      if (args[0]?.includes?.('auth') || args[0]?.includes?.('token')) {
        addLog('POLISH', 'DETECTED', 'Auth error detected - check manually');
      }
      
      originalError(...args);
    };

    return () => {
      console.error = originalError;
    };
  }, []);

  // Guardian Agent - Monitor React errors
  useEffect(() => {
    const handleError = (event) => {
      addLog('GUARDIAN', 'ERROR', 'React error detected', {
        message: event.error?.message,
        stack: event.error?.stack
      });
      setErrorCount(prev => prev + 1);
      
      // Log error but don't auto-reload
      addLog('GUARDIAN', 'DETECTED', 'React error logged - manual fix required');
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  // Start monitoring
  useEffect(() => {
    if (isMonitoring) {
      addLog('ORCHESTRATOR', 'START', '🚀 4-Agent Live Monitoring System ACTIVATED');
      addLog('CODESYNC', 'READY', '🔧 Network monitoring active');
      addLog('POLISH', 'READY', '✨ Error detection active');
      addLog('GUARDIAN', 'READY', '🛡️ React error protection active');
    }
  }, [isMonitoring]);

  const getLogColor = (type) => {
    switch (type) {
      case 'ERROR': return '#ff4444';
      case 'AUTOFIX': return '#44ff44';
      case 'SUCCESS': return '#4444ff';
      case 'NETWORK': return '#ffaa44';
      case 'STATE': return '#aa44ff';
      default: return '#ffffff';
    }
  };

  const getAgentEmoji = (agent) => {
    switch (agent) {
      case 'ORCHESTRATOR': return '🎯';
      case 'CODESYNC': return '🔧';
      case 'POLISH': return '✨';
      case 'GUARDIAN': return '🛡️';
      default: return '🤖';
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      width: '400px',
      height: '600px',
      backgroundColor: '#000',
      color: '#00ff00',
      fontFamily: 'monospace',
      fontSize: '12px',
      border: '2px solid #00ff00',
      borderRadius: '8px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #00ff00',
        backgroundColor: '#001100'
      }}>
        <h3 style={{ margin: 0, color: '#00ff00' }}>🤖 4-Agent Live Monitor</h3>
        <div style={{ fontSize: '10px', marginTop: '5px' }}>
          <span style={{ color: '#ff4444' }}>Errors: {errorCount}</span> | 
          <span style={{ color: '#44ff44' }}> Auto-fixes: {autoFixCount}</span>
        </div>
        <div style={{ display: 'flex', gap: '5px', marginTop: '5px' }}>
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            style={{
              padding: '2px 8px',
              backgroundColor: isMonitoring ? '#ff4444' : '#44ff44',
              color: '#000',
              border: 'none',
              borderRadius: '3px',
              fontSize: '10px'
            }}
          >
            {isMonitoring ? 'STOP' : 'START'}
          </button>
          <button
            onClick={() => setLogs([])}
            style={{
              padding: '2px 8px',
              backgroundColor: '#ffaa44',
              color: '#000',
              border: 'none',
              borderRadius: '3px',
              fontSize: '10px'
            }}
          >
            CLEAR
          </button>
          <button
            onClick={() => {
              const errorLogs = logs.filter(log => log.type === 'ERROR');
              console.log('🔍 All Errors:', errorLogs);
              addLog('ORCHESTRATOR', 'EXPORT', `Exported ${errorLogs.length} errors to console`);
            }}
            style={{
              padding: '2px 8px',
              backgroundColor: '#aa44ff',
              color: '#000',
              border: 'none',
              borderRadius: '3px',
              fontSize: '10px'
            }}
          >
            EXPORT
          </button>
        </div>
      </div>
      
      <div
        ref={logsRef}
        style={{
          flex: 1,
          padding: '10px',
          overflowY: 'auto',
          lineHeight: '1.2'
        }}
      >
        {logs.map((log, index) => (
          <div key={index} style={{ marginBottom: '3px' }}>
            <span style={{ color: '#666' }}>
              {log.timestamp.split('T')[1].split('.')[0]}
            </span>
            <span style={{ marginLeft: '5px' }}>
              {getAgentEmoji(log.agent)}
            </span>
            <span 
              style={{ 
                color: getLogColor(log.type),
                marginLeft: '5px',
                fontWeight: 'bold'
              }}
            >
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

export default LiveMonitor;
