#!/usr/bin/env python3
"""
MiniMe LLM Module
Generates MiniMe responses using OpenAI GPT with the soul prompt.
Maintains conversation history for context.
"""

import sys

from openai import OpenAI

from agent.prompt_loader import load_system_prompt
from config import LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY


class ConversationManager:
    """Manages conversation history for MiniMe."""
    
    def __init__(self):
        """Initialize conversation manager with system prompt."""
        self.system_prompt = load_system_prompt()
        # Add instruction to be concise
        self.system_prompt += "\n\nIMPORTANT: Keep your responses brief and concise. Don't be verbose."
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    def add_user_message(self, user_message: str):
        """Add user message to conversation history."""
        self.conversation_history.append({"role": "user", "content": user_message})
    
    def add_assistant_message(self, assistant_message: str):
        """Add assistant response to conversation history."""
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
    
    def generate_response(self, user_message: str) -> str:
        """
        Generates a MiniMe response using the LLM with conversation history.
        
        Args:
            user_message (str): The user's transcribed message
            
        Returns:
            str: MiniMe's response text
            
        Raises:
            ValueError: If API key is not configured
            Exception: For other LLM errors
        """
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found in keys.env. "
                "Please add your OpenAI API key to keys.env"
            )
        
        if not user_message or not user_message.strip():
            return "I didn't catch that. Can you repeat?"
        
        try:
            # Add user message to history
            self.add_user_message(user_message)
            
            print("🤖 Generating MiniMe response...", flush=True)
            
            # Generate response with full conversation history
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=self.conversation_history,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
            
            mini_response = response.choices[0].message.content.strip()
            
            # Add assistant response to history
            self.add_assistant_message(mini_response)
            
            print(f"💭 MiniMe: {mini_response}", flush=True)
            return mini_response
            
        except Exception as e:
            error_msg = f"Error generating LLM response: {str(e)}"
            print(error_msg, file=sys.stderr, flush=True)
            raise Exception(error_msg) from e
    
    def reset(self):
        """Reset conversation history (keep system prompt)."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]


# Global conversation manager instance
_conversation_manager = None


def get_conversation_manager():
    """Get or create the global conversation manager."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager


def generate_response(user_message: str) -> str:
    """
    Generates a MiniMe response using the LLM with conversation history.
    
    Args:
        user_message (str): The user's transcribed message
        
    Returns:
        str: MiniMe's response text
    """
    manager = get_conversation_manager()
    return manager.generate_response(user_message)


def reset_conversation():
    """Reset the conversation history."""
    manager = get_conversation_manager()
    manager.reset()
