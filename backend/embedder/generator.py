"""
Embedding generator module for the Book Content Embeddings Backend.

Generates vector embeddings using Cohere models.
"""

import cohere
from typing import List, Dict, Any
import time
from models.entities import EmbeddingRecord, TextChunk
from utils.logger import get_logger
from utils.exceptions import EmbeddingError, CohereAPIError
from services.base_service import EmbedderService


class CohereEmbedder(EmbedderService):
    """Generates vector embeddings using Cohere models."""

    def __init__(self, api_key: str, model: str = "multilingual-22-12", max_retries: int = 3):
        """
        Initialize the CohereEmbedder.

        Args:
            api_key: Cohere API key
            model: The model to use for embeddings
            max_retries: Maximum number of retries for API calls
        """
        super().__init__()
        self.client = cohere.Client(api_key)
        self.model = model
        self.max_retries = max_retries

    def _execute(self, texts: List[str], chunk_ids: List[str] = None) -> List[EmbeddingRecord]:
        """
        Execute the embedding generation process.

        Args:
            texts: List of text strings to embed
            chunk_ids: Optional list of chunk IDs to associate with embeddings

        Returns:
            List of EmbeddingRecord objects
        """
        return self.generate_embeddings(texts, chunk_ids)

    def generate_embeddings(self, texts: List[str], chunk_ids: List[str] = None) -> List[EmbeddingRecord]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts: List of text strings to embed
            chunk_ids: Optional list of chunk IDs to associate with embeddings

        Returns:
            List of EmbeddingRecord objects
        """
        if not texts:
            return []

        # Prepare chunk IDs if not provided
        if chunk_ids is None:
            chunk_ids = [""] * len(texts)

        if len(chunk_ids) != len(texts):
            raise EmbeddingError(
                f"Number of chunk IDs ({len(chunk_ids)}) must match number of texts ({len(texts)})",
                model=self.model,
                text_length=len(texts)
            )

        # Generate embeddings in batches to respect API limits
        embeddings = []
        batch_size = 96  # Cohere's recommended batch size

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_chunk_ids = chunk_ids[i:i + batch_size]

            # Retry logic for API calls
            for attempt in range(self.max_retries):
                try:
                    response = self.client.embed(
                        texts=batch_texts,
                        model=self.model
                    )

                    # Create EmbeddingRecord objects for each embedding in the batch
                    for j, (embedding_vector, text, chunk_id) in enumerate(zip(response.embeddings, batch_texts, batch_chunk_ids)):
                        embedding_record = EmbeddingRecord(
                            chunk_id=chunk_id,
                            vector=embedding_vector,
                            content=text,
                            created_at=None  # Will be set by the dataclass
                        )
                        embeddings.append(embedding_record)

                    self.logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                    break  # Success, break out of retry loop

                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        # Final attempt failed, raise error
                        raise CohereAPIError(
                            f"Failed to generate embeddings after {self.max_retries} attempts: {str(e)}",
                            status_code=getattr(e, 'status_code', None),
                            response_data=getattr(e, 'response_data', None)
                        )

                    # Wait before retry with exponential backoff
                    time.sleep(2 ** attempt)

        self.logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings

    def validate_embedding(self, embedding: EmbeddingRecord) -> bool:
        """
        Validate that an embedding meets requirements.

        Args:
            embedding: The embedding record to validate

        Returns:
            True if valid, False otherwise
        """
        if not embedding.vector:
            return False

        # Check that all values in vector are finite numbers
        for val in embedding.vector:
            if not isinstance(val, (int, float)) or not (float('-inf') < val < float('inf')):
                return False

        return True

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model being used.

        Returns:
            Dictionary containing model information
        """
        # Note: Cohere API doesn't provide direct model info endpoint
        # This is basic info based on the model name
        return {
            "model": self.model,
            "expected_dimensions": self._get_expected_dimensions(self.model),
            "max_input_length": self._get_max_input_length(self.model)
        }

    def _get_expected_dimensions(self, model_name: str) -> int:
        """
        Get the expected dimension for a model.

        Args:
            model_name: Name of the Cohere model

        Returns:
            Expected dimension of embeddings
        """
        # These are approximate dimensions for common Cohere models
        model_dims = {
            "multilingual-22-12": 1024,
            "embed-english-v2.0": 4096,
            "embed-english-light-v2.0": 1024,
            "embed-multilingual-v2.0": 768
        }
        return model_dims.get(model_name, 1024)  # Default to 1024

    def _get_max_input_length(self, model_name: str) -> int:
        """
        Get the maximum input length for a model.

        Args:
            model_name: Name of the Cohere model

        Returns:
            Maximum allowed input length
        """
        # Approximate max input lengths
        return 4096  # Common value for Cohere models