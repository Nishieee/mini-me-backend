import { useEffect, useState, useRef } from 'react';

/**
 * Real-time microphone level detection hook
 * Returns normalized amplitude (0-1) at ~60fps
 */
export function useMicLevel(): number {
  const [level, setLevel] = useState<number>(0);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();
  const dataArrayRef = useRef<Uint8Array | null>(null);

  useEffect(() => {
    let mounted = true;

    async function setupMicrophone() {
      try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (!mounted) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        streamRef.current = stream;

        // Create audio context
        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;

        // Create analyser node
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        analyserRef.current = analyser;

        // Create media stream source
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        // Create data array for time-domain analysis
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        dataArrayRef.current = dataArray;

        // Animation loop to update level at ~60fps
        function updateLevel() {
          if (!mounted || !analyserRef.current || !dataArrayRef.current) {
            return;
          }

          // Get time-domain data (waveform)
          analyserRef.current.getByteTimeDomainData(dataArrayRef.current);

          // Calculate RMS (Root Mean Square) for amplitude
          let sum = 0;
          for (let i = 0; i < dataArrayRef.current.length; i++) {
            const normalized = (dataArrayRef.current[i] - 128) / 128;
            sum += normalized * normalized;
          }
          const rms = Math.sqrt(sum / dataArrayRef.current.length);

          // Normalize to 0-1 range and boost sensitivity
          const normalizedLevel = Math.min(rms * 3, 1.0);

          setLevel(normalizedLevel);

          animationFrameRef.current = requestAnimationFrame(updateLevel);
        }

        updateLevel();
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setLevel(0);
      }
    }

    setupMicrophone();

    return () => {
      mounted = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return level;
}

