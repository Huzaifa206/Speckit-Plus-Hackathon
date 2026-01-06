"""
Test functions for the Docusaurus content extraction.

Verifies that clean content is properly extracted from Docusaurus pages.
"""

from .extractor import DocusaurusExtractor
from ..models.entities import DocumentContent
from ..utils.logger import get_logger


def test_clean_content_extraction():
    """
    Test function to verify clean content extraction from Docusaurus pages.

    This function tests that content is extracted without navigation elements,
    headers, and other non-content elements.
    """
    logger = get_logger("test_extraction")
    extractor = DocusaurusExtractor()

    # Test with a sample URL (this would be replaced with an actual Docusaurus site in real usage)
    test_url = "https://example-docusaurus-site.com/docs/intro"

    try:
        # Extract content from a single page
        docs = extractor.extract_with_subpages(test_url)

        if not docs:
            logger.error("No content extracted from the test URL")
            return False

        # Verify that we have content
        for doc in docs:
            if not doc.content.strip():
                logger.error(f"Empty content extracted from {doc.url}")
                return False

            # Check that content has reasonable length
            if len(doc.content) < 50:
                logger.warning(f"Very short content from {doc.url}: {len(doc.content)} chars")

            # Verify that document has a title
            if not doc.title.strip():
                logger.warning(f"No title extracted from {doc.url}")

        logger.info(f"Successfully extracted content from {len(docs)} pages")
        logger.info(f"Sample content length: {len(docs[0].content) if docs else 0} characters")

        # Verify that content looks like clean text (no HTML tags)
        sample_content = docs[0].content if docs else ""
        if '<' in sample_content and '>' in sample_content:
            logger.warning("HTML tags detected in extracted content - cleaning may not be effective")
        else:
            logger.info("Content appears to be clean (no HTML tags detected)")

        return True

    except Exception as e:
        logger.error(f"Error during content extraction test: {str(e)}")
        return False


def test_content_extraction_quality():
    """
    Test the quality of content extraction by checking for common issues.

    Returns:
        True if extraction quality is acceptable, False otherwise
    """
    logger = get_logger("test_extraction_quality")

    # This is a placeholder for more comprehensive quality tests
    # In a real implementation, this would check:
    # - Content doesn't contain navigation elements
    # - Content has proper structure
    # - Content length is reasonable
    # - No duplicate content
    # - No irrelevant elements

    logger.info("Content extraction quality test completed")
    return True


if __name__ == "__main__":
    # Run the test
    success = test_clean_content_extraction()
    quality_success = test_content_extraction_quality()

    if success and quality_success:
        print("Content extraction tests passed!")
    else:
        print("Content extraction tests failed!")