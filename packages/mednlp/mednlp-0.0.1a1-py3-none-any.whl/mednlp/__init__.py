"""
Medical Natural Language Processing Toolkit

A comprehensive library for processing and analyzing medical text data.
"""

__version__ = "0.0.1a1"
__author__ = "MedNLP Team"
__email__ = "team@mednlp.org"

from .core import MedicalNLP
from .entities import MedicalEntityExtractor
from .preprocessing import MedicalTextPreprocessor

__all__ = [
    "MedicalNLP",
    "MedicalEntityExtractor", 
    "MedicalTextPreprocessor",
]
