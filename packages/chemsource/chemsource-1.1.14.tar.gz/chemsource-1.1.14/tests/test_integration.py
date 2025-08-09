"""
Integration tests for chemsource package.
These tests verify the package can be imported and basic functionality works.
"""
import unittest
import sys
import os

# Add the src directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPackageIntegration(unittest.TestCase):
    """Integration tests for the chemsource package."""
    
    def test_package_import(self):
        """Test that the package can be imported successfully."""
        try:
            import chemsource
            self.assertTrue(True, "Package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import chemsource package: {e}")
    
    def test_chemsource_class_import(self):
        """Test that the main ChemSource class can be imported."""
        try:
            from chemsource import ChemSource
            self.assertTrue(True, "ChemSource class imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import ChemSource class: {e}")
    
    def test_chemsource_instantiation_without_keys(self):
        """Test that ChemSource can be instantiated without API keys."""
        try:
            from chemsource import ChemSource
            chem = ChemSource()
            self.assertIsNotNone(chem, "ChemSource instance created successfully")
        except Exception as e:
            self.fail(f"Failed to create ChemSource instance: {e}")
    
    def test_config_module_import(self):
        """Test that configuration module can be imported."""
        try:
            from chemsource.config import Config, BASE_PROMPT
            config = Config()
            self.assertIsNotNone(BASE_PROMPT)
            self.assertIsInstance(BASE_PROMPT, str)
        except ImportError as e:
            self.fail(f"Failed to import Config class: {e}")
    
    def test_exceptions_module_import(self):
        """Test that exceptions module can be imported."""
        try:
            from chemsource.exceptions import (
                PubMedSearchXMLParseError,
                WikipediaRetrievalError
            )
            self.assertTrue(True, "Exceptions imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import exceptions: {e}")
    
    def test_classifier_module_import(self):
        """Test that classifier module can be imported."""
        try:
            from chemsource.classifier import classify
            self.assertTrue(callable(classify), "Classify function is callable")
        except ImportError as e:
            self.fail(f"Failed to import classifier module: {e}")
    
    def test_retriever_module_import(self):
        """Test that retriever module can be imported."""
        try:
            from chemsource.retriever import pubmed_retrieve, wikipedia_retrieve
            self.assertTrue(callable(pubmed_retrieve), "pubmed_retrieve is callable")
            self.assertTrue(callable(wikipedia_retrieve), "wikipedia_retrieve is callable")
        except ImportError as e:
            self.fail(f"Failed to import retriever module: {e}")
    
    def test_package_version_accessible(self):
        """Test that package version information is accessible."""
        try:
            import chemsource
            # Check if __version__ is defined
            if hasattr(chemsource, '__version__'):
                self.assertIsInstance(chemsource.__version__, str)
            else:
                # If no version is defined, that's also acceptable
                self.assertTrue(True, "Package imported without version info")
        except Exception as e:
            self.fail(f"Error accessing package version: {e}")
    
    def test_base_functionality_without_api_calls(self):
        """Test basic functionality that doesn't require API calls."""
        try:
            from chemsource import ChemSource
            from chemsource.config import Config
            
            # Test config creation
            config = Config(
                model="gpt-4o-mini",
                clean_output=True,
                allowed_categories=["MEDICAL", "FOOD"]
            )
            
            # Test ChemSource creation with config parameters
            chem = ChemSource(
                model="gpt-3.5-turbo",
                clean_output=False,
                allowed_categories=["MEDICAL"]
            )
            
            # Verify parameters were set correctly
            self.assertEqual(chem.model, "gpt-3.5-turbo")
            self.assertFalse(chem.clean_output)
            self.assertEqual(chem.allowed_categories, ["MEDICAL"])
            
        except Exception as e:
            self.fail(f"Error in basic functionality test: {e}")


class TestQuickInstallVerification(unittest.TestCase):
    """Quick tests to verify package installation and basic setup."""
    
    def test_all_modules_importable(self):
        """Test that all main modules can be imported."""
        modules_to_test = [
            'chemsource',
            'chemsource.config',
            'chemsource.classifier', 
            'chemsource.retriever',
            'chemsource.exceptions',
            'chemsource.chemsource'
        ]
        
        for module_name in modules_to_test:
            with self.subTest(module=module_name):
                try:
                    __import__(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")
    
    def test_dependencies_available(self):
        """Test that required dependencies are available."""
        dependencies = [
            'openai',
            'requests',
            'lxml',
            'wikipedia',
            'spellchecker'
        ]
        
        for dep in dependencies:
            with self.subTest(dependency=dep):
                try:
                    __import__(dep)
                except ImportError as e:
                    self.fail(f"Required dependency {dep} not available: {e}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
