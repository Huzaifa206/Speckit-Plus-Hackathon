"""
Text chunking module for the Book Content Embeddings Backend.

Implements various chunking strategies for preparing text content for embedding generation.
"""

import re
from typing import List, Tuple
from models.entities import TextChunk, DocumentContent
from utils.logger import get_logger
from utils.exceptions import ChunkingError
from services.base_service import ProcessorService


class TextChunker(ProcessorService):
    """Implements text chunking strategies for embedding preparation."""

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize the TextChunker.

        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Overlap between chunks (in characters)
        """
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _execute(self, content: str, document_id: str = None) -> List[TextChunk]:
        """
        Execute the chunking process.

        Args:
            content: The text content to chunk
            document_id: Optional document ID to associate with chunks

        Returns:
            List of TextChunk objects
        """
        return self.chunk_text(content, document_id)

    def chunk_text(self, content: str, document_id: str = None) -> List[TextChunk]:
        """
        Chunk text content using sentence-aware chunking.

        Args:
            content: The text content to chunk
            document_id: Optional document ID to associate with chunks

        Returns:
            List of TextChunk objects
        """
        if not content.strip():
            raise ChunkingError("Cannot chunk empty content", chunk_size=self.chunk_size)

        # Use sentence-aware chunking to respect sentence boundaries
        chunks = self._sentence_aware_chunking(content, document_id)
        self.logger.info(f"Created {len(chunks)} chunks from content of {len(content)} characters")
        return chunks

    def _sentence_aware_chunking(self, content: str, document_id: str = None) -> List[TextChunk]:
        """
        Perform sentence-aware chunking to preserve sentence boundaries.

        Args:
            content: The text content to chunk
            document_id: Optional document ID to associate with chunks

        Returns:
            List of TextChunk objects
        """
        # Split content into sentences
        sentences = self._split_into_sentences(content)
        chunks = []
        current_chunk = ""
        current_start_pos = 0
        chunk_index = 0

        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                # Create a chunk with the current content
                chunk = TextChunk(
                    document_id=document_id or "",
                    content=current_chunk.strip(),
                    chunk_index=chunk_index,
                    start_pos=current_start_pos,
                    end_pos=current_start_pos + len(current_chunk)
                )
                chunks.append(chunk)

                # Start a new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + sentence
                current_start_pos = current_start_pos + len(overlap_text)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                current_chunk += sentence

        # Add the final chunk if there's any content left
        if current_chunk.strip():
            chunk = TextChunk(
                document_id=document_id or "",
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                start_pos=current_start_pos,
                end_pos=current_start_pos + len(current_chunk)
            )
            chunks.append(chunk)

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.

        Args:
            text: The text to split into sentences

        Returns:
            List of sentences
        """
        # Pattern to match sentence endings: . ! ? followed by whitespace or end of string
        sentence_pattern = r'[.!?]+\s+|[\n\r]+|(?<=[.!?])\Z'
        sentences = re.split(sentence_pattern, text)

        # Reattach sentence endings and filter out empty strings
        result = []
        parts = re.split(f'({sentence_pattern})', text)

        # Combine sentence parts with their endings
        current_sentence = ""
        for i, part in enumerate(parts):
            current_sentence += part
            # If this part matches the sentence ending pattern, save the sentence
            if re.match(sentence_pattern, part) or i == len(parts) - 1:
                if current_sentence.strip():
                    result.append(current_sentence)
                current_sentence = ""

        # If there's any remaining text, add it as a sentence
        if current_sentence.strip():
            result.append(current_sentence)

        return [s for s in result if s.strip()]

    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """
        Get the ending portion of text for overlap.

        Args:
            text: The text to get overlap from
            overlap_size: The size of overlap needed

        Returns:
            Overlap text
        """
        if len(text) <= overlap_size:
            return text
        # Start from the end and look for a good break point (space or sentence boundary)
        overlap_text = text[-overlap_size:]
        space_idx = overlap_text.find(' ')
        if space_idx != -1:
            return overlap_text[space_idx:]
        return overlap_text

    def chunk_by_paragraph(self, content: str, document_id: str = None) -> List[TextChunk]:
        """
        Chunk text by paragraphs.

        Args:
            content: The text content to chunk
            document_id: Optional document ID to associate with chunks

        Returns:
            List of TextChunk objects
        """
        paragraphs = content.split('\n\n')
        chunks = []
        chunk_index = 0
        current_pos = 0

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            # If paragraph is too long, split it further
            if len(paragraph) > self.chunk_size:
                sub_chunks = self._sentence_aware_chunking(paragraph, document_id)
                for sub_chunk in sub_chunks:
                    sub_chunk.chunk_index = chunk_index
                    sub_chunk.start_pos = current_pos
                    current_pos += len(sub_chunk.content)
                    sub_chunk.end_pos = current_pos
                    chunks.append(sub_chunk)
                    chunk_index += 1
            else:
                chunk = TextChunk(
                    document_id=document_id or "",
                    content=paragraph.strip(),
                    chunk_index=chunk_index,
                    start_pos=current_pos,
                    end_pos=current_pos + len(paragraph)
                )
                current_pos += len(paragraph) + 2  # +2 for the \n\n
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def validate_chunk_size(self, chunk: TextChunk) -> bool:
        """
        Validate that a chunk meets size requirements.

        Args:
            chunk: The chunk to validate

        Returns:
            True if valid, False otherwise
        """
        # For now, just check that the chunk has content
        return bool(chunk.content.strip())