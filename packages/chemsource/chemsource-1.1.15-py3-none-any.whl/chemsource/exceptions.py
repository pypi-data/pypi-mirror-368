"""
Custom exceptions for the chemsource package.

This module defines specific exceptions that can be raised during
chemical information retrieval and processing operations.
"""


class PubMedSearchXMLParseError(Exception):
    """
    Raised when unable to parse XML response from PubMed search API.
    
    This exception is raised when the XML response from the PubMed search API
    cannot be parsed, typically due to malformed XML or network issues.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to parse XML response from PubMed search API") -> None:
        self.message = message
        super().__init__(message)


class PubMedAbstractXMLParseError(Exception):
    """
    Raised when unable to parse XML response from PubMed abstract retrieval API.
    
    This exception is raised when the XML response from the PubMed abstract
    retrieval API cannot be parsed.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to parse XML response from PubMed abstract retrieval API") -> None:
        self.message = message
        super().__init__(message)


class PubMedSearchResultsError(Exception):
    """
    Raised when unable to retrieve search result count from PubMed search response.
    
    This exception is raised when the search result count cannot be extracted
    from the PubMed search response XML.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to retrieve search result count from PubMed search response") -> None:
        self.message = message
        super().__init__(message)


class PubMedAbstractRetrievalError(Exception):
    """
    Raised when unable to retrieve abstracts from PubMed XML response.
    
    This exception is raised when abstract text cannot be extracted from
    the PubMed XML response.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to retrieve abstracts from PubMed XML response") -> None:
        self.message = message
        super().__init__(message)


class PubMedAbstractConcatenationError(Exception):
    """
    Raised when unable to concatenate PubMed abstract texts.
    
    This exception is raised when there's an error joining multiple
    PubMed abstract texts into a single string.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to concatenate PubMed abstract texts") -> None:
        self.message = message
        super().__init__(message)


class WikipediaRetrievalError(Exception):
    """
    Raised when unable to retrieve content from Wikipedia.
    
    This exception is raised when Wikipedia content cannot be retrieved,
    typically due to page not found or network issues.
    
    Args:
        message (str): The error message. Defaults to a standard message.
    """
    def __init__(self, message: str = "Failed to retrieve content from Wikipedia") -> None:
        self.message = message
        super().__init__(message)