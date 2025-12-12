import React from 'react';
import { Matrix } from './matrix';
import { generateBlinkPattern } from '../state/useBlink';

export type MiniMeState = 'idle' | 'wake' | 'listening' | 'thinking' | 'talk' | 'blink' | 'sleep';

interface MiniMeFaceProps {
  state: MiniMeState;
  levels: number[];
}

// Idle animation: gentle wave pattern (breathing)
const generateIdleWave = (frame: number, rows: number, cols: number): number[][] => {
  const frames: number[][] = [];
  for (let row = 0; row < rows; row++) {
    frames[row] = [];
    for (let col = 0; col < cols; col++) {
      const wave = Math.sin((col + frame * 0.1) * 0.5) * 0.3 + 0.3;
      frames[row][col] = Math.max(0, wave);
    }
  }
  return frames;
};

// Wake animation: bright pulse effect (excited)
const generateWakePulse = (frame: number, rows: number, cols: number): number[][] => {
  const frames: number[][] = [];
  const centerRow = Math.floor(rows / 2);
  const centerCol = Math.floor(cols / 2);
  const pulse = Math.sin(frame * 0.3) * 0.5 + 0.5;
  
  for (let row = 0; row < rows; row++) {
    frames[row] = [];
    for (let col = 0; col < cols; col++) {
      const dist = Math.sqrt(
        Math.pow(row - centerRow, 2) + Math.pow(col - centerCol, 2)
      );
      const maxDist = Math.sqrt(Math.pow(rows, 2) + Math.pow(cols, 2));
      const intensity = Math.max(0, 1 - (dist / maxDist) * 2) * pulse;
      frames[row][col] = intensity * 0.9; // Bright
    }
  }
  return frames;
};

// Thinking animation: pulse pattern
const generateThinkingPulse = (frame: number, rows: number, cols: number): number[][] => {
  const frames: number[][] = [];
  const pulse = Math.sin(frame * 0.2) * 0.4 + 0.5;
  
  for (let row = 0; row < rows; row++) {
    frames[row] = [];
    for (let col = 0; col < cols; col++) {
      const phase = (col + row + frame * 0.2) % 4;
      frames[row][col] = phase < 2 ? pulse : pulse * 0.3;
    }
  }
  return frames;
};

// Sleep animation: dim pattern
const generateSleepPattern = (frame: number, rows: number, cols: number): number[][] => {
  const frames: number[][] = [];
  const dim = Math.sin(frame * 0.05) * 0.1 + 0.1;
  
  for (let row = 0; row < rows; row++) {
    frames[row] = [];
    for (let col = 0; col < cols; col++) {
      frames[row][col] = dim;
    }
  }
  return frames;
};

export const MiniMeFace: React.FC<MiniMeFaceProps> = ({ state, levels }) => {
  const [animationFrame, setAnimationFrame] = React.useState(0);

  // Animation loop for frame-based animations
  React.useEffect(() => {
    if (state === 'idle' || state === 'wake' || state === 'thinking' || state === 'sleep') {
      const interval = setInterval(() => {
        setAnimationFrame(prev => prev + 1);
      }, 50); // ~20fps for animations
      return () => clearInterval(interval);
    } else {
      setAnimationFrame(0);
    }
  }, [state]);

  // Generate levels based on state
  let animationLevels: number[] = [];
  
  if (state === 'talk') {
    // Talking: use real audio levels from backend
    animationLevels = levels.length > 0 ? levels : Array(12).fill(0);
  } else if (state === 'listening') {
    // Listening: use mic levels
    animationLevels = levels.length > 0 ? levels : Array(12).fill(0);
  } else if (state === 'blink') {
    // Blink: convert blink pattern to levels
    const blinkPattern = generateBlinkPattern(7, 12);
    animationLevels = Array.from({ length: 12 }, (_, col) => {
      const colValues = blinkPattern.map(row => row[col]);
      return colValues.reduce((a, b) => a + b, 0) / colValues.length;
    });
  } else if (state === 'idle') {
    const frames = generateIdleWave(animationFrame, 7, 12);
    animationLevels = Array.from({ length: 12 }, (_, col) => {
      const colValues = frames.map(row => row[col]);
      return colValues.reduce((a, b) => a + b, 0) / colValues.length;
    });
  } else if (state === 'wake') {
    const frames = generateWakePulse(animationFrame, 7, 12);
    animationLevels = Array.from({ length: 12 }, (_, col) => {
      const colValues = frames.map(row => row[col]);
      return colValues.reduce((a, b) => a + b, 0) / colValues.length;
    });
  } else if (state === 'thinking') {
    const frames = generateThinkingPulse(animationFrame, 7, 12);
    animationLevels = Array.from({ length: 12 }, (_, col) => {
      const colValues = frames.map(row => row[col]);
      return colValues.reduce((a, b) => a + b, 0) / colValues.length;
    });
  } else if (state === 'sleep') {
    const frames = generateSleepPattern(animationFrame, 7, 12);
    animationLevels = Array.from({ length: 12 }, (_, col) => {
      const colValues = frames.map(row => row[col]);
      return colValues.reduce((a, b) => a + b, 0) / colValues.length;
    });
  } else {
    // Default: all off
    animationLevels = Array(12).fill(0.0);
  }
  
  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'transparent'
    }}>
      <Matrix
        rows={7}
        cols={12}
        mode="vu"
        levels={animationLevels}
        size={12}
        gap={2}
        palette={{ on: "#FFD700", off: "#222" }}
      />
    </div>
  );
};
