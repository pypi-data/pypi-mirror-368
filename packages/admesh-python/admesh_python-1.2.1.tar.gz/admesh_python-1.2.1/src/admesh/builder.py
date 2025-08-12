# File generated for AdMesh PII sanitization functionality

"""
Prompt building module for reconstructing clean, structured prompts from sanitized input.
Builds contextual prompts using extracted information while maintaining natural language flow.
"""

from typing import Dict, Optional, Union, List

class PromptBuilder:
    """
    Handles reconstruction of clean, structured prompts from sanitized input and extracted context.
    
    This class provides methods to:
    - Build contextual prompts using extracted information
    - Use fallback templates when context is incomplete
    - Maintain natural language flow
    - Generate privacy-preserving prompts
    """
    
    def __init__(self):
        """Initialize the prompt builder with template patterns."""
        self.context_templates = {
            'full': "Suggest tools for a {age}-year-old {gender} {goal}.",
            'age_gender': "Suggest tools for a {age}-year-old {gender}.",
            'age_goal': "Suggest tools for someone {goal} (age {age}).",
            'gender_goal': "Suggest tools for a {gender} {goal}.",
            'age_only': "Suggest tools for a {age}-year-old.",
            'gender_only': "Suggest tools for a {gender}.",
            'goal_only': "Suggest tools for {goal}.",
            'fallback': "Suggest relevant tools and services."
        }
        
        self.goal_prefixes = {
            'building': 'building',
            'creating': 'creating',
            'developing': 'developing',
            'making': 'making',
            'working on': 'working on',
            'starting': 'starting',
            'launching': 'launching'
        }
    
    def normalize_goal(self, goal: str) -> str:
        """
        Normalize goal text to ensure proper grammar in templates.

        Args:
            goal: Raw goal text extracted from input

        Returns:
            Normalized goal text suitable for template insertion
        """
        if not goal:
            return ""

        goal = goal.strip().lower()

        # Ensure goal starts with appropriate verb or article
        for prefix in self.goal_prefixes:
            if goal.startswith(prefix):
                return goal

        # Add appropriate prefix if missing
        if goal.startswith(('a ', 'an ', 'the ')):
            return f"working on {goal}"
        elif any(goal.startswith(word) for word in ['app', 'website', 'business', 'startup', 'tool', 'platform']):
            return f"building {goal}"
        else:
            return f"working on {goal}"
    
    def select_template(self, age: Optional[int], gender: Optional[str], goal: Optional[str]) -> str:
        """
        Select the most appropriate template based on available context.
        
        Args:
            age: Extracted age information
            gender: Extracted gender information
            goal: Extracted goal information
            
        Returns:
            Template key for prompt construction
        """
        has_age = age is not None
        has_gender = gender is not None
        has_goal = goal is not None and len(goal.strip()) > 0
        
        if has_age and has_gender and has_goal:
            return 'full'
        elif has_age and has_gender:
            return 'age_gender'
        elif has_age and has_goal:
            return 'age_goal'
        elif has_gender and has_goal:
            return 'gender_goal'
        elif has_age:
            return 'age_only'
        elif has_gender:
            return 'gender_only'
        elif has_goal:
            return 'goal_only'
        else:
            return 'fallback'
    
    def build_prompt(self, extracted_context: Dict[str, Union[int, str, None]]) -> str:
        """
        Build a structured prompt from extracted context information.
        
        Args:
            extracted_context: Dictionary containing age, gender, and goal
            
        Returns:
            Clean, structured prompt string
        """
        age = extracted_context.get('age')
        gender = extracted_context.get('gender')
        goal = extracted_context.get('goal')
        
        # Normalize goal if present
        if goal:
            goal = self.normalize_goal(goal)
        
        # Select appropriate template
        template_key = self.select_template(age, gender, goal)
        template = self.context_templates[template_key]
        
        # Build prompt using template
        try:
            if template_key == 'full':
                prompt = template.format(age=age, gender=gender, goal=goal)
            elif template_key == 'age_gender':
                prompt = template.format(age=age, gender=gender)
            elif template_key == 'age_goal':
                prompt = template.format(age=age, goal=goal)
            elif template_key == 'gender_goal':
                prompt = template.format(gender=gender, goal=goal)
            elif template_key == 'age_only':
                prompt = template.format(age=age)
            elif template_key == 'gender_only':
                prompt = template.format(gender=gender)
            elif template_key == 'goal_only':
                prompt = template.format(goal=goal)
            else:
                prompt = template
        except (KeyError, ValueError):
            # Fallback to basic template if formatting fails
            prompt = self.context_templates['fallback']
        
        return prompt
    
    def enhance_with_sanitized_text(self, base_prompt: str, sanitized_text: str) -> str:
        """
        Enhance the base prompt with additional context from sanitized text.

        Args:
            base_prompt: Base prompt built from extracted context
            sanitized_text: Sanitized input text with PII removed

        Returns:
            Enhanced prompt with additional context
        """
        if not sanitized_text or sanitized_text.strip() in ['', '[NAME]', '[EMAIL]', '[PHONE]']:
            return base_prompt

        # Clean up sanitized text
        cleaned_text = sanitized_text.strip()

        # Remove placeholder tokens if they're the only content or mostly placeholders
        placeholder_tokens = ['[NAME]', '[EMAIL]', '[PHONE]']
        words = cleaned_text.split()
        placeholder_count = sum(1 for word in words if any(token in word for token in placeholder_tokens))

        # If more than 50% of words are placeholders, don't add context
        if len(words) > 0 and placeholder_count / len(words) > 0.5:
            return base_prompt

        # Don't add context if it's too short or starts with common phrases
        if len(cleaned_text) <= 20 or cleaned_text.startswith(('Suggest', 'I need', 'Looking for', 'Hi,', 'Hello,')):
            return base_prompt

        return base_prompt
    
    def build_complete_prompt(self, sanitized_text: str, extracted_context: Dict[str, Union[int, str, None]]) -> str:
        """
        Build a complete prompt combining extracted context and sanitized text.
        
        Args:
            sanitized_text: Text with PII removed
            extracted_context: Dictionary containing age, gender, and goal
            
        Returns:
            Complete structured prompt
        """
        # Build base prompt from context
        base_prompt = self.build_prompt(extracted_context)
        
        # Enhance with sanitized text if meaningful
        enhanced_prompt = self.enhance_with_sanitized_text(base_prompt, sanitized_text)
        
        return enhanced_prompt
    
    def format_removed_pii(self, detected_pii: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
        """
        Format detected PII for the response structure.
        
        Args:
            detected_pii: Dictionary containing lists of detected PII
            
        Returns:
            Formatted PII dictionary with single values or None
        """
        return {
            'name': detected_pii.get('names', [None])[0] if detected_pii.get('names') else None,
            'email': detected_pii.get('emails', [None])[0] if detected_pii.get('emails') else None,
            'phone': detected_pii.get('phones', [None])[0] if detected_pii.get('phones') else None
        }
