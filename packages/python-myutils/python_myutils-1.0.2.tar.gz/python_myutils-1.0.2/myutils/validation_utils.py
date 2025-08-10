"""Validation utilities for common data validation needs."""

import re
from typing import Any, List, Dict, Union


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (US format)."""
    pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
    return bool(re.match(pattern, phone.strip()))


def is_valid_url(url: str) -> bool:
    """Basic URL validation."""
    # Allow localhost and IP addresses, case insensitive
    pattern = r'^https?:\/\/(www\.|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6})(:[0-9]{1,5})?\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def is_valid_ip(ip: str) -> bool:
    """Validate IPv4 address (no leading zeros allowed)."""
    # Stricter pattern that doesn't allow leading zeros
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
    return bool(re.match(pattern, ip))


def is_numeric(value: str) -> bool:
    """Check if string represents a number (excluding NaN, inf)."""
    if not value or value.strip() != value:
        return False
    try:
        num = float(value)
        # Exclude NaN and infinite values
        return not (num != num or abs(num) == float('inf'))  # NaN != NaN is True
    except ValueError:
        return False


def has_required_keys(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """Check if dictionary has all required keys."""
    return all(key in data for key in required_keys)


def is_in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
    """Check if value is within range (inclusive)."""
    return min_val <= value <= max_val


def is_not_empty(value: str) -> bool:
    """Check if string is not empty or just whitespace."""
    return bool(value and value.strip())


def validate_password_strength(password: str) -> Dict[str, bool]:
    """Validate password strength and return detailed results."""
    return {
        'min_length': len(password) >= 8,
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_digit': bool(re.search(r'\d', password)),
        'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }


def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements."""
    criteria = validate_password_strength(password)
    return all(criteria.values())