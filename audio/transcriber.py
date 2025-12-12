#!/usr/bin/env python3
"""
MiniMe Transcription Module
Transcribes audio to text using OpenAI Whisper API.
"""

import os
import sys

from openai import OpenAI

from config import OPENAI_API_KEY


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribes audio file to text using OpenAI Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: The transcribed text
        
    Raises:
        ValueError: If API key is not configured
        FileNotFoundError: If audio file doesn't exist
        Exception: For other transcription errors
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found in keys.env. "
            "Please add your OpenAI API key to keys.env"
        )
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print("🔄 Transcribing audio...", flush=True)
        
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        text = transcript.text.strip()
        print(f"📝 Transcribed: {text}", flush=True)
        return text
        
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        print(error_msg, file=sys.stderr, flush=True)
        raise Exception(error_msg) from e
