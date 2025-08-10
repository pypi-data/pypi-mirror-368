"""String utilities for common string operations."""

import re
from typing import List, Optional


def camel_to_snake(camel_str: str) -> str:
    """Convert CamelCase to snake_case."""
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    components = snake_str.split('_')
    return ''.join(word.capitalize() for word in components)


def remove_extra_spaces(text: str) -> str:
    """Remove extra whitespace and normalize spaces."""
    return ' '.join(text.split())


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length and add suffix."""
    if len(text) <= max_length:
        return text
    # Ensure we don't go negative with the slice
    truncate_length = max(0, max_length - len(suffix))
    return text[:truncate_length] + suffix


def extract_numbers(text: str) -> List[str]:
    """Extract all numbers from a string."""
    return re.findall(r'\d+', text)


def is_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clean_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def plural(word: str, count: int) -> str:
    """Simple pluralization with more comprehensive rules."""
    if count == 1:
        return word
    
    # Handle special cases
    special_cases = {
        'child': 'children',
        'mouse': 'mice',
        'foot': 'feet',
        'tooth': 'teeth',
        'goose': 'geese',
        'man': 'men',
        'woman': 'women',
        'person': 'people'
    }
    
    if word.lower() in special_cases:
        return special_cases[word.lower()]
    
    # Regular pluralization rules
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z', 'o')):
        return word + 'es'
    elif word.endswith('f'):
        return word[:-1] + 'ves'
    elif word.endswith('fe'):
        return word[:-2] + 'ves'
    else:
        return word + 's'