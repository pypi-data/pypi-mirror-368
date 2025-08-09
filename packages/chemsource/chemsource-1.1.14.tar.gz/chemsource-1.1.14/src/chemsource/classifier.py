"""
Chemical classification module for chemsource.

This module provides AI-powered classification functionality for chemical
entities and compounds.
"""

from typing import Optional, List, Union, Any
from openai import OpenAI
from spellchecker import SpellChecker


def classify(name: str,
             input_text: Optional[str] = None, 
             api_key: Optional[str] = None, 
             baseprompt: Optional[str] = None,
             model: str = 'gpt-4-0125-preview', 
             temperature: float = 0,
             top_p: float = 0,
             max_length: int = 250000,
             clean_output: bool = False,
             allowed_categories: Optional[List[str]] = None,
             custom_client: Optional[Any] = None,
             spell_checker: Optional[SpellChecker] = None) -> Union[str, List[str]]:
    """
    Classify a chemical compound using an AI language model.
    
    This function takes a chemical compound name and additional information,
    then uses an AI model to classify it into predefined categories.
    
    Args:
        name (str): The name of the chemical compound to classify.
        input_text (str, optional): Additional information about the compound.
        api_key (str, optional): API key for the language model service.
        baseprompt (str, optional): Base prompt template for classification.
        model (str, optional): Name of the language model to use. Defaults to 'gpt-4-0125-preview'.
        temperature (float, optional): Temperature parameter for model creativity. Defaults to 0.
        top_p (float, optional): Top-p parameter for nucleus sampling. Defaults to 0.
        max_length (int, optional): Maximum length of the prompt in characters. Defaults to 250000.
        clean_output (bool, optional): Whether to clean and validate the output. Defaults to False.
        allowed_categories (List[str], optional): List of allowed categories for filtering output.
        custom_client (Any, optional): Custom OpenAI client instance.
        spell_checker (SpellChecker, optional): Spell checker instance for output correction.
    
    Returns:
        Union[str, List[str]]: Either the raw model output (if clean_output=False) or 
                              a cleaned list of categories (if clean_output=True).
    
    Raises:
        ValueError: If clean_output is True but allowed_categories is None.
        
    Example:
        >>> classify("aspirin", "pain relief medication", api_key="your_key")
        "MEDICAL"
        
        >>> classify("aspirin", "pain relief medication", api_key="your_key", 
        ...          clean_output=True, allowed_categories=["MEDICAL", "FOOD"])
        ["MEDICAL"]
    """
    
    if custom_client is not None:
        client = custom_client
    elif model == "deepseek-chat":
        client = OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com"
                        )
    else:
        client = OpenAI(
                        api_key=api_key
                        )

    if clean_output and allowed_categories is None:
        raise ValueError("If clean_output is True, a list in allowed_categories must be provided to filter the output.")
    


    split_base = baseprompt.split("COMPOUND_NAME")
    prompt = split_base[0] + str(name) + split_base[1] + str(input_text)
    prompt = prompt[:max_length]

    # Use user role for custom clients (like Gemini) that may not support system messages
    message_role = "user" if custom_client is not None else "system"
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": message_role, "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        stream=False
        )
    if clean_output == False:
        return response.choices[0].message.content
    else:
        cleaned_response_string = response.choices[0].message.content.replace("\n", " ").replace("  ", " ").strip()
        classification_list = cleaned_response_string.split(",")
        classification_list = [item.strip().replace("  ", " ") for item in classification_list]
        
        if allowed_categories is not None:
            updated_classification_list = []
            for item in classification_list:
                if spell_checker is not None:
                    updated_item = spell_checker.correction(item)
                    if updated_item in allowed_categories:
                        updated_classification_list.append(updated_item)
                else:
                    # Fallback to original item if no spell checker provided
                    if item.upper() in [cat.upper() for cat in allowed_categories]:
                        updated_classification_list.append(item)
            return updated_classification_list
        else:
            return classification_list
