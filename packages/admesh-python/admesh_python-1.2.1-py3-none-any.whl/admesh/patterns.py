# File generated for AdMesh PII sanitization functionality

"""
Regex patterns for PII detection and context extraction.
All patterns are compiled for performance and designed to be privacy-preserving.
"""

import re
from typing import Dict, Pattern

# PII Detection Patterns
NAME_PATTERNS = [
    # "I'm [Name]", "My name is [Name]", "I am [Name]"
    re.compile(r"\b(?:I'?m|my name is|I am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE),
    # "Hi, I'm [Name]", "Hello, I'm [Name]"
    re.compile(r"\b(?:hi|hello|hey),?\s+(?:I'?m|my name is|I am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE),
    # "This is [Name]" - more specific to avoid capturing too much
    re.compile(r"\b(?:this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+here\b", re.IGNORECASE),
]

EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)

PHONE_PATTERNS = [
    # International formats with full number - most specific first
    re.compile(r'(\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4})\b'),
    re.compile(r'(\+\d{1,3}[-\s]?\d{3,14})\b'),
    # US formats
    re.compile(r'(\(\d{3}\)\s?\d{3}[-\s]?\d{4})\b'),
    re.compile(r'\b(\d{3}[-.]?\d{3}[-.]?\d{4})\b'),
    re.compile(r'\b(\d{3}\s\d{3}\s\d{4})\b'),
]

# Context Extraction Patterns
AGE_PATTERNS = [
    # "I'm 27", "I am 27", "27 years old", "27-year-old"
    re.compile(r"\b(?:I'?m|I am)\s+(\d{1,2})\b", re.IGNORECASE),
    re.compile(r"\b(\d{1,2})\s*(?:years?\s*old|yr\s*old|y\.?o\.?)\b", re.IGNORECASE),
    re.compile(r"\b(\d{1,2})[-\s]?year[-\s]?old\b", re.IGNORECASE),
    re.compile(r"\bage[:\s]+(\d{1,2})\b", re.IGNORECASE),
]

GENDER_PATTERNS = [
    # Direct mentions
    re.compile(r"\b(male|female|man|woman|guy|girl|boy|gentleman|lady)\b", re.IGNORECASE),
    # Contextual mentions
    re.compile(r"\b(?:I'?m a|I am a)\s+(male|female|man|woman|guy|girl)\b", re.IGNORECASE),
]

GOAL_PATTERNS = [
    # Action-oriented goals - capture the full phrase including the action
    re.compile(r"\b((?:building|creating|developing|making|working on|starting|launching)\s+(?:a\s+)?[^.!?,]+)", re.IGNORECASE),
    re.compile(r"\b((?:want to|need to|trying to|planning to|looking to)\s+[^.!?,]+)", re.IGNORECASE),
    re.compile(r"\b(?:project|app|website|business|startup|company|tool|platform|service)\s+(?:for|about|that)\s+([^.!?]+)", re.IGNORECASE),
]

# Compiled pattern collections for easy access
COMPILED_PATTERNS: Dict[str, list] = {
    'names': NAME_PATTERNS,
    'phones': PHONE_PATTERNS,
    'ages': AGE_PATTERNS,
    'genders': GENDER_PATTERNS,
    'goals': GOAL_PATTERNS,
}

SINGLE_PATTERNS: Dict[str, Pattern] = {
    'email': EMAIL_PATTERN,
}

# Common words to exclude from name detection (to reduce false positives)
COMMON_WORDS = {
    'about', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did',
    'do', 'does', 'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself',
    'his', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more',
    'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only',
    'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 's', 'same', 'she',
    'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too',
    'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
    'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'you', 'your', 'yours', 'yourself',
    'yourselves', 'hello', 'hi', 'hey', 'thanks', 'thank', 'please', 'yes', 'yeah', 'ok', 'okay'
}

def is_valid_name(name: str) -> bool:
    """
    Validate if a detected name is likely to be a real name.
    Filters out common words and single letters.
    """
    if not name or len(name.strip()) < 2:
        return False
    
    # Check if it's a common word
    if name.lower().strip() in COMMON_WORDS:
        return False
    
    # Check if it contains only letters and spaces
    if not re.match(r'^[A-Za-z\s]+$', name):
        return False
    
    # Check if it's not all uppercase (likely acronym)
    if name.isupper() and len(name) > 3:
        return False
    
    return True

def normalize_gender(gender: str) -> str:
    """
    Normalize gender terms to standard values.
    """
    gender_lower = gender.lower()
    
    if gender_lower in ['male', 'man', 'guy', 'boy', 'gentleman']:
        return 'male'
    elif gender_lower in ['female', 'woman', 'girl', 'lady']:
        return 'female'
    
    return gender_lower

def extract_goal_text(match_text: str) -> str:
    """
    Clean and extract meaningful goal text from regex matches.
    """
    # Remove common prefixes and clean up
    goal = match_text.strip()
    
    # Remove trailing punctuation
    goal = re.sub(r'[.!?]+$', '', goal)
    
    # Limit length to avoid overly long extractions
    if len(goal) > 100:
        goal = goal[:100] + '...'
    
    return goal.strip()
