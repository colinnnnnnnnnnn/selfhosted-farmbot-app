import React, { useEffect, useState, useRef } from 'react';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [connected, setConnected] = useState(false);
  const logsEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/logs/');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected to logs');
      setConnected(true);
      setLogs(prev => [...prev, { timestamp: new Date().toISOString(), message: '>>> Connected to log stream' }]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Extract the message field - if it's an object, get its 'message' property
        let message = data.message;
        if (typeof message === 'object' && message !== null) {
          message = message.message || JSON.stringify(message);
        }
        // Ensure it's a string
        if (typeof message !== 'string') {
          message = String(message);
        }
        // Prevent duplicate consecutive messages
        setLogs(prev => {
          const lastLog = prev[prev.length - 1];
          if (lastLog && lastLog.message === message) {
            return prev; // Skip duplicate
          }
          return [...prev, { 
            timestamp: new Date().toISOString(), 
            message: message
          }];
        });
      } catch (e) {
        // If not JSON, just display raw message
        setLogs(prev => [...prev, { 
          timestamp: new Date().toISOString(), 
          message: event.data 
        }]);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setLogs(prev => [...prev, { timestamp: new Date().toISOString(), message: '>>> WebSocket error occurred' }]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setLogs(prev => [...prev, { timestamp: new Date().toISOString(), message: '>>> Disconnected from log stream' }]);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      width: '400px',
      height: '450px',
      backgroundColor: '#1e1e1e',
      border: '2px solid #555',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '10px 15px',
        backgroundColor: '#2d2d2d',
        borderBottom: '1px solid #555',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ margin: 0, color: 'white', fontSize: '16px' }}>Live Logs</h3>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: connected ? '#4caf50' : '#f44336'
          }} title={connected ? 'Connected' : 'Disconnected'} />
        </div>
        <button 
          onClick={clearLogs}
          style={{
            padding: '5px 10px',
            fontSize: '12px',
            backgroundColor: '#444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Clear
        </button>
      </div>

      {/* Log content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '10px',
        fontFamily: 'Consolas, Monaco, monospace',
        fontSize: '12px',
        color: '#d4d4d4',
        backgroundColor: '#1e1e1e'
      }}>
        {logs.length === 0 ? (
          <div style={{ color: '#888', fontStyle: 'italic' }}>
            Waiting for logs...
          </div>
        ) : (
          logs.map((log, index) => {
            const messageStr = String(log.message || '');
            return (
              <div key={index} style={{ 
                marginBottom: '8px',
                borderLeft: '2px solid #444',
                paddingLeft: '8px',
                lineHeight: '1.4'
              }}>
                <span style={{ color: '#888', fontSize: '10px' }}>
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>
                {' '}
                <span style={{ color: messageStr.startsWith('>>>') ? '#4caf50' : '#d4d4d4' }}>
                  {messageStr}
                </span>
              </div>
            );
          })
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default LogViewer;
