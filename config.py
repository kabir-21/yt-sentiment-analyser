import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # YouTube API Configuration
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your_youtube_api_key_here')
    
    # LLM API Keys (optional - users can provide in UI)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Application Settings
    MAX_VIDEOS_PER_ANALYSIS = 50
    DEFAULT_VIDEOS_COUNT = 10
    
    # API Rate Limiting (requests per minute)
    YOUTUBE_RATE_LIMIT = 100
    LLM_RATE_LIMIT = 60
