"""
Main chemsource module for chemical compound classification and information retrieval.

This module provides the main ChemSource class that combines configuration management,
information retrieval, and AI-powered classification of chemical compounds.
"""

from typing import Optional, List, Tuple, Union, Any
from .config import Config
from .config import BASE_PROMPT

from .classifier import classify as cls
from .retriever import retrieve as ret

from spellchecker import SpellChecker


class ChemSource(Config):
    """
    Main class for chemical compound classification and information retrieval.
    
    chemsource combines configuration management, information retrieval from multiple sources
    (PubMed, Wikipedia), and AI-powered classification of chemical compounds. It extends
    the Config class to provide a complete solution for chemical information processing.
    
    Args:
        model_api_key (str, optional): API key for the language model service.
        model (str, optional): Name of the language model to use. Defaults to "gpt-4o".
        ncbi_key (str, optional): API key for NCBI/PubMed access.
        prompt (str, optional): Custom prompt template. Defaults to BASE_PROMPT.
        temperature (float, optional): Temperature parameter for model creativity. Defaults to 0.
        max_tokens (int, optional): Maximum number of tokens for model context. Defaults to 250000.
        clean_output (bool, optional): Whether to clean and validate output. Defaults to False.
        allowed_categories (List[str], optional): List of allowed categories for filtering. Defaults to None.
        custom_client (Any, optional): Custom OpenAI client instance. Defaults to None.
    
    Raises:
        ValueError: If clean_output is True but allowed_categories is None or empty.
        TypeError: If allowed_categories is not a list when clean_output is True.
        
    Attributes:
        spell_checker (SpellChecker): Spell checker instance for output correction (when clean_output is enabled).
        clean_output (bool): Whether output cleaning is enabled.
        allowed_categories (List[str]): The allowed categories list.
        custom_client (Any): The custom client instance.
    
    Example:
        >>> chem = ChemSource(model_api_key="your_key")
        >>> info, classification = chem.chemsource("aspirin")
        >>> print(classification)
        "MEDICAL"
    """
    
    def __init__(self, 
                 model_api_key: Optional[str] = None, 
                 model: str = "gpt-4o", 
                 ncbi_key: Optional[str] = None, 
                 prompt: str = BASE_PROMPT,
                 temperature: float = 0,
                 max_tokens: int = 250000,
                 clean_output: bool = False,
                 allowed_categories: Optional[List[str]] = None,
                 custom_client: Optional[Any] = None) -> None:
        super().__init__(model_api_key=model_api_key, 
                         model=model, 
                         ncbi_key=ncbi_key,
                         prompt=prompt, 
                         temperature=temperature,
                         max_tokens=max_tokens,
                         clean_output=clean_output,
                         allowed_categories=allowed_categories,
                         custom_client=custom_client
                         )
        if clean_output and allowed_categories is None:
            raise ValueError("If clean_output is True, a list in allowed_categories must be provided to filter the output.")
        
        elif clean_output and not isinstance(allowed_categories, list):
            raise TypeError("allowed_categories must be a list when clean_output is True.")
        
        elif clean_output and isinstance(allowed_categories, list) and len(allowed_categories) == 0:
            raise ValueError("allowed_categories cannot be an empty list when clean_output is True.")
        
        # Create SpellChecker instance for spell correction when clean_output is enabled
        if clean_output and isinstance(allowed_categories, list) and len(allowed_categories) > 0:
            self.spell_checker = SpellChecker()
            self.spell_checker.word_frequency.load_words(allowed_categories)
        else:
            self.spell_checker = None
            
        self.clean_output = clean_output
        self.allowed_categories = allowed_categories
        self.custom_client = custom_client
    
    def chemsource(self, name: str, priority: str = "WIKIPEDIA", single_source: bool = False) -> Tuple[Tuple[Optional[str], Optional[str]], Optional[str]]:
        """
        Retrieve information and classify a chemical compound.
        
        This is the main method that combines information retrieval and classification.
        It retrieves information about the compound from specified sources and then
        classifies it using the configured AI model.
        
        Args:
            name (str): The name of the chemical compound to process.
            priority (str, optional): Priority source for information retrieval. 
                                    Options: "WIKIPEDIA", "PUBMED". Defaults to "WIKIPEDIA".
            single_source (bool, optional): Whether to use only the priority source. Defaults to False.
        
        Returns:
            Tuple[Tuple[Optional[str], Optional[str]], Optional[str]]: A tuple containing:
                - Information tuple: (source, content)
                - Classification result
        
        Raises:
            ValueError: If model_api_key is not provided.
            
        Example:
            >>> chem = ChemSource(model_api_key="your_key")
            >>> info, classification = chem.chemsource("aspirin")
            >>> print(info[0])  # Source
            >>> print(info[1])  # Content
            >>> print(classification)  # Classification result
        """
        if self.model_api_key is None and self.custom_client is None:
            raise ValueError("Either model_api_key or custom_client must be provided")

        information = ret(name, 
                         priority,
                         single_source, 
                         ncbikey=self.ncbi_key
                         )
        
        if information[1] == "":
            return (None, None), None
        
        return information, cls(name, 
                                information, 
                                self.model_api_key,
                                self.prompt,
                                self.model,
                                self.temperature,
                                self.top_p,
                                self.max_tokens,
                                self.clean_output,
                                self.allowed_categories,
                                self.custom_client,
                                self.spell_checker)

    def classify(self, name: str, information: str) -> Optional[Union[str, List[str]]]:
        """
        Classify a chemical compound based on provided information.
        
        This method classifies a chemical compound using the provided information
        and the configured AI model.
        
        Args:
            name (str): The name of the chemical compound to classify.
            information (str): Information about the compound to use for classification.
        
        Returns:
            Optional[Union[str, List[str]]]: Classification result. Returns None if 
                                           information is empty, otherwise returns a 
                                           string (if clean_output=False) or list of 
                                           strings (if clean_output=True).
        
        Raises:
            ValueError: If neither model_api_key nor custom_client is provided.
            
        Example:
            >>> chem = ChemSource(model_api_key="your_key")
            >>> result = chem.classify("aspirin", "pain relief medication")
            >>> print(result)
            "MEDICAL"
        """
        if self.model_api_key is None and self.custom_client is None:
            raise ValueError("Either model_api_key or custom_client must be provided")
        
        if information == "":
            return None
        
        return cls(name, 
                   information,
                   self.model_api_key,
                   self.prompt,
                   self.model,
                   self.temperature,
                   self.top_p,
                   self.max_tokens,
                   self.clean_output,
                   self.allowed_categories,
                   self.custom_client,
                   self.spell_checker)
    
    def retrieve(self, name: str, priority: str = "WIKIPEDIA", single_source: bool = False) -> Tuple[str, str]:
        """
        Retrieve information about a chemical compound from various sources.
        
        This method retrieves information about a chemical compound from sources
        like Wikipedia and PubMed without performing classification.
        
        Args:
            name (str): The name of the chemical compound to look up.
            priority (str, optional): Priority source for information retrieval. 
                                    Options: "WIKIPEDIA", "PUBMED". Defaults to "WIKIPEDIA".
            single_source (bool, optional): Whether to use only the priority source. Defaults to False.
        
        Returns:
            Tuple[str, str]: A tuple containing (source, content).
            
        Example:
            >>> chem = ChemSource()
            >>> source, content = chem.retrieve("aspirin")
            >>> print(f"Retrieved from {source}: {content[:100]}...")
        """
        return ret(name, 
                   priority, 
                   single_source,
                   ncbikey=self.ncbi_key
                   )