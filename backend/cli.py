"""
Command-line interface for the Book Content Embeddings Backend.

Provides a CLI for executing the pipeline with various options.
"""

import argparse
import sys
from .main import main as run_pipeline
from .config import config


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Book Content Embeddings Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --docs-url https://example-docusaurus.com
  %(prog)s --chunk-size 400 --chunk-overlap 75
  %(prog)s --docs-url https://example.com --collection-name my_embeddings
        """
    )

    # Main options
    parser.add_argument(
        '--docs-url',
        type=str,
        default=config.docs_url,
        help='URL of the Docusaurus documentation site to process (default: from config)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=config.chunk_size,
        help=f'Target size for text chunks (default: {config.chunk_size})'
    )

    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=config.chunk_overlap,
        help=f'Overlap between chunks (default: {config.chunk_overlap})'
    )

    parser.add_argument(
        '--collection-name',
        type=str,
        default='book_embeddings',
        help='Name of the Qdrant collection to store embeddings (default: book_embeddings)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default=config.embedding_model,
        help=f'Embedding model to use (default: {config.embedding_model})'
    )

    parser.add_argument(
        '--include-subpages',
        action='store_true',
        default=False,
        help='Include subpages when crawling the documentation site'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Show what would be done without actually processing'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='Enable verbose logging'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Update configuration based on command line arguments
    config.docs_url = args.docs_url
    config.chunk_size = args.chunk_size
    config.chunk_overlap = args.chunk_overlap
    config.embedding_model = args.model

    # Set logging level based on verbosity
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dry_run:
        print("Dry run mode - would execute pipeline with the following parameters:")
        print(f"  Docs URL: {config.docs_url}")
        print(f"  Chunk size: {config.chunk_size}")
        print(f"  Chunk overlap: {config.chunk_overlap}")
        print(f"  Model: {config.embedding_model}")
        print(f"  Collection name: {args.collection_name}")
        print(f"  Include subpages: {args.include_subpages}")
        return 0

    try:
        print(f"Starting pipeline for {config.docs_url}")
        run_pipeline()
        print("Pipeline completed successfully!")
        return 0
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        return 1
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())