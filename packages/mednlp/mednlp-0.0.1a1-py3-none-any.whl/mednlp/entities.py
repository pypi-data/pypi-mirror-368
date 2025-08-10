"""
Medical entity extraction functionality.
"""

from typing import List, Dict, Any
import re


class MedicalEntityExtractor:
    """
    Extract medical entities from text using various methods.
    """
    
    def __init__(self):
        """Initialize the entity extractor."""
        self.medical_patterns = {
            'symptoms': [
                r'\b(chest pain|shortness of breath|fever|headache|nausea)\b',
                r'\b(dizziness|fatigue|cough|sore throat|abdominal pain)\b'
            ],
            'medications': [
                r'\b(aspirin|ibuprofen|acetaminophen|amoxicillin|metformin)\b',
                r'\b(atorvastatin|lisinopril|metoprolol|omeprazole|simvastatin)\b'
            ],
            'conditions': [
                r'\b(diabetes|hypertension|asthma|depression|arthritis)\b',
                r'\b(heart disease|cancer|stroke|obesity|anxiety)\b'
            ]
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medical entities from text using pattern matching.
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            List of extracted entities with type and position information
        """
        entities = []
        
        for entity_type, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'type': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8  # Placeholder confidence score
                    })
        
        return entities
    
    def extract_medications(self, text: str) -> List[str]:
        """Extract medication names from text."""
        medications = []
        for pattern in self.medical_patterns['medications']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            medications.extend(matches)
        return list(set(medications))
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptom descriptions from text."""
        symptoms = []
        for pattern in self.medical_patterns['symptoms']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            symptoms.extend(matches)
        return list(set(symptoms))
