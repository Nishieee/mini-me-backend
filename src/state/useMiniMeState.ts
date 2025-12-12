import { useState, useEffect, useRef } from 'react';

export type MiniMeState = 
  | 'idle' 
  | 'wake' 
  | 'listening' 
  | 'thinking' 
  | 'talk' 
  | 'blink' 
  | 'sleep';

interface MiniMeStateConfig {
  state: MiniMeState;
  levels: number[];
  micLevel: number;
  lastBackendEvent: number;
  wakeStartTime: number | null;
}

/**
 * MiniMe State Machine
 * Manages all avatar states with priority rules
 */
export function useMiniMeState(
  micLevel: number,
  backendEvent: { event: string; levels?: number[] } | null,
  isBlinking: boolean
): { state: MiniMeState; levels: number[] } {
  const [config, setConfig] = useState<MiniMeStateConfig>({
    state: 'idle',
    levels: [],
    micLevel: 0,
    lastBackendEvent: Date.now(),
    wakeStartTime: null,
  });

  const idleTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sleepTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setConfig(prev => ({ ...prev, micLevel }));
  }, [micLevel]);

  useEffect(() => {
    if (!backendEvent) return;

    const now = Date.now();

    if (backendEvent.event === 'wake') {
      setConfig(prev => ({
        ...prev,
        state: 'wake',
        levels: [],
        lastBackendEvent: now,
        wakeStartTime: now,
      }));
    } else if (backendEvent.event === 'thinking') {
      setConfig(prev => ({
        ...prev,
        state: 'thinking',
        levels: [],
        lastBackendEvent: now,
      }));
    } else if (backendEvent.event === 'talk') {
      setConfig(prev => ({
        ...prev,
        state: 'talk',
        levels: backendEvent.levels || [],
        lastBackendEvent: now,
      }));
    } else if (backendEvent.event === 'idle') {
      setConfig(prev => ({
        ...prev,
        state: 'idle',
        levels: [],
        lastBackendEvent: now,
      }));
    } else if (backendEvent.event === 'sleep') {
      setConfig(prev => ({
        ...prev,
        state: 'sleep',
        levels: [],
        lastBackendEvent: now,
      }));
    } else if (backendEvent.event === 'listening') {
      setConfig(prev => ({
        ...prev,
        state: 'listening',
        levels: [],
        lastBackendEvent: now,
      }));
    }
  }, [backendEvent]);

  // Handle wake mode timeout (500ms)
  useEffect(() => {
    if (config.state === 'wake' && config.wakeStartTime) {
      const timeout = setTimeout(() => {
        setConfig(prev => ({
          ...prev,
          state: 'idle',
          wakeStartTime: null,
        }));
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [config.state, config.wakeStartTime]);

  // Handle listening mode (mic level > 0.1 and not in talk state)
  useEffect(() => {
    // Don't override talk, wake, thinking, or sleep states
    if (config.state === 'talk' || config.state === 'wake' || config.state === 'thinking' || config.state === 'sleep') {
      return;
    }

    if (micLevel > 0.1) {
      // Clear any existing timeouts
      if (idleTimeoutRef.current) {
        clearTimeout(idleTimeoutRef.current);
        idleTimeoutRef.current = null;
      }
      setConfig(prev => ({
        ...prev,
        state: 'listening',
        levels: Array(12).fill(micLevel),
      }));
    } else if (config.state === 'listening' && micLevel < 0.03) {
      // Clear listening timeout
      if (idleTimeoutRef.current) {
        clearTimeout(idleTimeoutRef.current);
      }
      // Transition to idle after 3 seconds of silence
      idleTimeoutRef.current = setTimeout(() => {
        setConfig(prev => ({
          ...prev,
          state: 'idle',
          levels: [],
        }));
      }, 3000);
    } else if (config.state === 'listening') {
      // Update levels while listening
      setConfig(prev => ({
        ...prev,
        levels: Array(12).fill(micLevel),
      }));
    }
  }, [micLevel, config.state]);

  // Handle sleep mode (no sound for 10 seconds)
  useEffect(() => {
    if (config.state === 'idle' && micLevel < 0.03) {
      if (sleepTimeoutRef.current) {
        clearTimeout(sleepTimeoutRef.current);
      }
      sleepTimeoutRef.current = setTimeout(() => {
        setConfig(prev => ({
          ...prev,
          state: 'sleep',
          levels: [],
        }));
      }, 10000);
    } else {
      if (sleepTimeoutRef.current) {
        clearTimeout(sleepTimeoutRef.current);
      }
    }
  }, [config.state, micLevel]);

  // Apply blink override (blink overrides everything except talk)
  const finalState: MiniMeState = 
    isBlinking && config.state !== 'talk' ? 'blink' : config.state;

  // Cleanup timeouts
  useEffect(() => {
    return () => {
      if (idleTimeoutRef.current) {
        clearTimeout(idleTimeoutRef.current);
      }
      if (sleepTimeoutRef.current) {
        clearTimeout(sleepTimeoutRef.current);
      }
    };
  }, []);

  return {
    state: finalState,
    levels: config.levels,
  };
}

