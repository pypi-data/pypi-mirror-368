"""
Tests for the retriever module.
"""
import unittest
from unittest.mock import patch, MagicMock
from chemsource.retriever import pubmed_retrieve, wikipedia_retrieve
from chemsource.exceptions import (
    PubMedSearchXMLParseError,
    WikipediaRetrievalError
)


class TestRetriever(unittest.TestCase):
    """Test cases for the retriever module."""
    
    @patch('chemsource.retriever.r.get')
    def test_get_pubmed_info_success(self, mock_get):
        """Test successful PubMed information retrieval."""
        # Mock search response
        search_response = MagicMock()
        search_response.content = b'''
        <eSearchResult>
            <Count>2</Count>
            <QueryKey>1</QueryKey>
            <WebEnv>test_web_env</WebEnv>
            <IdList>
                <Id>12345</Id>
                <Id>67890</Id>
            </IdList>
        </eSearchResult>
        '''
        
        # Mock abstract response
        abstract_response = MagicMock()
        abstract_response.content = b'''
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <Abstract>
                            <AbstractText>Test abstract about aspirin.</AbstractText>
                        </Abstract>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        '''
        
        mock_get.side_effect = [search_response, abstract_response]
        
        result = pubmed_retrieve("aspirin", ncbikey="test_key")
        
        self.assertIsNotNone(result)
        self.assertIn("Test abstract about aspirin", result)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('chemsource.retriever.r.get')
    def test_get_pubmed_info_no_results(self, mock_get):
        """Test PubMed retrieval with no search results."""
        search_response = MagicMock()
        search_response.content = b'''
        <eSearchResult>
            <Count>0</Count>
            <IdList>
            </IdList>
            <WebEnv>NCID_1_123456789_130.14.22.76_9001_1234567890_123456789</WebEnv>
            <QueryKey>1</QueryKey>
        </eSearchResult>
        '''
        
        mock_get.return_value = search_response
        
        result = pubmed_retrieve("nonexistent_compound", ncbikey="test_key")
        
        self.assertEqual(result, 'NO_RESULTS')  # Should return 'NO_RESULTS' for zero count
        self.assertEqual(mock_get.call_count, 1)
    
    @patch('chemsource.retriever.r.get')
    def test_get_pubmed_info_xml_parse_error(self, mock_get):
        """Test PubMed retrieval with XML parsing error."""
        search_response = MagicMock()
        search_response.content = b"Invalid XML"
        
        mock_get.return_value = search_response
        
        with self.assertRaises(PubMedSearchXMLParseError):
            pubmed_retrieve("aspirin", ncbikey="test_key")
    
    @patch('chemsource.retriever.r.get')
    def test_get_pubmed_info_request_failure(self, mock_get):
        """Test PubMed retrieval with request failure."""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(PubMedSearchXMLParseError):
            pubmed_retrieve("aspirin", ncbikey="test_key")
    
    @patch('chemsource.retriever.wikipedia.page')
    def test_get_wikipedia_info_success(self, mock_page):
        """Test successful Wikipedia information retrieval."""
        mock_wiki_page = MagicMock()
        mock_wiki_page.content = "Aspirin is a medication used to reduce pain, fever, or inflammation."
        mock_page.return_value = mock_wiki_page
        
        result = wikipedia_retrieve("aspirin")
        
        self.assertIsNotNone(result)
        self.assertIn("Aspirin is a medication", result)
        mock_page.assert_called_once_with("aspirin", auto_suggest=False)
    
    @patch('chemsource.retriever.wikipedia.page')
    def test_get_wikipedia_info_page_not_found(self, mock_page):
        """Test Wikipedia retrieval with page not found."""
        from wikipedia.exceptions import DisambiguationError, PageError
        
        mock_page.side_effect = PageError("Page not found")
        
        with self.assertRaises(WikipediaRetrievalError):
            wikipedia_retrieve("nonexistent_compound")
    
    @patch('chemsource.retriever.wikipedia.page')
    def test_get_wikipedia_info_disambiguation(self, mock_page):
        """Test Wikipedia retrieval with disambiguation error."""
        from wikipedia.exceptions import DisambiguationError
        
        mock_page.side_effect = DisambiguationError("Multiple pages", ["option1", "option2"])
        
        with self.assertRaises(WikipediaRetrievalError):
            wikipedia_retrieve("ambiguous_term")
    
    @patch('chemsource.retriever.wikipedia.page')
    def test_get_wikipedia_info_general_exception(self, mock_page):
        """Test Wikipedia retrieval with general exception."""
        mock_page.side_effect = Exception("General error")
        
        with self.assertRaises(WikipediaRetrievalError):
            wikipedia_retrieve("aspirin")


if __name__ == '__main__':
    unittest.main()
