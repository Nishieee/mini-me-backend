#!/usr/bin/env python3
"""
MiniMe Wake Word Listener (Step 1)
Detects "Hey MiniMe" wake word using Picovoice Porcupine.
"""

import os
import sys
from dotenv import load_dotenv
import numpy as np
import pvporcupine
import pyaudio

# Load environment variables from keys.env
load_dotenv('keys.env')

def main():
    # Get Picovoice access key
    access_key = os.getenv('PICOVOICE_KEY')
    if not access_key or access_key == 'your_picovoice_access_key_here':
        print("ERROR: Please set your PICOVOICE_KEY in keys.env")
        print("Get your key from: https://console.picovoice.ai/")
        sys.exit(1)
    
    # Path to the wake word model file
    keyword_path = os.path.join('wakeword', 'minime.ppn')
    
    if not os.path.exists(keyword_path):
        print(f"ERROR: Wake word model file not found: {keyword_path}")
        print("Please place your minime.ppn file in the wakeword/ directory")
        sys.exit(1)
    
    # Initialize Porcupine
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path]
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize Porcupine: {e}")
        sys.exit(1)
    
    # Initialize PyAudio
    pa = pyaudio.PyAudio()
    
    # Open audio stream
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    print("Listening for 'Hey MiniMe'...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length)
            # Convert bytes to numpy array of int16
            pcm = np.frombuffer(pcm, dtype=np.int16)
            
            # Check for wake word
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("Wake word detected!")
                break
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # Cleanup
        if 'audio_stream' in locals():
            audio_stream.close()
        if 'pa' in locals():
            pa.terminate()
        if 'porcupine' in locals():
            porcupine.delete()
        print("Cleanup complete")

if __name__ == '__main__':
    main()

