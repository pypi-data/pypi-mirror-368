"""
Tests for the exceptions module.
"""
import unittest
from chemsource.exceptions import (
    PubMedSearchXMLParseError,
    PubMedAbstractXMLParseError,
    PubMedSearchResultsError,
    PubMedAbstractRetrievalError,
    PubMedAbstractConcatenationError,
    WikipediaRetrievalError
)


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions."""
    
    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from Exception."""
        exceptions = [
            PubMedSearchXMLParseError,
            PubMedAbstractXMLParseError,
            PubMedSearchResultsError,
            PubMedAbstractRetrievalError,
            PubMedAbstractConcatenationError,
            WikipediaRetrievalError
        ]
        
        for exc_class in exceptions:
            self.assertTrue(issubclass(exc_class, Exception))
    
    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated with messages."""
        test_message = "Test error message"
        
        exceptions = [
            PubMedSearchXMLParseError(test_message),
            PubMedAbstractXMLParseError(test_message),
            PubMedSearchResultsError(test_message),
            PubMedAbstractRetrievalError(test_message),
            PubMedAbstractConcatenationError(test_message),
            WikipediaRetrievalError(test_message)
        ]
        
        for exc in exceptions:
            self.assertEqual(str(exc), test_message)
    
    def test_exception_raising(self):
        """Test that exceptions can be raised and caught."""
        test_message = "Test error"
        
        with self.assertRaises(PubMedSearchXMLParseError) as context:
            raise PubMedSearchXMLParseError(test_message)
        self.assertEqual(str(context.exception), test_message)
        
        with self.assertRaises(WikipediaRetrievalError) as context:
            raise WikipediaRetrievalError(test_message)
        self.assertEqual(str(context.exception), test_message)


if __name__ == '__main__':
    unittest.main()
