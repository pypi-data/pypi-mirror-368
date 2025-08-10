"""Utility functions for ReqNinja."""

import json
import re
from typing import Any, Dict, Union
from pathlib import Path


def parse_json_or_data(data: str) -> Union[Dict[str, Any], str]:
    """Try to parse data as JSON, fallback to string."""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return data


def format_headers(headers: Dict[str, str]) -> str:
    """Format headers for display."""
    return '\n'.join(f"{k}: {v}" for k, v in headers.items())


def validate_url(url: str) -> bool:
    """Validate URL format."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def ensure_dir(filepath: str) -> None:
    """Ensure directory exists for filepath."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
