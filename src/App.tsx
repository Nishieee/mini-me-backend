import React, { useEffect, useState, useRef } from 'react';
import { MiniMeFace } from './components/MiniMeFace';
import { useMicLevel } from './hooks/useMicLevel';
import { useBlink } from './state/useBlink';
import { useMiniMeState, MiniMeState } from './state/useMiniMeState';

function App() {
  const micLevel = useMicLevel();
  const isBlinking = useBlink();
  const [backendEvent, setBackendEvent] = useState<{ event: string; levels?: number[] } | null>(null);
  const lastBackendEventRef = useRef<number>(Date.now());

  // Listen for WebSocket messages from backend
  useEffect(() => {
    // Check if MiniMeSocket is available (from preload.js)
    if (!window.MiniMeSocket) {
      console.warn('⚠️ MiniMeSocket not available. Make sure preload.js is loaded.');
      return;
    }

    console.log('✅ Setting up WebSocket message handler...');

    // Listen for messages from backend
    window.MiniMeSocket.onMessage((msg: any) => {
      console.log('📨 Received from backend:', msg);
      lastBackendEventRef.current = Date.now();
      setBackendEvent(msg);
    });

    // Initial state
    console.log('🎬 Initializing MiniMe...');
  }, []);

  // Use state machine to manage all states
  const { state, levels } = useMiniMeState(micLevel, backendEvent, isBlinking);

  // Update levels for listening state (real-time mic levels)
  const finalLevels = React.useMemo(() => {
    if (state === 'listening' && micLevel > 0.1) {
      return Array(12).fill(micLevel);
    }
    return levels;
  }, [state, levels, micLevel]);

  // Debug logging
  useEffect(() => {
    if (micLevel > 0.1) {
      console.log('🎤 Mic level:', micLevel.toFixed(2));
    }
  }, [micLevel]);

  useEffect(() => {
    console.log('🎭 State:', state, 'Levels:', levels.length > 0 ? levels.map(l => l.toFixed(2)).join(', ') : 'none');
  }, [state, levels]);

  return <MiniMeFace state={state} levels={finalLevels} />;
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    MiniMeSocket?: {
      onMessage: (callback: (msg: any) => void) => void;
      send: (data: any) => void;
      isConnected: () => boolean;
    };
  }
}

export default App;
