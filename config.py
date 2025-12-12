#!/usr/bin/env python3
"""
MiniMe Configuration Module
Centralized configuration and environment variable loading.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / "keys.env"

# Load environment variables
load_dotenv(ENV_FILE)

# API Keys
PICOVOICE_KEY = os.getenv('PICOVOICE_KEY')
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY') or os.getenv('ELEVEN_LAB_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVEN_VOICE_ID = os.getenv('ELEVEN_VOICE_ID', 'BZLr92pCdlwYqmn82yuB')

# File paths
WAKE_WORD_MODEL = PROJECT_ROOT / 'wakeword' / 'minime.ppn'
SOUL_PROMPT_FILE = PROJECT_ROOT / 'agent' / 'soul_prompt.txt'

# Audio settings
AUDIO_CHUNK = 1024
AUDIO_FORMAT = 'int16'
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
SILENCE_THRESHOLD = 150
SILENCE_DURATION = 2.5
MAX_RECORDING_DURATION = 30
AUTO_STOP_DURATION = 5.0  # Auto-stop after this many seconds if audio detected

# LLM settings
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.9
LLM_MAX_TOKENS = 150  # Reduced for less verbose responses

# TTS settings
TTS_MODEL = "eleven_monolingual_v1"

def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not PICOVOICE_KEY or PICOVOICE_KEY == 'your_picovoice_access_key_here':
        errors.append("PICOVOICE_KEY not found in keys.env")
    
    if not ELEVEN_API_KEY:
        errors.append("ELEVEN_API_KEY not found in keys.env")
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not found in keys.env")
    
    if not WAKE_WORD_MODEL.exists():
        errors.append(f"Wake word model not found: {WAKE_WORD_MODEL}")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

