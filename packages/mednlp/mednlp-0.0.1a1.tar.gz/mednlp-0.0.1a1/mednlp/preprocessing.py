"""
Medical text preprocessing functionality.
"""

import re
from typing import List


class MedicalTextPreprocessor:
    """Basic medical text preprocessing utilities."""
    
    def __init__(self):
        """Initialize the preprocessor."""
        self.abbreviations = {
            'pt': 'patient',
            'hx': 'history',
            'dx': 'diagnosis',
            'tx': 'treatment'
        }
    
    def clean_text(self, text: str) -> str:
        """Remove special characters and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Basic cleaning
        text = re.sub(r'[^\w\s\.\,\-\']', '', text)
        return text
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand common medical abbreviations."""
        for abbr, full in self.abbreviations.items():
            text = re.sub(rf'\b{abbr}\b', full, text, flags=re.IGNORECASE)
        return text
    
    def preprocess(self, text: str) -> str:
        """Apply all preprocessing steps."""
        text = self.clean_text(text)
        text = self.expand_abbreviations(text)
        return text
