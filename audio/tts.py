#!/usr/bin/env python3
"""
MiniMe Text-to-Speech Module
Uses ElevenLabs TTS API to convert text to speech and play it.
Extracts audio levels for mouth animation.
"""

import io
import struct
import sys
import wave

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

from config import ELEVEN_API_KEY, ELEVEN_VOICE_ID, TTS_MODEL

# Import WebSocket sender (will be None if not available)
try:
    from backend.ws_server import send_to_ui
except ImportError:
    send_to_ui = None


def extract_audio_levels(audio_bytes: bytes, chunk_size: int = 1024) -> list:
    """
    Extract amplitude levels from audio bytes for mouth animation.
    
    Args:
        audio_bytes: Raw audio data (PCM)
        chunk_size: Size of each analysis chunk
        
    Returns:
        List of normalized amplitude levels (0-1) for 12 frequency bands
    """
    try:
        # Try to parse as WAV
        audio_io = io.BytesIO(audio_bytes)
        wav_file = wave.open(audio_io, 'rb')
        
        # Read audio data
        frames = wav_file.readframes(wav_file.getnframes())
        wav_file.close()
        
        # Convert to 16-bit integers
        samples = struct.unpack(f'{len(frames)//2}h', frames)
        
        # Calculate RMS for chunks
        num_chunks = 12
        chunk_length = len(samples) // num_chunks
        levels = []
        
        for i in range(num_chunks):
            start = i * chunk_length
            end = start + chunk_length
            chunk = samples[start:end] if end <= len(samples) else samples[start:]
            
            if chunk:
                # Calculate RMS (root mean square) for amplitude
                rms = (sum(x * x for x in chunk) / len(chunk)) ** 0.5
                # Normalize to 0-1 range (assuming max 16-bit value ~32768)
                normalized = min(rms / 16384.0, 1.0)
                levels.append(normalized)
            else:
                levels.append(0.0)
        
        return levels[:12]  # Return exactly 12 values
        
    except Exception as e:
        # If parsing fails, return zero levels
        print(f"Warning: Could not extract audio levels: {e}", flush=True)
        return [0.0] * 12


def speak_text(text: str):
    """
    Takes text and plays it out loud using ElevenLabs TTS.
    Sends audio levels to frontend via WebSocket for mouth animation.
    
    Args:
        text (str): The text to convert to speech and play
        
    Raises:
        ValueError: If API key is not configured
        Exception: For other ElevenLabs API errors
    """
    if not ELEVEN_API_KEY:
        raise ValueError(
            "ELEVEN_API_KEY not found in keys.env. "
            "Please add your ElevenLabs API key to keys.env"
        )
    
    if not text or not text.strip():
        print("Warning: Empty text provided to speak_text", flush=True)
        return
    
    try:
        client = ElevenLabs(api_key=ELEVEN_API_KEY)
        
        # Generate audio using ElevenLabs API
        audio_generator = client.text_to_speech.convert(
            voice_id=ELEVEN_VOICE_ID,
            text=text,
            model_id=TTS_MODEL
        )
        
        # Collect audio chunks for level extraction
        audio_chunks = []
        frame_size = 4096  # Process in frames
        
        # Notify frontend that MiniMe is about to talk
        if send_to_ui:
            send_to_ui({"event": "talk", "levels": [0.0] * 12})
        
        # Process audio in chunks and extract levels
        for chunk in audio_generator:
            audio_chunks.append(chunk)
            
            # Extract levels from this chunk
            if send_to_ui and len(chunk) > 0:
                try:
                    levels = extract_audio_levels(chunk)
                    send_to_ui({"event": "talk", "levels": levels})
                except Exception as e:
                    # Continue even if level extraction fails
                    pass
        
        # Combine all chunks
        audio_data = b''.join(audio_chunks)
        
        # Play the audio
        play(io.BytesIO(audio_data))
        
        # Notify frontend that talking is done
        if send_to_ui:
            send_to_ui({"event": "idle"})
        
    except Exception as e:
        # Parse ElevenLabs API errors for better user feedback
        error_str = str(e)
        
        # Notify frontend of error
        if send_to_ui:
            send_to_ui({"event": "idle"})
        
        # Check for permission errors
        if "missing_permissions" in error_str or "text_to_speech" in error_str.lower():
            error_msg = (
                "❌ ElevenLabs API Error: Your API key is missing the 'text_to_speech' permission.\n"
                "   Please go to https://elevenlabs.io/ and:\n"
                "   1. Check your API key permissions\n"
                "   2. Ensure 'text_to_speech' permission is enabled\n"
                "   3. Update your API key in keys.env if needed"
            )
        elif "401" in error_str or "unauthorized" in error_str.lower():
            error_msg = (
                "❌ ElevenLabs API Error: Invalid or unauthorized API key.\n"
                "   Please check your ELEVEN_API_KEY in keys.env"
            )
        elif "quota" in error_str.lower() or "limit" in error_str.lower():
            error_msg = (
                "❌ ElevenLabs API Error: Quota exceeded or rate limit reached.\n"
                "   Please check your ElevenLabs account usage"
            )
        else:
            error_msg = f"Error in ElevenLabs TTS: {error_str}"
        
        print(error_msg, file=sys.stderr, flush=True)
        raise Exception(error_msg) from e
