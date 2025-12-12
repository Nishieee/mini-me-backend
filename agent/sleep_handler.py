#!/usr/bin/env python3
"""
MiniMe Sleep Mode Handler
Detects sleep commands and handles sleep mode transitions.
"""

def is_sleep_command(text: str) -> bool:
    """
    Returns True if the user text contains any sleep-mode command.
    
    Args:
        text (str): The user's transcribed text
        
    Returns:
        bool: True if a sleep command is detected
    """
    if not text:
        return False
    
    # Normalize text to lowercase for case-insensitive matching
    text_lower = text.lower().strip()
    
    # List of sleep command phrases
    sleep_phrases = [
        "ok bye",
        "okay bye",
        "goodbye",
        "good bye",
        "bye",
        "bye minime",
        "sleep",
        "go to sleep",
        "rest",
        "rest now",
        "quiet",
        "go away",
        "stop",
        "later",
        "you can sleep"
    ]
    
    # Check if any sleep phrase is in the text
    for phrase in sleep_phrases:
        if phrase in text_lower:
            return True
    
    return False

def get_sleep_message() -> str:
    """
    Returns a short sleep message for MiniMe to say.
    
    Returns:
        str: Sleep message text
    """
    return "Okay yaar, I'm sleeping… call me when needed."

