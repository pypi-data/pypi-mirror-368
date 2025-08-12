# File generated for AdMesh PII sanitization functionality

"""
Main module for PII sanitization and prompt building functionality.
Provides the primary sanitize_and_build function for the AdMesh Python SDK.
"""

from typing import Dict, Union, Optional
from .sanitizer import PIISanitizer
from .builder import PromptBuilder

def sanitize_and_build(user_input: str) -> Dict[str, Union[str, Dict[str, Optional[Union[str, int]]]]]:
    """
    Sanitizes user input by removing PII and builds a structured prompt.
    
    This function performs the following operations:
    1. Detects and removes personally identifiable information (PII)
    2. Extracts contextual information (age, gender, goals)
    3. Builds a clean, structured prompt for the AdMesh /recommend endpoint
    4. Returns comprehensive analysis results
    
    All processing is done locally without external API calls to ensure privacy.
    
    Args:
        user_input (str): Raw user input containing potential PII
        
    Returns:
        dict: Contains sanitized prompt, removed PII, and extracted context
        
        Structure:
        {
            "prompt": str,  # Clean, structured prompt for recommendations
            "removed": {    # PII that was detected and removed
                "name": str | None,
                "email": str | None, 
                "phone": str | None
            },
            "extracted_context": {  # Contextual information extracted
                "age": int | None,
                "gender": str | None,
                "goal": str | None
            }
        }
    
    Example:
        >>> result = sanitize_and_build("Hi, I'm Priya (priya@gmail.com). I'm a 27-year-old female building a wellness app.")
        >>> print(result)
        {
            "prompt": "Suggest tools for a 27-year-old female building a wellness app.",
            "removed": {
                "name": "Priya",
                "email": "priya@gmail.com",
                "phone": None
            },
            "extracted_context": {
                "age": 27,
                "gender": "female", 
                "goal": "building a wellness app"
            }
        }
    
    Privacy Assurance:
        - All processing happens locally on the client side
        - No data is sent to external services during sanitization
        - PII is completely removed from the final prompt
        - Original input is not stored or logged
    
    Performance:
        - Typical processing time: < 100ms for standard inputs
        - Memory usage: Minimal, patterns are pre-compiled
        - No network requests during processing
    """
    
    # Validate input
    if not user_input or not isinstance(user_input, str):
        return {
            "prompt": "Suggest relevant tools and services.",
            "removed": {
                "name": None,
                "email": None,
                "phone": None
            },
            "extracted_context": {
                "age": None,
                "gender": None,
                "goal": None
            }
        }
    
    # Initialize sanitizer and builder
    sanitizer = PIISanitizer()
    builder = PromptBuilder()
    
    # Perform PII analysis
    analysis_result = sanitizer.analyze_text(user_input)
    
    # Extract components
    sanitized_text = analysis_result['sanitized_text']
    detected_pii = analysis_result['detected_pii']
    extracted_context = analysis_result['extracted_context']
    
    # Build structured prompt
    prompt = builder.build_complete_prompt(sanitized_text, extracted_context)
    
    # Format removed PII for response
    removed_pii = builder.format_removed_pii(detected_pii)
    
    # Return structured result
    return {
        "prompt": prompt,
        "removed": removed_pii,
        "extracted_context": extracted_context
    }

# Convenience function for backward compatibility and alternative naming
def sanitize_user_input(user_input: str) -> Dict[str, Union[str, Dict[str, Optional[Union[str, int]]]]]:
    """
    Alias for sanitize_and_build function.
    
    Args:
        user_input (str): Raw user input containing potential PII
        
    Returns:
        dict: Same structure as sanitize_and_build
    """
    return sanitize_and_build(user_input)

# Export main functions
__all__ = ['sanitize_and_build', 'sanitize_user_input']
