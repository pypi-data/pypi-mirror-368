"""
chemsource: A tool for classifying novel drugs and health-related chemicals by origin.

This package provides functionality to classify chemical compounds using AI models
and retrieve chemical information from various sources including PubMed and Wikipedia.

Classes:
    ChemSource: Main class for chemical compound classification and information retrieval.

Version:
    1.1.15
"""

__version__ = "1.1.15"
__author__ = "Prajit Rajkumar"
__email__ = "prajkumar@ucsd.edu"

from .chemsource import ChemSource

__all__ = ["ChemSource"]