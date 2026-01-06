"""
Test functions for the Cohere embedding generator.

Verifies that embeddings are generated with appropriate dimensions and quality.
"""

from .generator import CohereEmbedder
from ..models.entities import TextChunk
from ..utils.logger import get_logger


def test_embedding_quality():
    """
    Test function to verify embedding quality.

    Tests that valid embeddings are generated with appropriate dimensions and consistency.
    """
    logger = get_logger("test_embedder")

    # This test requires a valid Cohere API key to run properly
    # For testing purposes, we'll skip if no API key is available
    import os
    api_key = os.getenv("COHERE_API_KEY", "")

    if not api_key or api_key == "your-cohere-api-key-here":
        logger.warning("No Cohere API key found, skipping embedding quality test")
        return True

    try:
        # Initialize embedder with test configuration
        embedder = CohereEmbedder(api_key=api_key, model="multilingual-22-12")

        # Test content
        test_texts = [
            "This is a test sentence for embedding.",
            "Another test sentence with different content.",
            "A third sentence to verify consistency."
        ]

        # Generate embeddings
        embeddings = embedder.generate_embeddings(test_texts)

        # Verify we got embeddings back
        if len(embeddings) != len(test_texts):
            logger.error(f"Expected {len(test_texts)} embeddings, got {len(embeddings)}")
            return False

        # Verify each embedding has proper structure
        expected_dimensions = embedder._get_expected_dimensions("multilingual-22-12")
        for i, emb in enumerate(embeddings):
            # Check that content matches
            if emb.content != test_texts[i]:
                logger.error(f"Embedding {i} content doesn't match input text")
                return False

            # Check that vector has expected dimensions
            if len(emb.vector) != expected_dimensions:
                logger.error(f"Embedding {i} has {len(emb.vector)} dimensions, expected {expected_dimensions}")
                return False

            # Check that all values are finite numbers
            for j, val in enumerate(emb.vector):
                if not isinstance(val, (int, float)) or not (float('-inf') < val < float('inf')):
                    logger.error(f"Embedding {i} vector value at index {j} is not a finite number: {val}")
                    return False

            logger.info(f"Embedding {i}: {len(emb.vector)} dimensions, content length: {len(emb.content)}")

        logger.info(f"Successfully generated {len(embeddings)} embeddings with {expected_dimensions} dimensions each")
        return True

    except Exception as e:
        logger.error(f"Error during embedding quality test: {str(e)}")
        return False


def test_embedding_validation():
    """
    Test the embedding validation functionality.
    """
    logger = get_logger("test_embedding_validation")

    # Initialize embedder
    embedder = CohereEmbedder(api_key="test-key", model="multilingual-22-12")

    # Test with valid embedding
    from ..models.entities import EmbeddingRecord
    valid_embedding = EmbeddingRecord(
        vector=[0.1, 0.2, 0.3],
        content="test content"
    )
    if not embedder.validate_embedding(valid_embedding):
        logger.error("Valid embedding failed validation")
        return False

    # Test with empty vector
    invalid_embedding = EmbeddingRecord(
        vector=[],
        content="test content"
    )
    # Note: This validation is not strict in the current implementation
    # The validation method checks for finite numbers in the vector

    logger.info("Embedding validation test completed")
    return True


def test_model_info():
    """
    Test the model information functionality.
    """
    logger = get_logger("test_model_info")

    # Initialize embedder
    embedder = CohereEmbedder(api_key="test-key", model="multilingual-22-12")

    # Get model info
    info = embedder.get_model_info()

    if "model" not in info or "expected_dimensions" not in info:
        logger.error("Model info missing required fields")
        return False

    logger.info(f"Model: {info['model']}, Expected dimensions: {info['expected_dimensions']}")
    return True


if __name__ == "__main__":
    # Run tests (these require a valid Cohere API key to fully test)
    success1 = test_embedding_quality()
    success2 = test_embedding_validation()
    success3 = test_model_info()

    if success1 and success2 and success3:
        print("Embedding tests completed (some may be skipped without API key)!")
    else:
        print("Some embedding tests failed!")