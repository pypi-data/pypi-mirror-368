#!/usr/bin/env python3
"""
Unit tests for the chemsource.classifier module.

This module tests the AI classification functionality of the chemsource package
with various configurations and edge cases.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from spellchecker import SpellChecker

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chemsource.classifier import classify


class TestClassifier(unittest.TestCase):
    """Test cases for the classifier module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_response = Mock()
        self.mock_response.choices = [Mock()]
        self.mock_response.choices[0].message = Mock()
        
        self.mock_client = Mock()
        self.mock_client.chat.completions.create.return_value = self.mock_response

    def test_classify_basic_functionality(self):
        """Test basic classification functionality."""
        # Mock the OpenAI response
        self.mock_response.choices[0].message.content = "MEDICAL"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            result = classify(
                name="aspirin",
                input_text="pain relief medication",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: "
            )
        
        self.assertEqual(result, "MEDICAL")
        self.mock_client.chat.completions.create.assert_called_once()

    def test_classify_custom_client(self):
        """Test classification with custom client."""
        self.mock_response.choices[0].message.content = "PHARMACEUTICAL"
        
        result = classify(
            name="ibuprofen",
            input_text="anti-inflammatory drug",
            custom_client=self.mock_client,
            baseprompt="Classify COMPOUND_NAME: "
        )
        
        self.assertEqual(result, "PHARMACEUTICAL")
        # Verify that the custom client was used and message role was "user"
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['messages'][0]['role'], 'user')

    def test_classify_standard_client_message_role(self):
        """Test that standard client uses 'system' message role."""
        self.mock_response.choices[0].message.content = "FOOD"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            classify(
                name="glucose",
                input_text="sugar",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: "
            )
        
        # Verify that the standard client uses "system" role
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['messages'][0]['role'], 'system')

    def test_classify_clean_output_true(self):
        """Test classification with clean_output=True."""
        self.mock_response.choices[0].message.content = "MEDICAL, PHARMACEUTICAL"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            result = classify(
                name="aspirin",
                input_text="pain relief",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                clean_output=True,
                allowed_categories=["MEDICAL", "PHARMACEUTICAL", "FOOD"]
            )
        
        self.assertEqual(result, ["MEDICAL", "PHARMACEUTICAL"])

    def test_classify_clean_output_without_allowed_categories(self):
        """Test that clean_output=True without allowed_categories raises ValueError."""
        with self.assertRaises(ValueError) as context:
            classify(
                name="aspirin",
                baseprompt="Classify COMPOUND_NAME: ",
                clean_output=True,
                custom_client=self.mock_client  # Use mock client to avoid API key requirement
            )
        
        self.assertIn("allowed_categories must be provided", str(context.exception))

    def test_classify_with_spell_checker(self):
        """Test classification with spell checker correction."""
        self.mock_response.choices[0].message.content = "MEDCAL, PHARMACEUTICL"  # Misspelled
        
        # Create a mock spell checker that returns corrected words
        mock_spell_checker = Mock()
        mock_spell_checker.correction = Mock(side_effect=lambda word: {
            "MEDCAL": "MEDICAL", 
            "PHARMACEUTICL": "PHARMACEUTICAL"
        }.get(word, word))
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            result = classify(
                name="aspirin",
                input_text="pain relief",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                clean_output=True,
                allowed_categories=["MEDICAL", "PHARMACEUTICAL", "FOOD"],
                spell_checker=mock_spell_checker
            )
        
        self.assertEqual(result, ["MEDICAL", "PHARMACEUTICAL"])

    def test_classify_deepseek_model(self):
        """Test classification with DeepSeek model."""
        self.mock_response.choices[0].message.content = "CHEMICAL"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client) as mock_openai:
            result = classify(
                name="benzene",
                input_text="organic compound",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                model="deepseek-chat"
            )
        
        # Verify DeepSeek API base URL was used
        mock_openai.assert_called_with(
            api_key="test_key",
            base_url="https://api.deepseek.com"
        )
        self.assertEqual(result, "CHEMICAL")

    def test_classify_max_length_truncation(self):
        """Test that prompts are truncated to max_length."""
        long_input = "A" * 1000  # Very long input text
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            classify(
                name="compound",
                input_text=long_input,
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME with info: ",
                max_length=50  # Small max length
            )
        
        # Check that the prompt was truncated
        call_args = self.mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]['messages'][0]['content']
        self.assertLessEqual(len(prompt_content), 50)

    def test_classify_allowed_categories_filtering(self):
        """Test that output is filtered by allowed_categories."""
        self.mock_response.choices[0].message.content = "MEDICAL, UNKNOWN_CATEGORY, FOOD"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            result = classify(
                name="compound",
                input_text="test",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                clean_output=True,
                allowed_categories=["MEDICAL", "FOOD"]  # UNKNOWN_CATEGORY not allowed
            )
        
        # Only allowed categories should be returned
        self.assertEqual(result, ["MEDICAL", "FOOD"])
        self.assertNotIn("UNKNOWN_CATEGORY", result)

    def test_classify_case_insensitive_filtering(self):
        """Test that allowed_categories filtering is case-insensitive."""
        self.mock_response.choices[0].message.content = "medical, FOOD, Chemical"
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            result = classify(
                name="compound",
                input_text="test",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                clean_output=True,
                allowed_categories=["MEDICAL", "FOOD", "CHEMICAL"]
            )
        
        # All categories should match despite case differences
        self.assertEqual(len(result), 3)

    def test_classify_prompt_construction(self):
        """Test that prompts are constructed correctly."""
        baseprompt = "Please classify COMPOUND_NAME with description: "
        
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            classify(
                name="glucose",
                input_text="simple sugar",
                api_key="test_key",
                baseprompt=baseprompt
            )
        
        # Verify the prompt was constructed properly
        call_args = self.mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]['messages'][0]['content']
        
        expected_prompt = "Please classify glucose with description: simple sugar"
        self.assertEqual(prompt_content, expected_prompt)

    def test_classify_model_parameters(self):
        """Test that model parameters are passed correctly."""
        with patch('chemsource.classifier.OpenAI', return_value=self.mock_client):
            classify(
                name="compound",
                input_text="test",
                api_key="test_key",
                baseprompt="Classify COMPOUND_NAME: ",
                model="gpt-3.5-turbo",
                temperature=0.5,
                top_p=0.9
            )
        
        # Verify model parameters were passed
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], "gpt-3.5-turbo")
        self.assertEqual(call_args[1]['temperature'], 0.5)
        self.assertEqual(call_args[1]['top_p'], 0.9)
        self.assertEqual(call_args[1]['stream'], False)


if __name__ == '__main__':
    unittest.main()
