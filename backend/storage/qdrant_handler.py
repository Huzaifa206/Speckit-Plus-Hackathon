"""
Qdrant storage handler for the Book Content Embeddings Backend.

Handles storage and retrieval of embeddings in Qdrant vector database.
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import uuid
from models.entities import EmbeddingRecord
from utils.logger import get_logger
from utils.exceptions import StorageError, QdrantError
from services.base_service import StorageService


class QdrantHandler(StorageService):
    """Handles storage and retrieval of embeddings in Qdrant."""

    def __init__(self, url: str, api_key: str, collection_name: str = "book_embeddings"):
        """
        Initialize the QdrantHandler.

        Args:
            url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Name of the collection to store embeddings
        """
        super().__init__()
        self.client = QdrantClient(url=url, api_key=api_key, prefer_grpc=False)
        self.collection_name = collection_name

    def _execute(self, embeddings: List[EmbeddingRecord], metadata: Dict[str, Any] = None) -> int:
        """
        Execute the storage process.

        Args:
            embeddings: List of EmbeddingRecord objects to store
            metadata: Optional metadata to associate with the storage operation

        Returns:
            Number of embeddings stored
        """
        return self.store_embeddings(embeddings)

    def create_collection(self, vector_size: int = 1024, distance: str = "Cosine") -> bool:
        """
        Create a collection in Qdrant with specified parameters.

        Args:
            vector_size: Size of the vectors to be stored
            distance: Distance function to use for similarity search

        Returns:
            True if collection was created or already exists
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with specified vector size and distance function
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance[distance.upper()]
                    )
                )
                self.logger.info(f"Created collection '{self.collection_name}' with {vector_size} dimensions")
            else:
                self.logger.info(f"Collection '{self.collection_name}' already exists")

            return True

        except Exception as e:
            raise QdrantError(
                f"Failed to create collection '{self.collection_name}': {str(e)}",
                collection_name=self.collection_name,
                operation="create_collection",
                error_details={"error": str(e)}
            )

    def store_embeddings(self, embeddings: List[EmbeddingRecord]) -> int:
        """
        Store embeddings in Qdrant collection.

        Args:
            embeddings: List of EmbeddingRecord objects to store

        Returns:
            Number of embeddings successfully stored
        """
        if not embeddings:
            self.logger.info("No embeddings to store")
            return 0

        # Create collection if it doesn't exist
        vector_size = len(embeddings[0].vector) if embeddings else 1024
        self.create_collection(vector_size=vector_size)

        try:
            # Prepare points for insertion
            points = []
            for embedding in embeddings:
                point = models.PointStruct(
                    id=str(uuid.uuid4()),  # Generate a unique ID for each point
                    vector=embedding.vector,
                    payload={
                        "content": embedding.content,
                        "document_url": embedding.document_url,
                        "document_title": embedding.document_title,
                        "chunk_id": embedding.chunk_id,
                        "chunk_index": embedding.chunk_index,
                        "created_at": embedding.created_at.isoformat() if embedding.created_at else None,
                        "similarity_score": embedding.similarity_score
                    }
                )
                points.append(point)

            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            self.logger.info(f"Successfully stored {len(points)} embeddings in collection '{self.collection_name}'")
            return len(points)

        except Exception as e:
            raise QdrantError(
                f"Failed to store embeddings in collection '{self.collection_name}': {str(e)}",
                collection_name=self.collection_name,
                operation="store_embeddings",
                error_details={"error": str(e), "embeddings_count": len(embeddings)}
            )

    def search_embeddings(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in Qdrant.

        Args:
            query_vector: The vector to search for similar embeddings
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing similar embeddings and their metadata
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "document_url": result.payload.get("document_url", ""),
                    "document_title": result.payload.get("document_title", ""),
                    "chunk_id": result.payload.get("chunk_id", ""),
                    "chunk_index": result.payload.get("chunk_index"),
                    "created_at": result.payload.get("created_at")
                }
                formatted_results.append(formatted_result)

            self.logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            raise QdrantError(
                f"Failed to search embeddings in collection '{self.collection_name}': {str(e)}",
                collection_name=self.collection_name,
                operation="search_embeddings",
                error_details={"error": str(e)}
            )

    def get_embedding_by_id(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific embedding by its ID.

        Args:
            embedding_id: The ID of the embedding to retrieve

        Returns:
            Dictionary containing the embedding and its metadata, or None if not found
        """
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[embedding_id]
            )

            if records:
                record = records[0]
                return {
                    "id": record.id,
                    "vector": record.vector,
                    "content": record.payload.get("content", ""),
                    "document_url": record.payload.get("document_url", ""),
                    "document_title": record.payload.get("document_title", ""),
                    "chunk_id": record.payload.get("chunk_id", ""),
                    "chunk_index": record.payload.get("chunk_index"),
                    "created_at": record.payload.get("created_at")
                }
            else:
                return None

        except Exception as e:
            raise QdrantError(
                f"Failed to retrieve embedding with ID '{embedding_id}': {str(e)}",
                collection_name=self.collection_name,
                operation="get_embedding_by_id",
                error_details={"error": str(e), "embedding_id": embedding_id}
            )

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary containing collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.distance,
                "point_count": collection_info.points_count,
                "indexed_point_count": collection_info.indexed_vectors_count
            }
        except Exception as e:
            raise QdrantError(
                f"Failed to get collection info for '{self.collection_name}': {str(e)}",
                collection_name=self.collection_name,
                operation="get_collection_info",
                error_details={"error": str(e)}
            )

    def delete_collection(self) -> bool:
        """
        Delete the collection.

        Returns:
            True if collection was deleted successfully
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            raise QdrantError(
                f"Failed to delete collection '{self.collection_name}': {str(e)}",
                collection_name=self.collection_name,
                operation="delete_collection",
                error_details={"error": str(e)}
            )