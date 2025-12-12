#!/usr/bin/env python3
"""
MiniMe Text-to-Speech Module
Uses ElevenLabs TTS API to convert text to speech and play it.
"""

import sys

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

from config import ELEVEN_API_KEY, ELEVEN_VOICE_ID, TTS_MODEL


def speak_text(text: str):
    """
    Takes text and plays it out loud using ElevenLabs TTS.
    
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
        
        # Play the audio directly through system speakers
        play(audio_generator)
        
    except Exception as e:
        # Parse ElevenLabs API errors for better user feedback
        error_str = str(e)
        
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
