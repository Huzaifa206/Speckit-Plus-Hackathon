"""
Unit tests for critical components of the Book Content Embeddings Backend.

Tests core functionality of key modules.
"""

import unittest
from unittest.mock import Mock, patch
from processor.chunker import TextChunker
from models.entities import DocumentContent
from config import Config


class TestTextChunker(unittest.TestCase):
    """Unit tests for the TextChunker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    def test_chunk_text_basic(self):
        """Test basic text chunking functionality."""
        content = "This is a test sentence. " * 10  # Creates content longer than chunk_size
        document_id = "test_doc_1"

        chunks = self.chunker.chunk_text(content, document_id)

        # Should create multiple chunks since content is longer than chunk_size
        self.assertGreater(len(chunks), 1)

        # Each chunk should have the correct document_id
        for chunk in chunks:
            self.assertEqual(chunk.document_id, document_id)

        # Total content should be preserved (approximately)
        total_chunked_content = sum(len(chunk.content) for chunk in chunks)
        self.assertGreater(total_chunked_content, len(content) * 0.8)  # Allow some overlap/duplication

    def test_chunk_text_short_content(self):
        """Test chunking of content shorter than chunk size."""
        content = "This is a short sentence."
        document_id = "test_doc_2"

        chunks = self.chunker.chunk_text(content, document_id)

        # Should create a single chunk for short content
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].content, content)
        self.assertEqual(chunks[0].document_id, document_id)

    def test_chunk_text_empty_content(self):
        """Test chunking of empty content raises appropriate error."""
        with self.assertRaises(Exception):  # Should raise ChunkingError
            self.chunker.chunk_text("", "test_doc_3")

    def test_sentence_aware_chunking(self):
        """Test that sentence boundaries are respected when possible."""
        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        # With chunk_size=100, this should try to keep sentences together

        chunks = self.chunker.chunk_text(content, "test_doc_4")

        # Verify chunks were created
        self.assertGreaterEqual(len(chunks), 1)

        # Verify no chunk is empty
        for chunk in chunks:
            self.assertTrue(chunk.content.strip())


class TestConfig(unittest.TestCase):
    """Unit tests for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock environment for testing
        import os
        os.environ["COHERE_API_KEY"] = "test-key"
        os.environ["QDRANT_URL"] = "https://test-qdrant.com"
        os.environ["QDRANT_API_KEY"] = "test-qdrant-key"
        os.environ["CHUNK_SIZE"] = "400"
        os.environ["CHUNK_OVERLAP"] = "60"
        os.environ["LOG_LEVEL"] = "DEBUG"

    def tearDown(self):
        """Clean up test environment."""
        import os
        # Remove the test environment variables
        for key in ["COHERE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", "CHUNK_SIZE", "CHUNK_OVERLAP", "LOG_LEVEL"]:
            if key in os.environ:
                del os.environ[key]

    def test_config_initialization(self):
        """Test that configuration is properly initialized."""
        config = Config()

        self.assertEqual(config.cohere_api_key, "test-key")
        self.assertEqual(config.qdrant_url, "https://test-qdrant.com")
        self.assertEqual(config.qdrant_api_key, "test-qdrant-key")
        self.assertEqual(config.chunk_size, 400)
        self.assertEqual(config.chunk_overlap, 60)
        self.assertEqual(config.log_level, "DEBUG")

    def test_config_default_values(self):
        """Test that default values are used when environment variables are missing."""
        # Temporarily remove some environment variables
        import os
        original_chunk_size = os.environ.get("CHUNK_SIZE")
        if "CHUNK_SIZE" in os.environ:
            del os.environ["CHUNK_SIZE"]

        config = Config()

        # Should use default value
        self.assertEqual(config.chunk_size, 300)  # Default value

        # Restore original value
        if original_chunk_size is not None:
            os.environ["CHUNK_SIZE"] = original_chunk_size

    def test_config_bounds_validation(self):
        """Test that configuration values are validated against bounds."""
        import os
        # Set an out-of-bounds value
        os.environ["CHUNK_SIZE"] = "5000"  # Above max of 2000

        config = Config()
        # Should fall back to default when out of bounds
        self.assertEqual(config.chunk_size, 300)  # Default value instead of 5000


def run_tests():
    """Run all unit tests."""
    print("Running unit tests for critical components...")

    # Create a test suite
    suite = unittest.TestSuite()

    # Add tests
    suite.addTest(unittest.makeSuite(TestTextChunker))
    suite.addTest(unittest.makeSuite(TestConfig))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)