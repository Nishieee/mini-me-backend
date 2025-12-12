import { useEffect, useState, useRef } from 'react';

/**
 * Automatic blinking animation manager
 * Triggers blink every 3-6 seconds (random)
 * Blink duration: 120ms
 */
export function useBlink(): boolean {
  const [isBlinking, setIsBlinking] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const blinkTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    function scheduleBlink() {
      // Random interval between 3-6 seconds
      const delay = 3000 + Math.random() * 3000;

      timeoutRef.current = setTimeout(() => {
        setIsBlinking(true);

        // Blink duration: 120ms
        blinkTimeoutRef.current = setTimeout(() => {
          setIsBlinking(false);
          scheduleBlink(); // Schedule next blink
        }, 120);
      }, delay);
    }

    scheduleBlink();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
    };
  }, []);

  return isBlinking;
}

/**
 * Generate blink pattern for Matrix component
 * Top rows turn on, creating a "blink" effect
 */
export function generateBlinkPattern(rows: number, cols: number): number[][] {
  const pattern: number[][] = [];
  for (let row = 0; row < rows; row++) {
    pattern[row] = [];
    for (let col = 0; col < cols; col++) {
      // Top 2-3 rows light up for blink
      if (row < 2) {
        pattern[row][col] = 0.9;
      } else {
        pattern[row][col] = 0.1;
      }
    }
  }
  return pattern;
}

