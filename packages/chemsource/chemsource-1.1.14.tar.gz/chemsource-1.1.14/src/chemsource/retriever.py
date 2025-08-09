"""
Information retrieval module for chemsource.

This module handles the retrieval of information from various sources such as
PubMed and Wikipedia for chemical research purposes.
"""

from typing import Optional, Tuple
from .exceptions import (
    PubMedSearchXMLParseError, 
    PubMedSearchResultsError,
    PubMedAbstractXMLParseError, 
    PubMedAbstractRetrievalError, 
    PubMedAbstractConcatenationError,
    WikipediaRetrievalError
)

from lxml import etree
import re
import requests as r
import wikipedia

#: Default parameters for PubMed search API
SEARCH_PARAMS = {'db': 'pubmed',
                 'term': '',
                 'retmax': '3',
                 'usehistory': 'n',
                 'sort': 'relevance',
                 'api_key': None
                 }

#: Default parameters for PubMed abstract retrieval API
XML_RETRIEVAL_PARAMS = {'db': 'pubmed',
                        'query_key': '1',
                        'WebEnv': '',
                        'rettype': 'abstract',
                        'retmax': '3',
                        'api_key': None
                        }


def retrieve(name: str, priority: str = "WIKIPEDIA", single_source: bool = False, ncbikey: Optional[str] = None) -> Tuple[str, str]:
    """
    Retrieve information about a chemical compound from various sources.
    
    This function retrieves information about a chemical compound from multiple sources
    including Wikipedia and PubMed, with configurable priority and source selection.
    
    Args:
        name (str): The name of the chemical compound to look up.
        priority (str, optional): Priority source for information retrieval. 
                                Options: "WIKIPEDIA", "PUBMED". Defaults to "WIKIPEDIA".
        single_source (bool, optional): Whether to use only the priority source. Defaults to False.
        ncbikey (str, optional): API key for NCBI/PubMed access.
    
    Returns:
        Tuple[str, str]: A tuple containing (source, content) where source indicates
                        the data source used and content contains the retrieved information.
    
    Raises:
        PubMedSearchXMLParseError: If PubMed search XML cannot be parsed.
        PubMedSearchResultsError: If search results cannot be retrieved from PubMed.
        PubMedAbstractXMLParseError: If PubMed abstract XML cannot be parsed.
        PubMedAbstractRetrievalError: If abstracts cannot be retrieved from PubMed.
        PubMedAbstractConcatenationError: If abstract texts cannot be concatenated.
        WikipediaRetrievalError: If Wikipedia content cannot be retrieved.
        
    Example:
        >>> source, content = retrieve("aspirin")
        >>> print(f"Retrieved from {source}: {content[:100]}...")
    """
    if (priority == "WIKIPEDIA" and not single_source):
        try:
            description = wikipedia_retrieve(name)
            info_source = "WIKIPEDIA"
        except:
            try:
                description = pubmed_retrieve(name, ncbikey)
                info_source = "PUBMED"
            except:
                description = None
                info_source = None
    elif (priority == "PUBMED" and not single_source):
        try:
            description = pubmed_retrieve(name, ncbikey)
            info_source = "PUBMED"
        except:
            try:
                description = wikipedia_retrieve(name)
                info_source = "WIKIPEDIA"
            except:
                description = None
                info_source = None
    
    elif (priority == "WIKIPEDIA" and single_source):
        try:
            description = wikipedia_retrieve(name)
            info_source = "WIKIPEDIA"
        except:
            description = None
            info_source = None
    
    elif (priority == "PUBMED" and single_source):
        try:
            description = pubmed_retrieve(name, ncbikey)
            info_source = "PUBMED"
        except:
            description = None
            info_source = None
    
    else:
        raise ValueError("priority must be either WIKIPEDIA or PUBMED" 
                         + "and single_source must be a boolean value")

    return info_source, description
    
def pubmed_retrieve(drug: str, ncbikey: Optional[str] = None) -> str:
    """
    Retrieve abstracts from PubMed for a given compound.
    
    This function searches PubMed for articles related to a chemical compound
    and retrieves the abstracts of the most relevant articles.
    
    Args:
        drug (str): The name of the compound to search for in PubMed.
        ncbikey (str, optional): API key for NCBI/PubMed access for higher rate limits.
    
    Returns:
        str: Concatenated abstract texts from PubMed articles, or 'NO_RESULTS' if no articles found.
        
    Raises:
        PubMedSearchXMLParseError: If the search XML response cannot be parsed.
        PubMedSearchResultsError: If search results cannot be retrieved.
        PubMedAbstractXMLParseError: If abstract XML cannot be parsed.
        PubMedAbstractRetrievalError: If abstracts cannot be retrieved.
        PubMedAbstractConcatenationError: If abstract texts cannot be concatenated.
        
    Example:
        >>> abstracts = pubmed_retrieve("aspirin", ncbikey="your_ncbi_key")
        >>> print(abstracts[:100])
    """
    temp_search_params = SEARCH_PARAMS
    temp_search_params['api_key'] = ncbikey

    if (temp_search_params["api_key"] is None):
        del temp_search_params["api_key"]
    temp_search_params['term'] = drug + '[ti]'

    try:
        xml_content = etree.fromstring(r.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?", 
                                             params=temp_search_params).content)
    except:
        raise PubMedSearchXMLParseError()
    try:
        if (str(xml_content.find(".//Count").text) == "0"):
            return 'NO_RESULTS'
    except:
        raise PubMedSearchResultsError()
    else:
        temp_retrieval_params = XML_RETRIEVAL_PARAMS
        temp_retrieval_params['api_key'] = ncbikey

        if (temp_retrieval_params["api_key"] is None):
            del temp_retrieval_params["api_key"]
        temp_retrieval_params['WebEnv'] = xml_content.find(".//WebEnv").text
        try:
            retrieval_content = etree.fromstring(r.get(('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'), 
                                                       params=temp_retrieval_params
                                                       ).content)
        except:
            raise PubMedAbstractXMLParseError()
        try:
            abstracts = retrieval_content.findall(".//AbstractText")
        except:
            raise PubMedAbstractRetrievalError()
        result = ''
        try:
            for abstract in abstracts:
                result = result + ' ' + abstract.text
        except:
            raise PubMedAbstractConcatenationError()
        return result


def wikipedia_retrieve(drug: str) -> str:
    """
    Retrieve content from Wikipedia for a given compound.
    
    This function fetches the Wikipedia page content for a chemical compound
    and processes it by removing newlines, tabs, and extra spaces.
    
    Args:
        drug (str): The name of the compound to look up on Wikipedia.
    
    Returns:
        str: The processed Wikipedia content with cleaned formatting.
        
    Raises:
        WikipediaRetrievalError: If Wikipedia content cannot be retrieved.
        
    Example:
        >>> content = wikipedia_retrieve("aspirin")
        >>> print(content[:100])
    """
    try:
        description = wikipedia.page(drug, auto_suggest=False).content
        description = description.replace('\n', ' ')
        description = description.replace('\t', ' ')
        description = ' '.join(description.split())
        return description
    except Exception as e:
        raise WikipediaRetrievalError(f"Failed to retrieve Wikipedia content for '{drug}': {str(e)}")