"""File utilities for common file operations."""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def read_json(file_path: str) -> Dict[str, Any]:
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def write_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """Write data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


def read_csv_as_dicts(file_path: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of dictionaries."""
    with open(file_path, 'r', newline='') as f:
        return list(csv.DictReader(f))


def ensure_dir_exists(dir_path: str) -> None:
    """Create directory if it doesn't exist."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_file_extension(file_path: str) -> str:
    """Get file extension without the dot."""
    return Path(file_path).suffix.lstrip('.')


def file_exists(file_path: str) -> bool:
    """Check if file exists."""
    return Path(file_path).exists()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return Path(file_path).stat().st_size