#!/usr/bin/env python3
"""
MiniMe Prompt Loader Module
Loads the system prompt from soul_prompt.txt for MiniMe's dual-personality system.
"""

from pathlib import Path

from config import SOUL_PROMPT_FILE


def load_system_prompt() -> str:
    """
    Loads the MiniMe system prompt (soul_prompt.txt) and returns it as a string.
    
    Returns:
        str: The complete system prompt text
        
    Raises:
        FileNotFoundError: If soul_prompt.txt is not found
        ValueError: If the file is empty
        IOError: If there's an error reading the file
    """
    if not SOUL_PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"System prompt file not found: {SOUL_PROMPT_FILE}\n"
            "Please create soul_prompt.txt in the agent/ directory and paste your MiniMe prompt."
        )
    
    try:
        with open(SOUL_PROMPT_FILE, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # Strip trailing whitespace safely (preserve leading whitespace and structure)
        prompt = prompt.rstrip()
        
        if not prompt:
            raise ValueError(
                f"System prompt file is empty: {SOUL_PROMPT_FILE}\n"
                "Please add your MiniMe prompt text to soul_prompt.txt"
            )
        
        return prompt
        
    except IOError as e:
        raise IOError(
            f"Error reading system prompt file {SOUL_PROMPT_FILE}: {str(e)}"
        ) from e
