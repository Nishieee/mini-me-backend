#!/usr/bin/env python3
"""
MiniMe Audio Recorder Module
Records audio from microphone after wake word detection.
"""

import contextlib
import io
import os
import struct
import sys
import tempfile
import wave
from pathlib import Path

import pyaudio

from config import (
    AUDIO_CHUNK,
    AUDIO_CHANNELS,
    AUDIO_RATE,
    AUTO_STOP_DURATION,
    MAX_RECORDING_DURATION,
    PROJECT_ROOT,
    SILENCE_DURATION,
    SILENCE_THRESHOLD,
)

# PyAudio constants
FORMAT = pyaudio.paInt16


def record_until_silence(max_duration=MAX_RECORDING_DURATION):
    """
    Records audio from microphone until silence is detected or max duration reached.
    
    Args:
        max_duration (float): Maximum recording duration in seconds
        
    Returns:
        str: Path to the temporary WAV file containing the recorded audio
        
    Raises:
        Exception: If recording fails
    """
    temp_file = None
    pa = None
    stream = None
    
    try:
        # Suppress PortAudio macOS warnings
        with contextlib.redirect_stderr(io.StringIO()):
            pa = pyaudio.PyAudio()
        
        # Create temporary WAV file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav', dir=PROJECT_ROOT)
        os.close(temp_fd)
        temp_file = temp_path
        
        # Open audio stream (suppress PortAudio warnings)
        with contextlib.redirect_stderr(io.StringIO()):
            stream = pa.open(
                format=FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK
            )
        
        frames = []
        silence_frame_count = int(SILENCE_DURATION * AUDIO_RATE / AUDIO_CHUNK)
        max_frames = int(max_duration * AUDIO_RATE / AUDIO_CHUNK)
        frame_count = 0
        
        print("🎤 Recording... (speak now, or stay silent for 2.5 seconds to finish)", flush=True)
        
        # Track recording state
        has_audio = False
        min_audio_frames = int(0.5 * AUDIO_RATE / AUDIO_CHUNK)
        consecutive_silence = 0
        auto_stop_frames = int(AUTO_STOP_DURATION * AUDIO_RATE / AUDIO_CHUNK)
        
        while frame_count < max_frames:
            data = stream.read(AUDIO_CHUNK, exception_on_overflow=False)
            frames.append(data)
            frame_count += 1
            
            # Calculate RMS for audio level detection
            audio_samples = struct.unpack(f'{AUDIO_CHUNK}h', data)
            rms = int((sum(x*x for x in audio_samples) / len(audio_samples)) ** 0.5)
            
            # Update audio detection state
            if rms > SILENCE_THRESHOLD:
                has_audio = True
                consecutive_silence = 0
            else:
                consecutive_silence += 1
            
            # Stop conditions
            # 1. Silence detected after audio
            if has_audio and consecutive_silence >= silence_frame_count and frame_count > min_audio_frames:
                print(f"✅ Recording complete (silence detected after {frame_count * AUDIO_CHUNK / AUDIO_RATE:.1f}s)", flush=True)
                break
            
            # 2. Auto-stop after reasonable duration
            if has_audio and frame_count >= auto_stop_frames:
                print(f"✅ Recording complete (auto-stop after {AUTO_STOP_DURATION}s)", flush=True)
                break
        
        # Final check
        if frame_count >= max_frames:
            print(f"✅ Recording complete (max duration reached)", flush=True)
        
        # Stop stream and save
        stream.stop_stream()
        stream.close()
        
        # Save to WAV file
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(AUDIO_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_file
        
    except Exception as e:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
        raise Exception(f"Error recording audio: {str(e)}") from e
    finally:
        if stream:
            stream.close()
        if pa:
            pa.terminate()
