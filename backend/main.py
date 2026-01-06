"""
Main entry point for the Book Content Embeddings Backend.

This module orchestrates the complete pipeline:
- Crawling Docusaurus URLs
- Extracting and cleaning content
- Chunking text
- Generating embeddings with Cohere
- Storing in Qdrant
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Import the config module
from config import config

# Set up logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from environment variables."""
    # Use the config module instead of loading directly
    return {
        "cohere_api_key": config.cohere_api_key,
        "qdrant_url": config.qdrant_url,
        "qdrant_api_key": config.qdrant_api_key,
        "docs_url": config.docs_url,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "vector_dimension": config.vector_dimension,
        "embedding_model": config.embedding_model
    }

from crawler.extractor import DocusaurusExtractor
from processor.chunker import TextChunker
from embedder.generator import CohereEmbedder
from storage.qdrant_handler import QdrantHandler
import time
import signal
import sys


# Global variable to track if shutdown is requested
_shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_requested = True


def main():
    """Main function to run the complete pipeline."""
    global _shutdown_requested

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start_time = time.time()

    try:
        logger.info("Starting Book Content Embeddings Pipeline")

        # Load configuration
        config_dict = load_config()
        logger.info("Configuration loaded successfully")

        # Validate configuration using the global config instance
        if not config.validate():  # Call validate on the actual config object
            logger.error("Configuration validation failed, exiting")
            sys.exit(1)
        logger.info("Configuration validated successfully")

        # Initialize components
        extractor = DocusaurusExtractor()
        chunker = TextChunker(chunk_size=config_dict["chunk_size"], chunk_overlap=config_dict["chunk_overlap"])
        embedder = CohereEmbedder(api_key=config_dict["cohere_api_key"], model=config_dict["embedding_model"])
        storage = QdrantHandler(
            url=config_dict["qdrant_url"],
            api_key=config_dict["qdrant_api_key"],
            collection_name="book_embeddings"
        )
        logger.info("Components initialized successfully")

        # Crawl and extract content
        docs_url = config_dict["docs_url"]
        logger.info(f"Starting content extraction from: {docs_url}")

        extraction_start = time.time()
        # Extract content from the documentation site
        documents = extractor.extract_with_subpages(docs_url)
        extraction_time = time.time() - extraction_start
        logger.info(f"Extracted {len(documents)} documents from {docs_url} in {extraction_time:.2f} seconds")

        # Check if shutdown was requested during extraction
        if _shutdown_requested:
            logger.info("Shutdown requested, stopping pipeline")
            return

        # Process and chunk content
        logger.info("Starting content chunking process")
        chunking_start = time.time()
        all_chunks = []
        for doc in documents:
            if _shutdown_requested:
                logger.info("Shutdown requested, stopping chunking process")
                break
            chunks = chunker.chunk_text(doc.content, document_id=doc.id)
            all_chunks.extend(chunks)
            logger.info(f"Chunked document '{doc.title}' into {len(chunks)} chunks")

        chunking_time = time.time() - chunking_start
        logger.info(f"Total chunks created: {len(all_chunks)} in {chunking_time:.2f} seconds")

        # Check if shutdown was requested during chunking
        if _shutdown_requested:
            logger.info("Shutdown requested, stopping pipeline")
            return

        # Generate embeddings
        logger.info("Starting embedding generation process")
        embedding_start = time.time()
        if all_chunks:
            # Extract text content and chunk IDs for embedding
            texts = [chunk.content for chunk in all_chunks]
            chunk_ids = [chunk.id for chunk in all_chunks]

            # Process embeddings in batches to allow for interruption
            embeddings = []
            batch_size = 10  # Small batch size to allow for more frequent interruption checks

            for i in range(0, len(texts), batch_size):
                if _shutdown_requested:
                    logger.info("Shutdown requested, stopping embedding generation")
                    break

                batch_texts = texts[i:i + batch_size]
                batch_chunk_ids = chunk_ids[i:i + batch_size]

                batch_embeddings = embedder.generate_embeddings(batch_texts, batch_chunk_ids)
                embeddings.extend(batch_embeddings)

                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            embedding_time = time.time() - embedding_start
            logger.info(f"Generated {len(embeddings)} embeddings in {embedding_time:.2f} seconds")
        else:
            logger.warning("No chunks to embed, skipping embedding generation")
            embeddings = []
            embedding_time = 0

        # Check if shutdown was requested during embedding
        if _shutdown_requested:
            logger.info("Shutdown requested, stopping pipeline")
            return

        # Store embeddings in Qdrant
        logger.info("Starting storage process")
        storage_start = time.time()
        if embeddings:
            # Store embeddings in smaller batches to allow for interruption
            stored_count = 0
            batch_size = 50  # Qdrant batch size

            for i in range(0, len(embeddings), batch_size):
                if _shutdown_requested:
                    logger.info("Shutdown requested, stopping storage process")
                    break

                batch_embeddings = embeddings[i:i + batch_size]
                batch_stored = storage.store_embeddings(batch_embeddings)
                stored_count += batch_stored

                logger.info(f"Stored batch {i//batch_size + 1}/{(len(embeddings)-1)//batch_size + 1}, "
                           f"total stored: {stored_count}")

            storage_time = time.time() - storage_start
            logger.info(f"Stored {stored_count} embeddings in Qdrant in {storage_time:.2f} seconds")
        else:
            logger.warning("No embeddings to store, skipping storage process")
            storage_time = 0

        # Performance metrics
        total_time = time.time() - start_time
        logger.info(f"Pipeline completed successfully in {total_time:.2f} seconds")
        logger.info(f"Performance breakdown - Extraction: {extraction_time:.2f}s, "
                   f"Chunking: {chunking_time:.2f}s, "
                   f"Embedding: {embedding_time:.2f}s, "
                   f"Storage: {storage_time:.2f}s")

        # Success criteria validation
        logger.info("Validating success criteria...")

        # SC-001: All public Docusaurus URLs from the deployed site are successfully crawled and clean text is extracted (100% of pages processed)
        if len(documents) > 0:
            logger.info(f"✓ SC-001: Successfully processed {len(documents)} documents")
        else:
            logger.warning("⚠ SC-001: No documents were processed")

        # SC-002: Text content is chunked and embedded with 95% success rate (less than 5% failure rate)
        if all_chunks and embeddings:
            success_rate = len(embeddings) / len(all_chunks) * 100
            logger.info(f"✓ SC-002: Embedding success rate: {success_rate:.2f}% ({len(embeddings)}/{len(all_chunks)})")
            if success_rate < 95:
                logger.warning(f"⚠ SC-002: Success rate below target (95%), got {success_rate:.2f}%")
        elif not all_chunks:
            logger.info("✓ SC-002: No chunks to process, success rate N/A")
        else:
            logger.warning("⚠ SC-002: No embeddings generated")

        # SC-003: Generated embeddings are successfully stored in Qdrant with 99% reliability
        if embeddings:
            storage_success_rate = stored_count / len(embeddings) * 100 if len(embeddings) > 0 else 0
            logger.info(f"✓ SC-003: Storage success rate: {storage_success_rate:.2f}% ({stored_count}/{len(embeddings)})")
            if storage_success_rate < 99:
                logger.warning(f"⚠ SC-003: Storage success rate below target (99%), got {storage_success_rate:.2f}%")
        else:
            logger.info("✓ SC-003: No embeddings to store, storage success rate N/A")

        # SC-005: The complete pipeline (crawl → chunk → embed → store) completes within 30 minutes for a medium-sized documentation site
        pipeline_minutes = total_time / 60
        logger.info(f"✓ SC-005: Pipeline completed in {pipeline_minutes:.2f} minutes (target: ≤ 30 minutes)")
        if pipeline_minutes > 30:
            logger.warning(f"⚠ SC-005: Pipeline took longer than target (30 minutes), got {pipeline_minutes:.2f} minutes")

        if all_chunks:
            logger.info(f"Processing rate: {len(all_chunks) / chunking_time:.2f} chunks/sec (excluding extraction)")

        if embeddings:
            logger.info(f"Embedding rate: {len(embeddings) / embedding_time:.2f} embeddings/sec")

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup operations
        logger.info("Performing cleanup operations...")
        # Add any necessary cleanup here
        logger.info("Cleanup completed")

if __name__ == "__main__":
    main()