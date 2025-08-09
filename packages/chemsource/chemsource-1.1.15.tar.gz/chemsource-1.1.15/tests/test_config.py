"""
Tests for the configuration module.
"""
import unittest
from unittest.mock import patch
from chemsource.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def test_config_initialization_defaults(self):
        """Test Config initialization with default values."""
        config = Config()
        
        # Test default values
        self.assertIsNone(config.model_api_key)
        self.assertIsNone(config.ncbi_key)
        self.assertEqual(config.model, "gpt-4o")
        from chemsource.config import BASE_PROMPT
        self.assertEqual(config.prompt, BASE_PROMPT)
        self.assertFalse(config.clean_output)
        self.assertIsNone(config.allowed_categories)
        self.assertIsNone(config.custom_client)
    
    def test_config_initialization_with_parameters(self):
        """Test Config initialization with custom parameters."""
        config = Config(
            model_api_key="test_key",
            ncbi_key="test_ncbi",
            model="gpt-4o",
            prompt="Custom prompt",
            clean_output=True,
            allowed_categories=["MEDICAL", "FOOD"],
            custom_client="custom_client_object"
        )
        
        self.assertEqual(config.model_api_key, "test_key")
        self.assertEqual(config.ncbi_key, "test_ncbi")
        self.assertEqual(config.model, "gpt-4o")
        self.assertEqual(config.prompt, "Custom prompt")
        self.assertTrue(config.clean_output)
        self.assertEqual(config.allowed_categories, ["MEDICAL", "FOOD"])
        self.assertEqual(config.custom_client, "custom_client_object")
    
    def test_base_prompt_exists(self):
        """Test that BASE_PROMPT is defined and not empty."""
        from chemsource.config import BASE_PROMPT
        self.assertIsNotNone(BASE_PROMPT)
        self.assertIsInstance(BASE_PROMPT, str)
        self.assertGreater(len(BASE_PROMPT), 0)
        
    def test_base_prompt_contains_expected_content(self):
        """Test that BASE_PROMPT contains expected classification categories."""
        from chemsource.config import BASE_PROMPT
        expected_categories = ["MEDICAL", "ENDOGENOUS", "FOOD", "PERSONAL CARE", "INDUSTRIAL", "INFO"]
        
        for category in expected_categories:
            self.assertIn(category, BASE_PROMPT)


if __name__ == '__main__':
    unittest.main()
