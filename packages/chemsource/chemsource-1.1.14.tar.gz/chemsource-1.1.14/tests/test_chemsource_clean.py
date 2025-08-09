"""
Tests for the main ChemSource class.
"""
import unittest
from unittest.mock import patch, MagicMock
from chemsource.chemsource import ChemSource
from chemsource.config import Config


class TestChemSource(unittest.TestCase):
    """Test cases for the ChemSource class."""
    
    def test_chemsource_initialization_defaults(self):
        """Test ChemSource initialization with default values."""
        chem = ChemSource()
        
        self.assertIsInstance(chem, Config)  # ChemSource inherits from Config
        self.assertEqual(chem.model, "gpt-4-0125-preview")
        self.assertEqual(chem.temperature, 0)
        self.assertFalse(chem.clean_output)
        self.assertIsNone(chem.allowed_categories)
        self.assertIsNone(chem.custom_client)
    
    def test_chemsource_initialization_with_parameters(self):
        """Test ChemSource initialization with custom parameters."""
        chem = ChemSource(
            model_api_key="test_key",
            model="gpt-3.5-turbo",
            temperature=0.5,
            clean_output=True,
            allowed_categories=["MEDICAL", "CHEMICAL"]
        )
        
        self.assertEqual(chem.model_api_key, "test_key")
        self.assertEqual(chem.model, "gpt-3.5-turbo")
        self.assertEqual(chem.temperature, 0.5)
        self.assertTrue(chem.clean_output)
        self.assertEqual(chem.allowed_categories, ["MEDICAL", "CHEMICAL"])


if __name__ == '__main__':
    unittest.main()
