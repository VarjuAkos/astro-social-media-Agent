# Contents of the file: /ai-social-media-agent/ai-social-media-agent/src/config/settings.py

import os
from typing import Optional

class Config:
    """Configuration settings for the application."""
    
    # API keys and other sensitive information
    FACEBOOK_API_KEY = os.getenv('FACEBOOK_API_KEY')
    INSTAGRAM_API_KEY = os.getenv('INSTAGRAM_API_KEY')
    LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY')
    X_API_KEY = os.getenv('X_API_KEY')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    PORT = int(os.getenv('PORT', 8501))

class Settings:
    def __init__(self):
        # Try Groq first, then fallback to OpenAI
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        # Filter out placeholder values for Groq
        if self.groq_api_key in ["YOUR_NEW_GROQ_API_KEY", "your_groq_api_key_here", None, ""]:
            self.groq_api_key = None
            
        # Filter out placeholder values for OpenAI
        if self.openai_api_key in ["your_openai_api_key_here", None, ""]:
            self.openai_api_key = None
        
        # Use Groq if available, otherwise OpenAI
        if self.groq_api_key:
            self.use_groq = True
            self.model_name: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
        else:
            self.use_groq = False
            self.model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
            
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "1500"))
        
        # Platform-specific constraints
        self.platform_limits = {
            "facebook": {"max_chars": 63206, "hashtag_limit": 30},
            "instagram": {"max_chars": 2200, "hashtag_limit": 30},
            "linkedin": {"max_chars": 1300, "hashtag_limit": 3},
            "x": {"max_chars": 280, "hashtag_limit": 2}
        }
        
        # Hungarian language preference
        self.primary_language = "hungarian"
        self.allow_english_words = True

settings = Settings()

    # Other settings can be added here as needed
