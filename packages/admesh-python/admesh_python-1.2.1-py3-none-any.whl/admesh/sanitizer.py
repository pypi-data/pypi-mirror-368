# File generated for AdMesh PII sanitization functionality

"""
PII sanitization module for detecting and removing personally identifiable information.
All processing is done locally without external API calls for privacy preservation.
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from .patterns import (
    COMPILED_PATTERNS, SINGLE_PATTERNS, is_valid_name, normalize_gender, extract_goal_text
)

class PIISanitizer:
    """
    Handles detection and removal of personally identifiable information from user input.
    
    This class provides methods to:
    - Detect names, emails, and phone numbers
    - Extract contextual information (age, gender, goals)
    - Remove PII while preserving context
    - Maintain privacy by processing everything locally
    """
    
    def __init__(self):
        """Initialize the PII sanitizer with compiled patterns."""
        self.name_patterns = COMPILED_PATTERNS['names']
        self.phone_patterns = COMPILED_PATTERNS['phones']
        self.age_patterns = COMPILED_PATTERNS['ages']
        self.gender_patterns = COMPILED_PATTERNS['genders']
        self.goal_patterns = COMPILED_PATTERNS['goals']
        self.email_pattern = SINGLE_PATTERNS['email']
    
    def detect_names(self, text: str) -> List[str]:
        """
        Detect names in the input text using multiple patterns.

        Args:
            text: Input text to analyze

        Returns:
            List of detected names
        """
        names = []

        for pattern in self.name_patterns:
            matches = pattern.findall(text)
            for match in matches:
                # Handle both single groups and tuples
                name = match if isinstance(match, str) else match[0] if match else ""
                if name and is_valid_name(name):
                    # Additional check to avoid common phrases
                    if not any(phrase in name.lower() for phrase in ['the ', 'a ', 'an ']):
                        names.append(name.strip())

        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)

        return unique_names
    
    def detect_emails(self, text: str) -> List[str]:
        """
        Detect email addresses in the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected email addresses
        """
        matches = self.email_pattern.findall(text)
        return list(set(matches))  # Remove duplicates
    
    def detect_phones(self, text: str) -> List[str]:
        """
        Detect phone numbers in the input text using multiple patterns.

        Args:
            text: Input text to analyze

        Returns:
            List of detected phone numbers
        """
        phones = []
        found_positions = set()

        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                start, end = match.span()
                # Skip if we already found a phone number at this position
                if any(start <= pos < end or pos <= start < pos_end for pos, pos_end in found_positions):
                    continue

                phone = match.group(1) if match.groups() else match.group(0)
                if phone:
                    phones.append(phone)
                    found_positions.add((start, end))

        return phones
    
    def extract_age(self, text: str) -> Optional[int]:
        """
        Extract age information from the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected age as integer, or None if not found
        """
        for pattern in self.age_patterns:
            match = pattern.search(text)
            if match:
                try:
                    age = int(match.group(1))
                    # Validate reasonable age range
                    if 13 <= age <= 100:
                        return age
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_gender(self, text: str) -> Optional[str]:
        """
        Extract gender information from the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Normalized gender string, or None if not found
        """
        for pattern in self.gender_patterns:
            match = pattern.search(text)
            if match:
                gender = match.group(1)
                return normalize_gender(gender)
        
        return None
    
    def extract_goal(self, text: str) -> Optional[str]:
        """
        Extract goal/purpose information from the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extracted goal text, or None if not found
        """
        for pattern in self.goal_patterns:
            match = pattern.search(text)
            if match:
                goal_text = match.group(1)
                cleaned_goal = extract_goal_text(goal_text)
                if cleaned_goal and len(cleaned_goal) > 3:
                    return cleaned_goal
        
        return None
    
    def remove_pii(self, text: str, detected_pii: Dict[str, Union[List[str], str]]) -> str:
        """
        Remove detected PII from the input text.
        
        Args:
            text: Original input text
            detected_pii: Dictionary containing detected PII
            
        Returns:
            Text with PII removed
        """
        sanitized_text = text
        
        # Remove names
        if detected_pii.get('names'):
            for name in detected_pii['names']:
                # Use word boundaries to avoid partial matches
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                sanitized_text = pattern.sub('[NAME]', sanitized_text)
        
        # Remove emails
        if detected_pii.get('emails'):
            for email in detected_pii['emails']:
                sanitized_text = sanitized_text.replace(email, '[EMAIL]')
        
        # Remove phones
        if detected_pii.get('phones'):
            for phone in detected_pii['phones']:
                # Remove the original phone format
                sanitized_text = sanitized_text.replace(phone, '[PHONE]')
        
        # Clean up multiple spaces and normalize
        sanitized_text = re.sub(r'\s+', ' ', sanitized_text).strip()
        
        return sanitized_text
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, Dict, List]]:
        """
        Perform complete PII analysis on the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
            - sanitized_text: Text with PII removed
            - detected_pii: All detected PII information
            - extracted_context: Contextual information (age, gender, goal)
        """
        # Detect all PII
        names = self.detect_names(text)
        emails = self.detect_emails(text)
        phones = self.detect_phones(text)
        
        # Extract context
        age = self.extract_age(text)
        gender = self.extract_gender(text)
        goal = self.extract_goal(text)
        
        # Prepare detected PII dictionary
        detected_pii = {
            'names': names,
            'emails': emails,
            'phones': phones
        }
        
        # Remove PII from text
        sanitized_text = self.remove_pii(text, detected_pii)
        
        # Prepare extracted context
        extracted_context = {
            'age': age,
            'gender': gender,
            'goal': goal
        }
        
        return {
            'sanitized_text': sanitized_text,
            'detected_pii': detected_pii,
            'extracted_context': extracted_context
        }
