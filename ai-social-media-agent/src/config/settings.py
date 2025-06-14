# Contents of the file: /ai-social-media-agent/ai-social-media-agent/src/config/settings.py

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        # Only use Groq API
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        
        # Filter out placeholder values for Groq
        if self.groq_api_key in ["YOUR_NEW_GROQ_API_KEY", "your_groq_api_key_here", None, ""]:
            self.groq_api_key = None
        
        # Always use Groq
        if self.groq_api_key:
            self.use_groq = True
            self.model_name: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
        else:
            raise ValueError("GROQ_API_KEY environment variable is required")
            
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
