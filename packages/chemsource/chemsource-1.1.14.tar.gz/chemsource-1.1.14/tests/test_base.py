"""
Base test class for chemsource tests that require API keys.
"""
import os
import unittest
from chemsource.config import Config


class BaseTestWithAPIKeys(unittest.TestCase):
    """
    Base test class that provides real API keys for testing.
    
    This class checks for environment variables and sets up
    configuration objects with real API keys for integration testing.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        cls.openai_api_key = os.environ.get('OPENAI_API_KEY')
        cls.ncbi_api_key = os.environ.get('NCBI_API_KEY')
        
        if not cls.openai_api_key:
            raise unittest.SkipTest(
                "OPENAI_API_KEY environment variable not set. "
                "Set it with: export OPENAI_API_KEY=your_key_here"
            )
    
    def get_test_config(self, **kwargs):
        """
        Get a test configuration with real API keys.
        
        Args:
            **kwargs: Additional configuration parameters to override
        
        Returns:
            Config: Configuration object with real API keys
        """
        config_params = {
            'model_api_key': self.openai_api_key,
            'ncbi_key': self.ncbi_api_key,
        }
        config_params.update(kwargs)
        return Config(**config_params)


class BaseTestNoAPIKeys(unittest.TestCase):
    """
    Base test class for tests that don't require API keys.
    
    This class is for unit tests that test functionality
    without making external API calls.
    """
    pass
