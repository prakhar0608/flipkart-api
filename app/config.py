import os
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-session-secret-key')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Flipkart Ads API settings
    FLIPKART_CLIENT_ID = os.environ.get('FLIPKART_CLIENT_ID')
    FLIPKART_CLIENT_SECRET = os.environ.get('FLIPKART_CLIENT_SECRET')
    FLIPKART_REDIRECT_URI = os.environ.get('FLIPKART_REDIRECT_URI')
    FLIPKART_ENVIRONMENT = os.environ.get('FLIPKART_ENVIRONMENT', 'sandbox')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Mapping for environment selection
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config
}
