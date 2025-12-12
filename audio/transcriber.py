#!/usr/bin/env python3
"""
MiniMe Transcription Module
Transcribes audio to text using OpenAI Whisper API.
Accepts audio data directly in memory (no disk I/O).
"""

import io
import sys

from openai import OpenAI

from config import OPENAI_API_KEY


def transcribe_audio(audio_data: io.BytesIO) -> str:
    """
    Transcribes audio data to text using OpenAI Whisper API.
    
    Args:
        audio_data (io.BytesIO): In-memory WAV file containing the audio data
        
    Returns:
        str: The transcribed text
        
    Raises:
        ValueError: If API key is not configured
        Exception: For other transcription errors
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found in keys.env. "
            "Please add your OpenAI API key to keys.env"
        )
    
    if not audio_data:
        raise ValueError("Audio data is required for transcription")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print("🔄 Transcribing audio...", flush=True)
        
        # Reset buffer position to beginning
        audio_data.seek(0)
        
        # Create a file-like object with a filename for Whisper API
        audio_data.name = "audio.wav"
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_data,
            language="en"
        )
        
        text = transcript.text.strip()
        print(f"📝 Transcribed: {text}", flush=True)
        return text
        
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        print(error_msg, file=sys.stderr, flush=True)
        raise Exception(error_msg) from e
