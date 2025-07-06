import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    def __init__(self):
        # Twitter API Configuration
        self.API_KEY = self._get_env_var('API_KEY')
        self.API_SECRET_KEY = self._get_env_var('API_SECRET_KEY')
        self.ACCESS_TOKEN = self._get_env_var('ACCESS_TOKEN')
        self.ACCESS_TOKEN_SECRET = self._get_env_var('ACCESS_TOKEN_SECRET')
        self.BEARER_TOKEN = self._get_env_var('BEARER_TOKEN')
        
        # Database Configuration
        self.DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///src/default.db')
        
        # Application Configuration
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
        self.DASH_PORT = int(os.getenv('DASH_PORT', '8050'))
        
        # Streaming Configuration
        self.DEFAULT_KEYWORDS = [
            'python',
            'data science',
            'AI',
            'machine learning',
            'artificial intelligence'
        ]
        
        # Validate configuration
        self._validate_config()
    
    def _get_env_var(self, var_name):
        """Get environment variable with error handling"""
        value = os.getenv(var_name)
        if not value:
            logger.error(f"Missing required environment variable: {var_name}")
            raise ValueError(f"Missing required environment variable: {var_name}")
        return value
    
    def _validate_config(self):
        """Validate configuration settings"""
        required_vars = [
            'API_KEY',
            'API_SECRET_KEY',
            'ACCESS_TOKEN',
            'ACCESS_TOKEN_SECRET',
            'BEARER_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var, None)]
        
        if missing_vars:
            error_msg = f"Missing required configuration variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validated successfully")
    
    @property
    def twitter_config(self):
        """Get Twitter API configuration as a dictionary"""
        return {
            'consumer_key': self.API_KEY,
            'consumer_secret': self.API_SECRET_KEY,
            'access_token': self.ACCESS_TOKEN,
            'access_token_secret': self.ACCESS_TOKEN_SECRET,
            'bearer_token': self.BEARER_TOKEN
        }

# Create a global config instance
try:
    config = Config()
except Exception as e:
    logger.error(f"Error initializing configuration: {e}")
    raise 