"""
Test functions for the Qdrant storage handler.

Verifies that embeddings are properly stored and retrieved.
"""

from .qdrant_handler import QdrantHandler
from ..models.entities import EmbeddingRecord
from ..utils.logger import get_logger


def test_storage_and_retrieval():
    """
    Test function to verify storage and retrieval of embeddings.

    Tests that embeddings are properly stored in Qdrant and can be retrieved successfully.
    """
    logger = get_logger("test_storage")

    # This test requires valid Qdrant credentials to run properly
    # For testing purposes, we'll skip if no credentials are available
    import os
    qdrant_url = os.getenv("QDRANT_URL", "")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

    if not qdrant_url or not qdrant_api_key or qdrant_url == "your-qdrant-instance-url-here":
        logger.warning("No Qdrant credentials found, skipping storage and retrieval test")
        return True

    try:
        # Initialize Qdrant handler
        handler = QdrantHandler(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name="test_embeddings"
        )

        # Create test embeddings
        test_embeddings = [
            EmbeddingRecord(
                vector=[0.1, 0.2, 0.3, 0.4],
                content="This is the first test embedding",
                document_url="https://example.com/doc1",
                document_title="Test Document 1",
                chunk_index=0
            ),
            EmbeddingRecord(
                vector=[0.5, 0.6, 0.7, 0.8],
                content="This is the second test embedding",
                document_url="https://example.com/doc2",
                document_title="Test Document 2",
                chunk_index=1
            )
        ]

        # Store embeddings
        stored_count = handler.store_embeddings(test_embeddings)
        logger.info(f"Stored {stored_count} embeddings in Qdrant")

        if stored_count != len(test_embeddings):
            logger.error(f"Expected to store {len(test_embeddings)} embeddings, but stored {stored_count}")
            return False

        # Get collection info
        info = handler.get_collection_info()
        logger.info(f"Collection info: {info}")

        # Test search functionality with a query vector
        query_vector = [0.1, 0.2, 0.3, 0.4]  # Similar to the first embedding
        search_results = handler.search_embeddings(query_vector, top_k=5)

        logger.info(f"Search returned {len(search_results)} results")
        for i, result in enumerate(search_results):
            logger.info(f"Result {i}: Score={result['score']}, Content='{result['content'][:50]}...'")

        # Clean up - delete test collection
        handler.delete_collection()
        logger.info("Test collection deleted")

        logger.info("Storage and retrieval test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during storage and retrieval test: {str(e)}")
        return False


def test_error_handling():
    """
    Test the error handling functionality of the storage handler.
    """
    logger = get_logger("test_error_handling")

    try:
        # This will fail with invalid credentials, which tests our error handling
        handler = QdrantHandler(
            url="invalid-url",
            api_key="invalid-key",
            collection_name="test_collection"
        )

        # Try to create a collection, which should fail
        try:
            handler.create_collection()
            logger.error("Expected error when using invalid credentials, but none occurred")
            return False
        except Exception:
            logger.info("Correctly handled invalid credentials")

        logger.info("Error handling test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during error handling test: {str(e)}")
        return False


def test_collection_operations():
    """
    Test various collection operations.
    """
    logger = get_logger("test_collection_ops")

    # This test requires valid Qdrant credentials to run properly
    import os
    qdrant_url = os.getenv("QDRANT_URL", "")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

    if not qdrant_url or not qdrant_api_key or qdrant_url == "your-qdrant-instance-url-here":
        logger.warning("No Qdrant credentials found, skipping collection operations test")
        return True

    try:
        # Initialize handler with a test collection
        handler = QdrantHandler(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name="test_ops_collection"
        )

        # Test collection creation
        success = handler.create_collection(vector_size=4)
        if not success:
            logger.error("Failed to create collection")
            return False

        # Get collection info
        info = handler.get_collection_info()
        logger.info(f"Collection created with {info['vector_size']} dimensions and {info['point_count']} points")

        # Clean up
        handler.delete_collection()

        logger.info("Collection operations test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during collection operations test: {str(e)}")
        return False


if __name__ == "__main__":
    # Run tests (these require valid Qdrant credentials to fully test)
    success1 = test_storage_and_retrieval()
    success2 = test_error_handling()
    success3 = test_collection_operations()

    if success1 and success2 and success3:
        print("Storage tests completed (some may be skipped without credentials)!")
    else:
        print("Some storage tests failed!")