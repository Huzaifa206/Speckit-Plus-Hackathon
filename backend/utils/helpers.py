"""
Utility functions for the Book Content Embeddings Backend.

Contains commonly used helper functions across the application.
"""

import uuid
import hashlib
from datetime import datetime
from typing import Union, Optional
import logging

def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())

def generate_content_hash(content: str) -> str:
    """Generate a hash for content to identify duplicates."""
    return hashlib.sha256(content.encode()).hexdigest()

def get_current_timestamp() -> datetime:
    """Get current timestamp."""
    return datetime.utcnow()

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with the given name and level."""
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(level)
    return logger

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning a default value if division by zero."""
    if denominator == 0:
        return default
    return numerator / denominator

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix