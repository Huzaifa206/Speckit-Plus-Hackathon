"""
Configuration management module for the Book Content Embeddings Backend.

Handles loading, validation, and access to configuration values from environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to manage application settings."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.cohere_api_key: str = self._get_required_env("COHERE_API_KEY")
        self.qdrant_url: str = self._get_required_env("QDRANT_URL")
        self.qdrant_api_key: str = self._get_required_env("QDRANT_API_KEY")

        self.docs_url: str = os.getenv("DOCS_URL", "https://speckit-plus-hackathon-phi.vercel.app/")
        self.chunk_size: int = self._get_int_with_default("CHUNK_SIZE", 300, min_val=50, max_val=2000)
        self.chunk_overlap: int = self._get_int_with_default("CHUNK_OVERLAP", 50, min_val=0, max_val=500)
        self.vector_dimension: int = self._get_int_with_default("VECTOR_DIMENSION", 1024, min_val=128, max_val=4096)
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "multilingual-22-12")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable or raise an error if missing."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    def _get_int_with_default(self, key: str, default: int, min_val: int = None, max_val: int = None) -> int:
        """
        Get an integer environment variable with default value and optional bounds checking.

        Args:
            key: Environment variable key
            default: Default value if not found
            min_val: Minimum allowed value (optional)
            max_val: Maximum allowed value (optional)

        Returns:
            Integer value from environment or default
        """
        try:
            value = os.getenv(key)
            if value is None:
                return default
            int_val = int(value)

            # Check bounds if specified
            if min_val is not None and int_val < min_val:
                logging.warning(f"Value for {key} ({int_val}) is below minimum ({min_val}), using default ({default})")
                return default
            if max_val is not None and int_val > max_val:
                logging.warning(f"Value for {key} ({int_val}) is above maximum ({max_val}), using default ({default})")
                return default

            return int_val
        except ValueError:
            logging.warning(f"Invalid integer value for {key}: {value}, using default ({default})")
            return default

    def setup_logging(self):
        """Configure logging based on the configuration."""
        logging.basicConfig(
            level=self.log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def validate(self) -> bool:
        """Validate that all required configuration values are present and valid."""
        try:
            # Validate URL format
            from urllib.parse import urlparse
            parsed = urlparse(self.docs_url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"Invalid URL format for DOCS_URL: {self.docs_url}")

            # Validate log level
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.log_level not in valid_levels:
                raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}, must be one of {valid_levels}")

            # Validate chunk parameters make sense together
            if self.chunk_overlap >= self.chunk_size:
                raise ValueError(f"CHUNK_OVERLAP ({self.chunk_overlap}) should be less than CHUNK_SIZE ({self.chunk_size})")

            return True
        except Exception as e:
            logging.error(f"Configuration validation failed: {str(e)}")
            return False

# Global configuration instance
config = Config()