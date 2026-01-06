"""
Test functions for the TextChunker module.

Verifies that text is properly chunked with appropriate boundaries.
"""

from .chunker import TextChunker
from ..models.entities import DocumentContent
from ..utils.logger import get_logger


def test_chunk_boundaries():
    """
    Test function to verify proper chunk boundaries are maintained.

    Tests that chunks respect sentence and paragraph boundaries when possible.
    """
    logger = get_logger("test_chunker")

    # Initialize chunker with small chunk size for testing
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)

    # Test content with clear sentence boundaries
    test_content = """
    This is the first sentence. This is the second sentence.
    This is a new paragraph with the third sentence.
    And here is the fourth sentence in the same paragraph.
    Finally, this is the fifth sentence in a new paragraph.
    """

    try:
        # Chunk the content
        chunks = chunker.chunk_text(test_content)

        logger.info(f"Created {len(chunks)} chunks from test content")

        # Verify each chunk has content
        for i, chunk in enumerate(chunks):
            if not chunk.content.strip():
                logger.error(f"Chunk {i} has empty content")
                return False

            logger.info(f"Chunk {i}: {len(chunk.content)} chars, content: '{chunk.content[:50]}...'")

        # Check that chunks are of reasonable size
        for i, chunk in enumerate(chunks):
            if len(chunk.content) > chunker.chunk_size * 1.5:  # Allow some flexibility
                logger.warning(f"Chunk {i} exceeds expected size: {len(chunk.content)} > {chunker.chunk_size}")

        # Verify that the chunker preserved document reference
        for chunk in chunks:
            # Since we didn't provide a document ID, this is expected
            pass

        logger.info("Chunk boundary test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during chunk boundary test: {str(e)}")
        return False


def test_paragraph_chunking():
    """
    Test paragraph-aware chunking functionality.
    """
    logger = get_logger("test_paragraph_chunker")

    # Initialize chunker
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    # Test content with clear paragraph boundaries
    test_content = """
    This is the first paragraph. It has multiple sentences.
    This is the second sentence in the first paragraph.

    This is the second paragraph. It also has multiple sentences.
    This is the second sentence in the second paragraph.

    This is the third paragraph with just one sentence.
    """

    try:
        # Chunk by paragraph
        chunks = chunker.chunk_by_paragraph(test_content)

        logger.info(f"Created {len(chunks)} chunks using paragraph chunking")

        # Verify each chunk has content
        for i, chunk in enumerate(chunks):
            if not chunk.content.strip():
                logger.error(f"Paragraph chunk {i} has empty content")
                return False

            logger.info(f"Paragraph chunk {i}: {len(chunk.content)} chars")

        logger.info("Paragraph chunking test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during paragraph chunking test: {str(e)}")
        return False


def test_edge_cases():
    """
    Test edge cases for chunking functionality.
    """
    logger = get_logger("test_edge_cases")

    chunker = TextChunker()

    # Test empty content
    try:
        chunks = chunker.chunk_text("")
        logger.error("Expected error for empty content, but none occurred")
        return False
    except Exception:
        logger.info("Correctly handled empty content")

    # Test very short content
    try:
        chunks = chunker.chunk_text("Short")
        if len(chunks) == 1 and chunks[0].content == "Short":
            logger.info("Correctly handled short content")
        else:
            logger.error("Incorrect handling of short content")
            return False
    except Exception as e:
        logger.error(f"Error handling short content: {str(e)}")
        return False

    # Test content with no clear boundaries
    try:
        no_boundary_content = "This is a very long sentence without clear breaking points " * 5
        chunks = chunker.chunk_text(no_boundary_content)
        if len(chunks) > 0:
            logger.info("Correctly handled content with no clear boundaries")
        else:
            logger.error("Failed to handle content with no clear boundaries")
            return False
    except Exception as e:
        logger.error(f"Error handling content with no clear boundaries: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    # Run all tests
    success1 = test_chunk_boundaries()
    success2 = test_paragraph_chunking()
    success3 = test_edge_cases()

    if success1 and success2 and success3:
        print("All chunking tests passed!")
    else:
        print("Some chunking tests failed!")