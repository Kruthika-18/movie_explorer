"""
config.py - Application Configuration
--------------------------------------
Stores all settings for different environments.
Uses environment variables for security.
"""

import os
from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

class Config:
    """Base configuration shared by all environments."""
    
    # Secret key for session security & CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key')
    
    # OMDb API key
    OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')
    OMDB_BASE_URL = 'http://www.omdbapi.com/'
    
    # Database URI - SQLite by default, easy to switch to PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///movie_explorer.db')
    
    # Disable modification tracking (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination
    RESULTS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development environment - shows debug info."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment - secure settings."""
    DEBUG = False


# Dictionary to select config by name
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
