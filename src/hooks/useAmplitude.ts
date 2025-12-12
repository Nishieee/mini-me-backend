import { useEffect, useState, useRef } from 'react';

export function useAmplitude(stream: MediaStream | null): number[] {
  const [levels, setLevels] = useState<number[]>([]);
  const animationFrameRef = useRef<number>();
  const analyserRef = useRef<AnalyserNode | null>(null);

  useEffect(() => {
    if (!stream) {
      setLevels([]);
      return;
    }

    // Create audio context and analyser
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);

    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.8;
    source.connect(analyser);

    analyserRef.current = analyser;

    // Frequency data array
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    // Animation loop to update levels
    function updateLevels() {
      if (!analyserRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArray);

      // Normalize values (0-255 -> 0-1) and take first 12 values for the matrix
      const normalized = Array.from(dataArray.slice(0, 12)).map(v => v / 255);
      
      // Boost sensitivity - multiply by a factor to make it more responsive
      const boosted = normalized.map(v => Math.min(v * 2, 1));

      setLevels(boosted);

      animationFrameRef.current = requestAnimationFrame(updateLevels);
    }

    updateLevels();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      source.disconnect();
      analyser.disconnect();
      audioContext.close();
    };
  }, [stream]);

  return levels;
}

