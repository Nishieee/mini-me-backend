#!/usr/bin/env python3
"""
MiniMe Wake Word Detector Module
Detects "Hey MiniMe" wake word using Picovoice Porcupine.
"""

import contextlib
import io
import os
import sys

import numpy as np
import pvporcupine
import pyaudio

from config import PICOVOICE_KEY, PROJECT_ROOT, WAKE_WORD_MODEL


class WakeWordDetector:
    """Handles wake word detection with proper resource management."""
    
    def __init__(self):
        """Initialize the wake word detector."""
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Porcupine and PyAudio."""
        if not PICOVOICE_KEY or PICOVOICE_KEY == 'your_picovoice_access_key_here':
            raise ValueError(
                "PICOVOICE_KEY not found in keys.env. "
                "Get your key from: https://console.picovoice.ai/"
            )
        
        if not WAKE_WORD_MODEL.exists():
            raise FileNotFoundError(
                f"Wake word model file not found: {WAKE_WORD_MODEL}\n"
                "Please place your minime.ppn file in the wakeword/ directory"
            )
        
        # Initialize Porcupine
        try:
            self.porcupine = pvporcupine.create(
                access_key=PICOVOICE_KEY,
                keyword_paths=[str(WAKE_WORD_MODEL)]
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Porcupine: {e}") from e
        
        # Initialize PyAudio (suppress macOS PortAudio warnings)
        with contextlib.redirect_stderr(io.StringIO()):
            self.pa = pyaudio.PyAudio()
        
        # Open audio stream
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
    
    def listen_for_wake_word(self):
        """
        Listens continuously for the wake word.
        
        Returns:
            bool: True when wake word is detected
        """
        try:
            while True:
                # Read audio frame
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                # Convert bytes to numpy array of int16
                pcm = np.frombuffer(pcm, dtype=np.int16)
                
                # Check for wake word
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    return True
                    
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user", flush=True)
            return False
        except Exception as e:
            print(f"ERROR in wake word detection: {e}", file=sys.stderr, flush=True)
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()
