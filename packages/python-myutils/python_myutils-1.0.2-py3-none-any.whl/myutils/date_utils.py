"""Date and time utilities."""

from datetime import datetime, timedelta
from typing import Optional


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse string to datetime."""
    return datetime.strptime(date_str, format_str)


def days_ago(days: int) -> datetime:
    """Get datetime N days ago."""
    return datetime.now() - timedelta(days=days)


def days_from_now(days: int) -> datetime:
    """Get datetime N days from now."""
    return datetime.now() + timedelta(days=days)


def is_weekend(dt: datetime) -> bool:
    """Check if date is weekend (Saturday=5, Sunday=6)."""
    return dt.weekday() >= 5


def get_age_in_years(birth_date: datetime) -> int:
    """Calculate age in years from birth date."""
    today = datetime.now()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def time_since(dt: datetime) -> str:
    """Human readable time since given datetime."""
    now = datetime.now()
    diff = now - dt
    
    # Use total_seconds() for more accurate calculation
    total_seconds = int(diff.total_seconds())
    
    if diff.days > 0:
        unit = "day" if diff.days == 1 else "days"
        return f"{diff.days} {unit} ago"
    elif total_seconds >= 3600:
        hours = total_seconds // 3600
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit} ago"
    elif total_seconds >= 60:
        minutes = total_seconds // 60
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit} ago"
    else:
        return "just now"